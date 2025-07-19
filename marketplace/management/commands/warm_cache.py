from django.core.management.base import BaseCommand
from marketplace.models import Product, Category
from marketplace.serializers.products import ProductFeaturedSerializer, CategoryListSerializer
from marketplace.utils.cache import ProductsCache


class Command(BaseCommand):
    help = 'Pré-chauffe le cache avec les données les plus utilisées'
    
    def handle(self, *args, **options):
        self.stdout.write('🔥 Pré-chauffage du cache en cours...')
        
        # Cache des produits vedettes
        featured_products = Product.objects.filter(
            is_featured=True, 
            is_active=True
        ).select_related('category').prefetch_related('productimages_set')[:6]
        
        featured_data = ProductFeaturedSerializer(featured_products, many=True).data
        ProductsCache.set_featured_products(featured_data, limit=6)
        self.stdout.write(f'✅ {len(featured_data)} produits vedettes mis en cache')
        
        # Cache de l'arbre des catégories
        categories = Category.objects.filter(is_active=True).order_by('sort_order')
        categories_data = CategoryListSerializer(categories, many=True).data
        ProductsCache.set_categories_tree(categories_data)
        self.stdout.write(f'✅ {len(categories_data)} catégories mises en cache')
        
        self.stdout.write(self.style.SUCCESS('🎉 Cache pré-chauffé avec succès !'))