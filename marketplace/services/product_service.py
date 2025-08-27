# marketplace/services/product_service.py
"""
Product service for business logic related to products and categories
"""

from django.db.models import Q, Avg, Count, F
from django.core.cache import cache
from django.utils import timezone
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ProductService:
    """Service for product-related business logic"""
    
    @staticmethod
    def get_featured_products(limit: int = 8, category=None) -> List:
        """Get featured products for homepage or category"""
        from ..models import Product
        
        cache_key = f"featured_products_{category.slug if category else 'all'}_{limit}"
        cached_products = cache.get(cache_key)
        
        if cached_products is None:
            queryset = Product.objects.featured().select_related('category', 'seller')
            
            if category:
                queryset = queryset.filter(category=category)
            
            cached_products = list(queryset[:limit])
            # Cache for 30 minutes
            cache.set(cache_key, cached_products, 1800)
        
        return cached_products
    
    @staticmethod
    def search_products(query: str, category=None, filters: Dict[str, Any] = None) -> Dict:
        """Advanced product search with filters"""
        from ..models import Product
        
        if not query and not filters:
            return {
                'products': Product.objects.none(),
                'total_count': 0,
                'facets': {}
            }
        
        # Start with available products
        queryset = Product.objects.available().select_related('category', 'seller')
        
        # Apply text search
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(tags__icontains=query) |
                Q(brand__icontains=query) |
                Q(category__name__icontains=query)
            ).distinct()
        
        # Apply category filter
        if category:
            queryset = queryset.filter(category=category)
        
        # Apply additional filters
        if filters:
            queryset = ProductService._apply_filters(queryset, filters)
        
        # Get facets for filtering UI
        facets = ProductService._get_search_facets(queryset)
        
        return {
            'products': queryset,
            'total_count': queryset.count(),
            'facets': facets
        }
    
    @staticmethod
    def get_related_products(product, limit: int = 4) -> List:
        """Get products related to given product"""
        from ..models import Product
        
        cache_key = f"related_products_{product.id}_{limit}"
        cached_products = cache.get(cache_key)
        
        if cached_products is None:
            # Get products from same category, excluding current product
            related_products = Product.objects.available().filter(
                category=product.category
            ).exclude(
                id=product.id
            ).select_related('category', 'seller')[:limit]
            
            cached_products = list(related_products)
            # Cache for 1 hour
            cache.set(cache_key, cached_products, 3600)
        
        return cached_products
    
    @staticmethod
    def get_trending_products(limit: int = 10, days: int = 7) -> List:
        """Get trending products based on recent orders"""
        from ..models import Product, OrderItem
        
        cache_key = f"trending_products_{limit}_{days}"
        cached_products = cache.get(cache_key)
        
        if cached_products is None:
            # Calculate trending products based on recent order volume
            cutoff_date = timezone.now() - timezone.timedelta(days=days)
            
            trending_ids = OrderItem.objects.filter(
                order__created_at__gte=cutoff_date,
                order__status__in=['confirmed', 'processing', 'shipped', 'delivered']
            ).values('product_id').annotate(
                order_count=Count('id')
            ).order_by('-order_count').values_list('product_id', flat=True)[:limit]
            
            # Get products in the same order as trending_ids
            products = Product.objects.filter(
                id__in=trending_ids,
                is_active=True
            ).select_related('category', 'seller')
            
            # Preserve order
            product_dict = {p.id: p for p in products}
            cached_products = [product_dict[pid] for pid in trending_ids if pid in product_dict]
            
            # Cache for 2 hours
            cache.set(cache_key, cached_products, 7200)
        
        return cached_products
    
    @staticmethod
    def get_product_recommendations(user, limit: int = 8) -> List:
        """Get personalized product recommendations for user"""
        from ..models import Product, Order
        
        if not user or not user.is_authenticated:
            # Return featured products for anonymous users
            return ProductService.get_featured_products(limit)
        
        cache_key = f"product_recommendations_{user.id}_{limit}"
        cached_products = cache.get(cache_key)
        
        if cached_products is None:
            # Get user's purchase history
            user_categories = Order.objects.filter(
                user=user,
                status__in=['delivered', 'shipped']
            ).values_list('items__product__category', flat=True).distinct()
            
            if user_categories:
                # Recommend products from categories user has purchased from
                recommended_products = Product.objects.available().filter(
                    category__in=user_categories
                ).exclude(
                    # Exclude products user already bought
                    id__in=Order.objects.filter(user=user).values_list('items__product_id', flat=True)
                ).select_related('category', 'seller').order_by('-created_at')[:limit]
                
                cached_products = list(recommended_products)
            else:
                # New user - return featured products
                cached_products = ProductService.get_featured_products(limit)
            
            # Cache for 1 hour
            cache.set(cache_key, cached_products, 3600)
        
        return cached_products
    
    @staticmethod
    def update_product_stock(product, quantity_change: int) -> bool:
        """Update product stock with validation"""
        try:
            if product.stock_quantity is None:
                product.stock_quantity = 0
            
            new_quantity = product.stock_quantity + quantity_change
            
            if new_quantity < 0:
                logger.warning(f"Attempted to set negative stock for product {product.id}")
                return False
            
            product.stock_quantity = new_quantity
            product.save(update_fields=['stock_quantity', 'updated_at'])
            
            # Clear related caches
            cache.delete_many([
                f"product_detail_{product.id}",
                f"featured_products_{product.category.slug}",
                f"category_products_{product.category.slug}",
            ])
            
            return True
        except Exception as e:
            logger.error(f"Error updating stock for product {product.id}: {e}")
            return False
    
    @staticmethod
    def calculate_product_rating(product) -> Dict[str, Any]:
        """Calculate comprehensive product rating statistics"""
        from ..models import Review
        
        cache_key = f"product_rating_{product.id}"
        cached_rating = cache.get(cache_key)
        
        if cached_rating is None:
            reviews = Review.objects.approved().filter(product=product)
            
            if reviews.exists():
                rating_stats = reviews.aggregate(
                    average=Avg('rating'),
                    total_count=Count('id')
                )
                
                # Get rating distribution
                rating_distribution = {}
                for i in range(1, 6):
                    rating_distribution[i] = reviews.filter(rating=i).count()
                
                cached_rating = {
                    'average': round(rating_stats['average'], 1) if rating_stats['average'] else 0,
                    'total_count': rating_stats['total_count'],
                    'distribution': rating_distribution,
                    'percentage_positive': round(
                        (reviews.filter(rating__gte=4).count() / rating_stats['total_count']) * 100, 1
                    ) if rating_stats['total_count'] > 0 else 0
                }
            else:
                cached_rating = {
                    'average': 0,
                    'total_count': 0,
                    'distribution': {i: 0 for i in range(1, 6)},
                    'percentage_positive': 0
                }
            
            # Cache for 30 minutes
            cache.set(cache_key, cached_rating, 1800)
        
        return cached_rating
    
    @staticmethod
    def _apply_filters(queryset, filters: Dict[str, Any]):
        """Apply search filters to queryset"""
        if 'price_min' in filters and filters['price_min']:
            queryset = queryset.filter(
                Q(promotional_price__gte=filters['price_min']) |
                (Q(promotional_price__isnull=True) & Q(price__gte=filters['price_min']))
            )
        
        if 'price_max' in filters and filters['price_max']:
            queryset = queryset.filter(
                Q(promotional_price__lte=filters['price_max']) |
                (Q(promotional_price__isnull=True) & Q(price__lte=filters['price_max']))
            )
        
        if 'brand' in filters and filters['brand']:
            queryset = queryset.filter(brand__in=filters['brand'])
        
        if 'condition' in filters and filters['condition']:
            queryset = queryset.filter(condition_type__in=filters['condition'])
        
        if 'in_stock' in filters and filters['in_stock']:
            queryset = queryset.filter(stock_quantity__gt=0)
        
        if 'on_sale' in filters and filters['on_sale']:
            queryset = queryset.filter(promotional_price__isnull=False)
        
        return queryset
    
    @staticmethod
    def _get_search_facets(queryset) -> Dict[str, Any]:
        """Get search facets for filtering UI"""
        # Get price range
        price_stats = queryset.aggregate(
            min_price=models.Min(
                Case(
                    When(promotional_price__isnull=False, then=F('promotional_price')),
                    default=F('price')
                )
            ),
            max_price=models.Max(
                Case(
                    When(promotional_price__isnull=False, then=F('promotional_price')),
                    default=F('price')
                )
            )
        )
        
        # Get available brands
        brands = queryset.exclude(
            brand__isnull=True
        ).exclude(
            brand__exact=''
        ).values_list('brand', flat=True).distinct()
        
        # Get categories
        categories = queryset.values('category__id', 'category__name').distinct()
        
        return {
            'price_range': {
                'min': float(price_stats['min_price'] or 0),
                'max': float(price_stats['max_price'] or 0)
            },
            'brands': list(brands),
            'categories': list(categories),
            'total_count': queryset.count()
        }