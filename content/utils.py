# ======================================
# apps/content/utils.py
# ======================================

from django.core.cache import cache
from .models import Banner, Page, MediaContentSection


def invalidate_content_cache():
    """Invalide tous les caches de contenu"""
    cache_keys = [
        'active_banners',
        'featured_pages',
        'media_content_sections',
        'all_pages_nav'
    ]
    
    for key in cache_keys:
        cache.delete(key)
    
    # Invalider les caches de pages individuelles
    pages = Page.objects.filter(is_active=True).values_list('slug', flat=True)
    for slug in pages:
        cache.delete(f'page_detail_{slug}')
