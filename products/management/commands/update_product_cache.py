# ======================================
# apps/products/management/commands/update_product_cache.py
# ======================================

from django.core.management.base import BaseCommand
from django.core.cache import cache
from products.models import Product, Category


class Command(BaseCommand):
    help = 'Met à jour le cache des produits'
    
    def handle(self, *args, **options):
        self.stdout.write('Mise à jour du cache des produits...')
        
        # Vider les caches existants
        cache_keys = [
            'featured_products',
            'categories_list',
            'category_stats',
            'popular_searches'
        ]
        
        for key in cache_keys:
            cache.delete(key)
        
        # Pré-charger les données importantes
        
        # Produits vedettes
        featured_products = Product.objects.filter(
            is_active=True, 
            is_featured=True
        ).select_related('category')[:8]
        
        # Catégories actives
        categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Cache mis à jour: {len(featured_products)} produits vedettes, '
                f'{len(categories)} catégories'
            )
        )