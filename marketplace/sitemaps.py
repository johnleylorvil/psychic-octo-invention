"""
Sitemaps for Afèpanou marketplace
SEO optimization through XML sitemap generation
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models.product import Product, Category
from .models.content import Page

class StaticViewSitemap(Sitemap):
    """Sitemap for static views"""
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            'marketplace:home',
            'marketplace:about',
            'marketplace:contact',
            'marketplace:terms',
            'marketplace:privacy',
            'marketplace:category_index',
            'marketplace:product_search',
        ]

    def location(self, item):
        return reverse(item)

class CategorySitemap(Sitemap):
    """Sitemap for product categories"""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Category.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('marketplace:category_list', kwargs={'slug': obj.slug})

class ProductSitemap(Sitemap):
    """Sitemap for products"""
    changefreq = 'daily'
    priority = 0.9
    limit = 50000

    def items(self):
        return Product.objects.available().select_related('category')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('marketplace:product_detail', kwargs={'slug': obj.slug})

class PageSitemap(Sitemap):
    """Sitemap for CMS pages"""
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Page.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()

# Dictionary of all sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'categories': CategorySitemap,
    'products': ProductSitemap,
    'pages': PageSitemap,
}