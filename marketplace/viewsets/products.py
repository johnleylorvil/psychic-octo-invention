# marketplace/viewsets/products.py

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Prefetch, Count, Avg, F
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings

from marketplace.models import Product, Category, ProductImage, User
from marketplace.serializers.products import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductFeaturedSerializer,
    ProductSearchSerializer,
    CategoryListSerializer,
    CategoryDetailSerializer,
    ProductImageSerializer
)
from marketplace.utils.pagination import StandardResultsSetPagination


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour la gestion des produits
    
    Actions disponibles:
    - list: Liste des produits avec pagination et filtres
    - retrieve: Détail d'un produit par slug
    - featured: Produits vedettes pour landing page
    - search: Recherche full-text
    - images: Images d'un produit
    - reserve_stock: Réserver stock temporairement
    - check_stock: Vérifier disponibilité
    """
    
    queryset = Product.objects.select_related('category', 'seller').prefetch_related(
        Prefetch('images', queryset=ProductImage.objects.order_by('sort_order', 'id'))
    ).filter(is_active=True)
    
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtres disponibles
    filterset_fields = {
        'category': ['exact'],
        'category__slug': ['exact'],
        'price': ['gte', 'lte'],
        'is_featured': ['exact'],
        'brand': ['exact', 'icontains'],
        'origin_country': ['exact'],
        'condition_type': ['exact'],
        'requires_shipping': ['exact'],
        'is_digital': ['exact'],
    }
    
    # Recherche full-text
    search_fields = ['name', 'description', 'short_description', 'tags', 'brand']
    
    # Options de tri
    ordering_fields = ['price', 'created_at', 'name', 'stock_quantity']
    ordering = ['-created_at']
    
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """Retourne le serializer approprié selon l'action"""
        if self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action == 'featured':
            return ProductFeaturedSerializer
        elif self.action == 'search':
            return ProductSearchSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        """Optimise les requêtes selon l'action"""
        queryset = super().get_queryset()
        
        if self.action == 'retrieve':
            # Pour le détail, on charge tout y compris les reviews avec moyennes
            queryset = queryset.annotate(
                reviews_count=Count('reviews'),
                average_rating=Avg('reviews__rating')
            )
        elif self.action == 'featured':
            # Pour les produits vedettes
           queryset = queryset.filter(is_featured=True).order_by('-created_at')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        GET /api/products/featured/
        Retourne les produits vedettes pour la landing page
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Limite à 6 produits vedettes par défaut
        limit = int(request.query_params.get('limit', 6))
        queryset = queryset[:limit]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        GET /api/products/search/?q=terme
        Recherche avancée de produits
        """
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response({
                'results': [],
                'count': 0,
                'message': 'Paramètre de recherche "q" requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Recherche multi-critères
        queryset = self.get_queryset().filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(tags__icontains=query) |
            Q(brand__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'search_query': query})
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True, context={'search_query': query})
        return Response({
            'results': serializer.data,
            'count': queryset.count(),
            'query': query
        })
    
    @action(detail=True, methods=['get'])
    def images(self, request, slug=None):
        """
        GET /api/products/{slug}/images/
        Retourne toutes les images d'un produit
        """
        product = get_object_or_404(Product, slug=slug, is_active=True)
        images = ProductImage.objects.filter(product=product).order_by('sort_order', 'id')
        
        serializer = ProductImageSerializer(images, many=True)
        return Response({
            'product': product.name,
            'images': serializer.data,
            'count': images.count()
        })
    
    @action(detail=True, methods=['post'])
    def reserve_stock(self, request, slug=None):
        """
        POST /api/products/{slug}/reserve_stock/
        Réserve temporairement du stock (panier)
        """
        product = get_object_or_404(Product, slug=slug, is_active=True)
        quantity = int(request.data.get('quantity', 1))
        
        if quantity <= 0:
            return Response({
                'error': 'Quantité doit être positive'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 🎯 GESTION RACE CONDITIONS SIMPLE
        with transaction.atomic():
            # Recharge le produit avec lock pour éviter race conditions
            product = Product.objects.select_for_update().get(id=product.id)
            
            # Vérifie stock disponible
            if product.is_digital:
                return Response({
                    'success': True,
                    'message': 'Produit numérique - Stock illimité',
                    'reserved_quantity': quantity
                })
            
            if not product.stock_quantity or product.stock_quantity < quantity:
                return Response({
                    'error': f'Stock insuffisant. Disponible: {product.stock_quantity or 0}',
                    'available_stock': product.stock_quantity or 0
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 🎯 RÉSERVATION TEMPORAIRE SIMPLE
            # Pour MVP: on décrémente directement, sera libéré si panier abandonné
            product.stock_quantity = F('stock_quantity') - quantity
            product.save(update_fields=['stock_quantity'])
            
            # Recharge pour avoir la vraie valeur
            product.refresh_from_db()
            
            # 🎯 ALERTE STOCK BAS AUTOMATIQUE
            self._check_low_stock_alert(product)
            
            return Response({
                'success': True,
                'message': 'Stock réservé avec succès',
                'reserved_quantity': quantity,
                'remaining_stock': product.stock_quantity
            })
    
    @action(detail=True, methods=['post'])
    def release_stock(self, request, slug=None):
        """
        POST /api/products/{slug}/release_stock/
        Libère du stock réservé (abandon panier)
        """
        product = get_object_or_404(Product, slug=slug, is_active=True)
        quantity = int(request.data.get('quantity', 1))
        
        if product.is_digital:
            return Response({'success': True, 'message': 'Produit numérique'})
        
        # 🎯 LIBÉRATION STOCK SIMPLE
        with transaction.atomic():
            product = Product.objects.select_for_update().get(id=product.id)
            product.stock_quantity = F('stock_quantity') + quantity
            product.save(update_fields=['stock_quantity'])
            product.refresh_from_db()
            
            return Response({
                'success': True,
                'message': 'Stock libéré',
                'released_quantity': quantity,
                'current_stock': product.stock_quantity
            })
    
    @action(detail=True, methods=['post'])
    def confirm_purchase(self, request, slug=None):
        """
        POST /api/products/{slug}/confirm_purchase/
        Confirme l'achat définitif (commande payée)
        """
        product = get_object_or_404(Product, slug=slug, is_active=True)
        quantity = int(request.data.get('quantity', 1))
        order_number = request.data.get('order_number', '')
        
        if product.is_digital:
            return Response({
                'success': True,
                'message': 'Produit numérique - Pas de stock à décrémenter'
            })
        
        # 🎯 DÉCRÉMENTATION DÉFINITIVE LORS COMMANDE CONFIRMÉE
        with transaction.atomic():
            product = Product.objects.select_for_update().get(id=product.id)
            
            # Stock déjà réservé, on confirme juste la vente
            # (Dans un système plus complexe, on gérerait un stock "réservé" séparé)
            
            # 🎯 HISTORIQUE MOUVEMENT STOCK SIMPLE
            self._log_stock_movement(product, -quantity, 'sale', order_number)
            
            return Response({
                'success': True,
                'message': 'Achat confirmé',
                'sold_quantity': quantity,
                'current_stock': product.stock_quantity
            })
    
    @action(detail=True, methods=['get'])
    def check_stock(self, request, slug=None):
        """
        GET /api/products/{slug}/check_stock/
        Vérifie la disponibilité en temps réel
        """
        product = get_object_or_404(Product, slug=slug, is_active=True)
        quantity = int(request.query_params.get('quantity', 1))
        
        if product.is_digital:
            return Response({
                'available': True,
                'message': 'Produit numérique - Toujours disponible',
                'requested_quantity': quantity,
                'stock_type': 'digital'
            })
        
        available = product.stock_quantity and product.stock_quantity >= quantity
        
        return Response({
            'available': available,
            'requested_quantity': quantity,
            'current_stock': product.stock_quantity or 0,
            'message': 'Disponible' if available else 'Stock insuffisant',
            'stock_type': 'physical'
        })
    
    def _check_low_stock_alert(self, product):
        """🎯 ALERTE STOCK BAS AUTOMATIQUE - SIMPLE"""
        if (product.stock_quantity is not None and 
            product.stock_quantity <= (product.min_stock_alert or 5)):
            
            try:
                # Envoie email au superadmin
                superadmins = User.objects.filter(is_superuser=True, is_active=True)
                admin_emails = [admin.email for admin in superadmins if admin.email]
                
                if admin_emails:
                    send_mail(
                        subject=f'🚨 Stock Bas - {product.name}',
                        message=f'''
                        ALERTE STOCK BAS
                        
                        Produit: {product.name}
                        Stock actuel: {product.stock_quantity}
                        Seuil d'alerte: {product.min_stock_alert or 5}
                        Catégorie: {product.category.name}
                        
                        Action requise: Réapprovisionner le stock
                        
                        Lien admin: {settings.SITE_URL}/admin/marketplace/product/{product.id}/
                        ''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=admin_emails,
                        fail_silently=True
                    )
            except Exception:
                # Silent fail pour ne pas bloquer l'achat
                pass
    
    def _log_stock_movement(self, product, quantity_change, movement_type, reference=''):
        """🎯 HISTORIQUE MOUVEMENT STOCK - SIMPLE LOG"""
        try:
            # Pour MVP: log simple dans les notes admin du produit
            movement_log = f"[{movement_type.upper()}] {quantity_change:+d} unités"
            if reference:
                movement_log += f" (Réf: {reference})"
            
            # Ajoute au début des notes admin existantes
            current_notes = getattr(product, 'admin_notes', '') or ''
            new_notes = f"{movement_log}\n{current_notes}"
            
            # Limite à 1000 caractères pour éviter l'inflation
            if len(new_notes) > 1000:
                new_notes = new_notes[:1000] + "..."
            
            Product.objects.filter(id=product.id).update(admin_notes=new_notes)
            
        except Exception:
            # Silent fail pour ne pas bloquer l'achat
            pass


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour la gestion des catégories
    
    Actions disponibles:
    - list: Liste des catégories actives
    - retrieve: Détail d'une catégorie par slug
    - products: Produits d'une catégorie
    - featured: Catégories vedettes pour header
    - tree: Arbre hiérarchique complet
    """
    
    queryset = Category.objects.filter(is_active=True).prefetch_related(
        'products'
    ).order_by('sort_order', 'name')
    
    serializer_class = CategoryListSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """Retourne le serializer approprié selon l'action"""
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategoryListSerializer
    
    def get_queryset(self):
        """Optimise les requêtes selon l'action"""
        queryset = super().get_queryset()
        
        if self.action == 'list':
            # Pour la liste, on peut filtrer par parent
            parent_id = self.request.query_params.get('parent')
            if parent_id:
                queryset = queryset.filter(parent_id=parent_id)
            elif parent_id == '':  # Catégories racines
                queryset = queryset.filter(parent__isnull=True)
        
        elif self.action == 'retrieve':
            # Pour le détail, on compte les produits
            queryset = queryset.annotate(
                products_count=Count('products', filter=Q(products__is_active=True))
            )
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """
        GET /api/categories/{slug}/products/
        Retourne les produits d'une catégorie avec pagination
        """
        category = get_object_or_404(Category, slug=slug, is_active=True)
        
        # Récupère les produits de cette catégorie
        products = Product.objects.select_related('category', 'seller').prefetch_related(
            'images'
        ).filter(
            category=category,
            is_active=True
        ).order_by('-created_at')
        
        # Applique les filtres de prix si fournis
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        
        # Pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(products, request)
        
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response({
            'category': CategoryDetailSerializer(category).data,
            'products': serializer.data,
            'count': products.count()
        })
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        GET /api/categories/featured/
        Retourne les catégories vedettes pour header navigation
        """
        queryset = self.get_queryset().filter(is_featured=True)
        
        # Limite à 3 catégories vedettes par défaut pour header
        limit = int(request.query_params.get('limit', 3))
        queryset = queryset[:limit]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        GET /api/categories/tree/
        Retourne l'arbre hiérarchique des catégories
        """
        # Catégories racines avec leurs enfants
        root_categories = self.get_queryset().filter(parent__isnull=True)
        
        def build_tree(categories):
            tree = []
            for category in categories:
                children = Category.objects.filter(parent=category, is_active=True)
                category_data = CategoryListSerializer(category, context={'include_children': True}).data
                if children.exists():
                    category_data['children'] = build_tree(children)
                else:
                    category_data['children'] = []
                tree.append(category_data)
            return tree
        
        tree = build_tree(root_categories)
        
        return Response({
            'tree': tree,
            'count': len(tree)
        })