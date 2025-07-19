# marketplace/serializers/products.py

from rest_framework import serializers
from decimal import Decimal
from django.db.models import F
from marketplace.models import Product, Category, ProductImage, User


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer pour les images de produits"""
    
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image_url', 'image_path', 'alt_text', 'title',
            'is_primary', 'sort_order', 'image_type'
        ]


class CategoryListSerializer(serializers.ModelSerializer):
    """Serializer simple pour liste des catégories"""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'icon',
            'is_featured', 'sort_order', 'products_count'
        ]
    
    def get_products_count(self, obj):
        """Compte les produits actifs de cette catégorie"""
        if hasattr(obj, 'products_count'):
            return obj.products_count
        return obj.products.filter(is_active=True).count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une catégorie"""
    products_count = serializers.IntegerField(read_only=True)
    parent = CategoryListSerializer(read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'detailed_description',
            'banner_image', 'banner_image_path', 'icon', 'is_featured',
            'sort_order', 'meta_title', 'meta_description', 'parent',
            'children', 'products_count', 'created_at'
        ]
    
    def get_children(self, obj):
        """Retourne les sous-catégories si demandées"""
        include_children = self.context.get('include_children', False)
        if not include_children:
            return []
        
        children = Category.objects.filter(parent=obj, is_active=True)
        return CategoryListSerializer(children, many=True).data


class SellerBasicSerializer(serializers.ModelSerializer):
    """Serializer basique pour le vendeur"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        """Nom complet du vendeur"""
        return f"{obj.first_name} {obj.last_name}".strip()


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer pour liste des produits (optimisé performance)"""
    category = CategoryListSerializer(read_only=True)
    seller = SellerBasicSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    original_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    is_on_sale = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'price',
            'promotional_price', 'original_price', 'final_price', 
            'discount_percentage', 'is_on_sale', 'stock_quantity',
            'is_in_stock', 'stock_status', 'is_featured', 'category', 
            'seller', 'primary_image', 'brand', 'origin_country', 
            'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Retourne l'image principale du produit"""
        primary_image = None
        
        # Cherche d'abord une image marquée comme principale
        if hasattr(obj, 'images'):
            for image in obj.images.all():
                if image.is_primary:
                    primary_image = image
                    break
            
            # Sinon prend la première image disponible
            if not primary_image and obj.images.exists():
                primary_image = obj.images.first()
        
        if primary_image:
            return {
                'id': primary_image.id,
                'url': primary_image.image_url,
                'alt': primary_image.alt_text or obj.name,
                'title': primary_image.title or obj.name
            }
        return None
    
    def get_original_price(self, obj):
        """Prix original du produit"""
        return obj.price
    
    def get_final_price(self, obj):
        """Retourne le prix final (promotionnel si disponible)"""
        if obj.promotional_price and obj.promotional_price > 0:
            return obj.promotional_price
        return obj.price
    
    def get_discount_percentage(self, obj):
        """Calcule le pourcentage de réduction"""
        if not obj.promotional_price or obj.promotional_price >= obj.price:
            return 0
        
        discount = ((obj.price - obj.promotional_price) / obj.price) * 100
        return round(discount, 1)
    
    def get_is_on_sale(self, obj):
        """Vérifie si le produit est en promotion"""
        return (obj.promotional_price and 
                obj.promotional_price > 0 and 
                obj.promotional_price < obj.price)
    
    def get_is_in_stock(self, obj):
        """Vérifie si le produit est en stock"""
        if obj.is_digital:
            return True
        return obj.stock_quantity and obj.stock_quantity > 0
    
    def get_stock_status(self, obj):
        """Retourne le statut du stock avec message"""
        if obj.is_digital:
            return {'status': 'digital', 'message': 'Produit numérique'}
        
        if not obj.stock_quantity or obj.stock_quantity <= 0:
            return {'status': 'out_of_stock', 'message': 'Rupture de stock'}
        elif obj.stock_quantity <= (obj.min_stock_alert or 5):
            return {'status': 'low_stock', 'message': f'Plus que {obj.stock_quantity} en stock'}
        else:
            return {'status': 'in_stock', 'message': 'En stock'}


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un produit"""
    category = CategoryDetailSerializer(read_only=True)
    seller = SellerBasicSerializer(read_only=True)
    images = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    original_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    is_on_sale = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    reviews_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    related_products = serializers.SerializerMethodField()
    shipping_info = serializers.SerializerMethodField()
    specifications_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'description',
            'detailed_description', 'specifications', 'specifications_formatted',
            'category', 'seller', 'price', 'promotional_price', 'original_price',
            'final_price', 'discount_percentage', 'is_on_sale', 'stock_quantity',
            'is_in_stock', 'stock_status', 'sku', 'is_featured', 'is_digital',
            'requires_shipping', 'shipping_info', 'weight', 'dimensions',
            'tags', 'video_url', 'warranty_period', 'brand', 'model',
            'color', 'material', 'origin_country', 'condition_type',
            'meta_title', 'meta_description', 'images', 'reviews_count',
            'average_rating', 'related_products', 'created_at', 'updated_at'
        ]
    
    def get_images(self, obj):
        """Retourne toutes les images du produit triées"""
        if hasattr(obj, 'images'):
            images = obj.images.all().order_by('sort_order', 'id')
            return ProductImageSerializer(images, many=True).data
        return []
    
    def get_original_price(self, obj):
        """Prix original du produit"""
        return obj.price
    
    def get_final_price(self, obj):
        """Retourne le prix final (promotionnel si disponible)"""
        if obj.promotional_price and obj.promotional_price > 0:
            return obj.promotional_price
        return obj.price
    
    def get_discount_percentage(self, obj):
        """Calcule le pourcentage de réduction"""
        if not obj.promotional_price or obj.promotional_price >= obj.price:
            return 0
        
        discount = ((obj.price - obj.promotional_price) / obj.price) * 100
        return round(discount, 1)
    
    def get_is_on_sale(self, obj):
        """Vérifie si le produit est en promotion"""
        return (obj.promotional_price and 
                obj.promotional_price > 0 and 
                obj.promotional_price < obj.price)
    
    def get_is_in_stock(self, obj):
        """Vérifie si le produit est en stock"""
        if obj.is_digital:
            return True
        return obj.stock_quantity and obj.stock_quantity > 0
    
    def get_stock_status(self, obj):
        """Retourne le statut du stock avec message détaillé"""
        if obj.is_digital:
            return {
                'status': 'digital', 
                'message': 'Produit numérique - Disponible immédiatement',
                'quantity': None
            }
        
        if not obj.stock_quantity or obj.stock_quantity <= 0:
            return {
                'status': 'out_of_stock', 
                'message': 'Rupture de stock',
                'quantity': 0
            }
        elif obj.stock_quantity <= (obj.min_stock_alert or 5):
            return {
                'status': 'low_stock', 
                'message': f'Stock limité - Plus que {obj.stock_quantity} disponible(s)',
                'quantity': obj.stock_quantity
            }
        else:
            return {
                'status': 'in_stock', 
                'message': 'En stock',
                'quantity': obj.stock_quantity
            }
    
    def get_shipping_info(self, obj):
        """Informations de livraison"""
        if obj.is_digital:
            return {
                'type': 'digital',
                'message': 'Livraison numérique instantanée',
                'cost': 0
            }
        elif obj.requires_shipping:
            return {
                'type': 'physical',
                'message': 'Livraison physique requise',
                'weight': obj.weight,
                'dimensions': obj.dimensions
            }
        else:
            return {
                'type': 'pickup',
                'message': 'Retrait en magasin uniquement'
            }
    
    def get_specifications_formatted(self, obj):
        """Spécifications formatées pour affichage"""
        if not obj.specifications:
            return []
        
        # Si c'est déjà un dict, on le formate
        if isinstance(obj.specifications, dict):
            return [
                {'key': key.title(), 'value': value}
                for key, value in obj.specifications.items()
            ]
        
        return []
    
    def get_related_products(self, obj):
        """Retourne des produits similaires (même catégorie)"""
        related = Product.objects.filter(
            category=obj.category,
            is_active=True
        ).exclude(id=obj.id).select_related('category').prefetch_related(
            'images'
        ).order_by('-is_featured', '-created_at')[:4]
        
        return ProductListSerializer(related, many=True, context=self.context).data


class ProductFeaturedSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour produits vedettes landing page"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    primary_image = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    original_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    is_on_sale = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'price',
            'promotional_price', 'original_price', 'final_price', 
            'discount_percentage', 'is_on_sale', 'category_name', 
            'category_slug', 'primary_image', 'brand'
        ]
    
    def get_primary_image(self, obj):
        """Retourne l'image principale optimisée pour landing"""
        primary_image = None
        
        if hasattr(obj, 'images'):
            for image in obj.images.all():
                if image.is_primary:
                    primary_image = image
                    break
            
            if not primary_image and obj.images.exists():
                primary_image = obj.images.first()
        
        if primary_image:
            return {
                'url': primary_image.image_url,
                'alt': primary_image.alt_text or obj.name
            }
        return None
    
    def get_original_price(self, obj):
        """Prix original"""
        return obj.price
    
    def get_final_price(self, obj):
        """Prix final pour affichage"""
        if obj.promotional_price and obj.promotional_price > 0:
            return obj.promotional_price
        return obj.price
    
    def get_discount_percentage(self, obj):
        """Pourcentage de réduction pour badge promo"""
        if not obj.promotional_price or obj.promotional_price >= obj.price:
            return 0
        
        discount = ((obj.price - obj.promotional_price) / obj.price) * 100
        return round(discount, 1)
    
    def get_is_on_sale(self, obj):
        """Badge promotion"""
        return (obj.promotional_price and 
                obj.promotional_price > 0 and 
                obj.promotional_price < obj.price)


class ProductSearchSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour résultats de recherche"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    match_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'final_price',
            'category_name', 'primary_image', 'brand', 'match_score'
        ]
    
    def get_primary_image(self, obj):
        """Image pour résultats recherche"""
        if hasattr(obj, 'images') and obj.images.exists():
            image = obj.images.filter(is_primary=True).first()
            if not image:
                image = obj.images.first()
            
            if image:
                return {
                    'url': image.image_url,
                    'alt': image.alt_text or obj.name
                }
        return None
    
    def get_final_price(self, obj):
        """Prix final"""
        if obj.promotional_price and obj.promotional_price > 0:
            return obj.promotional_price
        return obj.price
    
    def get_match_score(self, obj):
        """Score de pertinence pour la recherche"""
        # Dans une implémentation avancée, on pourrait calculer
        # un score basé sur la correspondance avec les termes de recherche
        query = self.context.get('search_query', '')
        if not query:
            return 0
        
        score = 0
        query_lower = query.lower()
        
        # Points pour correspondance exacte dans le nom
        if query_lower in obj.name.lower():
            score += 10
        
        # Points pour correspondance dans la description
        if obj.short_description and query_lower in obj.short_description.lower():
            score += 5
        
        # Points pour correspondance dans la marque
        if obj.brand and query_lower in obj.brand.lower():
            score += 3
        
        return score