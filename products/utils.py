# ======================================
# apps/products/utils.py (bonus - utilitaires)
# ======================================

from django.core.cache import cache
from django.db.models import Count, Avg
from .models import Product, Category


class ProductSearchService:
    """Service pour la recherche avancée de produits"""
    
    @staticmethod
    def get_search_suggestions(query, limit=5):
        """Obtenir des suggestions de recherche"""
        if len(query) < 2:
            return []
        
        cache_key = f'search_suggestions_{query.lower()}'
        suggestions = cache.get(cache_key)
        
        if suggestions is None:
            # Rechercher dans les noms de produits
            products = Product.objects.filter(
                name__icontains=query,
                is_active=True
            ).values_list('name', flat=True)[:limit]
            
            suggestions = list(products)
            cache.set(cache_key, suggestions, 300)  # 5 minutes
        
        return suggestions
    
    @staticmethod
    def get_popular_searches():
        """Obtenir les recherches populaires"""
        cache_key = 'popular_searches'
        popular = cache.get(cache_key)
        
        if popular is None:
            # Simuler des recherches populaires basées sur les produits vedettes
            popular_products = Product.objects.filter(
                is_featured=True,
                is_active=True
            ).values_list('name', flat=True)[:10]
            
            popular = list(popular_products)
            cache.set(cache_key, popular, 3600)  # 1 heure
        
        return popular


class ProductStatsService:
    """Service pour les statistiques produits"""
    
    @staticmethod
    def get_category_stats():
        """Statistiques par catégorie"""
        cache_key = 'category_stats'
        stats = cache.get(cache_key)
        
        if stats is None:
            categories = Category.objects.filter(is_active=True).annotate(
                products_count=Count('product'),
                avg_price=Avg('product__price')
            ).order_by('-products_count')
            
            stats = []
            for category in categories:
                stats.append({
                    'name': category.name,
                    'slug': category.slug,
                    'products_count': category.products_count,
                    'avg_price': float(category.avg_price) if category.avg_price else 0
                })
            
            cache.set(cache_key, stats, 3600)  # 1 heure
        
        return stats
    
    @staticmethod
    def get_product_performance(product_id):
        """Performance d'un produit"""
        from apps.orders.models import OrderItem
        
        # Nombre de ventes
        sales_count = OrderItem.objects.filter(
            product_id=product_id,
            order__payment_status='paid'
        ).count()
        
        # Revenue total
        total_revenue = OrderItem.objects.filter(
            product_id=product_id,
            order__payment_status='paid'
        ).aggregate(
            total=models.Sum('total_price')
        )['total'] or 0
        
        # Note moyenne
        avg_rating = Review.objects.filter(
            product_id=product_id,
            is_approved=True
        ).aggregate(
            avg=Avg('rating')
        )['avg'] or 0
        
        return {
            'sales_count': sales_count,
            'total_revenue': float(total_revenue),
            'avg_rating': round(avg_rating, 1),
            'reviews_count': Review.objects.filter(
                product_id=product_id,
                is_approved=True
            ).count()
        }
