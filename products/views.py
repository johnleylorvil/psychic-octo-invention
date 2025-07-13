# ======================================
# apps/products/views.py
# ======================================

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db.models import Q, Count, Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Category, Product, Review
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ReviewSerializer, CreateReviewSerializer
)
from .filters import ProductFilter


class CategoryListView(generics.ListAPIView):
    """
    Liste des catégories actives
    GET /api/v1/products/categories/
    """
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        cache_key = 'categories_list'
        categories = cache.get(cache_key)
        
        if categories is None:
            categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
            cache.set(cache_key, categories, 3600)  # 1 heure
        
        return categories


class CategoryDetailView(generics.RetrieveAPIView):
    """
    Détail d'une catégorie
    GET /api/v1/products/categories/{slug}/
    """
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class ProductListView(generics.ListAPIView):
    """
    Liste des produits avec filtres
    GET /api/v1/products/
    """
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'tags', 'brand']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category', 'seller')


class ProductDetailView(generics.RetrieveAPIView):
    """
    Détail d'un produit
    GET /api/v1/products/{slug}/
    """
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category', 'seller')


@api_view(['GET'])
@permission_classes([AllowAny])
def featured_products(request):
    """
    Produits vedettes
    GET /api/v1/products/featured/
    """
    cache_key = 'featured_products'
    products_data = cache.get(cache_key)
    
    if products_data is None:
        products = Product.objects.filter(
            is_active=True, 
            is_featured=True
        ).select_related('category')[:8]
        
        serializer = ProductListSerializer(products, many=True)
        products_data = serializer.data
        cache.set(cache_key, products_data, 1800)  # 30 minutes
    
    return Response({
        'success': True,
        'data': products_data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def category_products(request, slug):
    """
    Produits d'une catégorie
    GET /api/v1/products/categories/{slug}/products/
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related('category')
    
    # Appliquer les filtres
    filter_set = ProductFilter(request.GET, queryset=products)
    products = filter_set.qs
    
    # Pagination simple
    page_size = 20
    page = int(request.GET.get('page', 1))
    start = (page - 1) * page_size
    end = start + page_size
    
    products_page = products[start:end]
    serializer = ProductListSerializer(products_page, many=True)
    
    return Response({
        'success': True,
        'data': {
            'category': CategorySerializer(category).data,
            'products': serializer.data,
            'total': products.count(),
            'page': page,
            'has_more': products.count() > end
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):
    """
    Recherche de produits
    GET /api/v1/products/search/?q=terme
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return Response({
            'success': False,
            'message': 'Terme de recherche requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(query) < 2:
        return Response({
            'success': False,
            'message': 'Le terme de recherche doit contenir au moins 2 caractères'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(tags__icontains=query) |
        Q(brand__icontains=query),
        is_active=True
    ).select_related('category')[:20]
    
    serializer = ProductListSerializer(products, many=True)
    
    return Response({
        'success': True,
        'data': {
            'query': query,
            'products': serializer.data,
            'count': len(serializer.data)
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def product_reviews(request, product_id):
    """
    Avis d'un produit
    GET /api/v1/products/{product_id}/reviews/
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    reviews = Review.objects.filter(
        product=product,
        is_approved=True
    ).order_by('-created_at')
    
    # Stats des avis
    rating_stats = reviews.aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    # Distribution des notes
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()
    
    serializer = ReviewSerializer(reviews, many=True)
    
    return Response({
        'success': True,
        'data': {
            'reviews': serializer.data,
            'stats': {
                'average_rating': round(rating_stats['avg_rating'], 1) if rating_stats['avg_rating'] else 0,
                'total_reviews': rating_stats['total_reviews'],
                'rating_distribution': rating_distribution
            }
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, product_id):
    """
    Créer un avis produit
    POST /api/v1/products/{product_id}/reviews/
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Vérifier si l'utilisateur a déjà laissé un avis
    existing_review = Review.objects.filter(
        product=product,
        user=request.user
    ).first()
    
    if existing_review:
        return Response({
            'success': False,
            'message': 'Vous avez déjà laissé un avis pour ce produit.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = CreateReviewSerializer(data=request.data)
    
    if serializer.is_valid():
        # Vérifier si c'est un achat vérifié
        from orders.models import OrderItem
        is_verified_purchase = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__payment_status='paid'
        ).exists()
        
        review = serializer.save(
            product=product,
            user=request.user,
            customer_name=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            customer_email=request.user.email,
            is_verified_purchase=is_verified_purchase,
            is_approved=False  # Modération requise
        )
        
        return Response({
            'success': True,
            'message': 'Votre avis a été soumis et sera publié après modération.',
            'data': ReviewSerializer(review).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
