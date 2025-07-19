# marketplace/cache.py - Système de cache pour performance

from django.core.cache import cache
from django.conf import settings
import hashlib
import json


class ProductsCache:
    """Système de cache intelligent pour Products APIs"""
    
    # Durées de cache par type de données
    CACHE_TIMEOUTS = {
        'products_list': getattr(settings, 'PRODUCTS_CACHE_TIMEOUT', 300),      # 5 min
        'categories_list': getattr(settings, 'CATEGORIES_CACHE_TIMEOUT', 1800), # 30 min
        'featured_products': getattr(settings, 'FEATURED_CACHE_TIMEOUT', 900),  # 15 min
        'product_detail': 600,      # 10 min pour détail produit
        'search_results': 180,      # 3 min pour recherche
    }
    
    @staticmethod
    def get_cache_key(prefix, **kwargs):
        """Génère une clé de cache unique basée sur les paramètres"""
        # Crée un hash des paramètres pour clé unique
        params_str = json.dumps(kwargs, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"afepanou:{prefix}:{params_hash}"
    
    @classmethod
    def get_products_list(cls, filters=None, page=1, page_size=12):
        """Cache pour liste des produits"""
        cache_key = cls.get_cache_key(
            'products_list',
            filters=filters or {},
            page=page,
            page_size=page_size
        )
        return cache.get(cache_key)
    
    @classmethod
    def set_products_list(cls, data, filters=None, page=1, page_size=12):
        """Met en cache la liste des produits"""
        cache_key = cls.get_cache_key(
            'products_list',
            filters=filters or {},
            page=page,
            page_size=page_size
        )
        cache.set(cache_key, data, cls.CACHE_TIMEOUTS['products_list'])
    
    @classmethod
    def get_featured_products(cls, limit=6):
        """Cache pour produits vedettes"""
        cache_key = cls.get_cache_key('featured_products', limit=limit)
        return cache.get(cache_key)
    
    @classmethod
    def set_featured_products(cls, data, limit=6):
        """Met en cache les produits vedettes"""
        cache_key = cls.get_cache_key('featured_products', limit=limit)
        cache.set(cache_key, data, cls.CACHE_TIMEOUTS['featured_products'])
    
    @classmethod
    def get_categories_tree(cls):
        """Cache pour arbre des catégories"""
        cache_key = 'afepanou:categories:tree'
        return cache.get(cache_key)
    
    @classmethod
    def set_categories_tree(cls, data):
        """Met en cache l'arbre des catégories"""
        cache_key = 'afepanou:categories:tree'
        cache.set(cache_key, data, cls.CACHE_TIMEOUTS['categories_list'])
    
    @classmethod
    def invalidate_product(cls, product_id):
        """Invalide le cache pour un produit spécifique"""
        # Invalide toutes les listes qui pourraient contenir ce produit
        cache_patterns = [
            'afepanou:products_list:*',
            'afepanou:featured_products:*',
            f'afepanou:product_detail:*{product_id}*',
        ]
        
        # Note: Dans un vrai environnement, utiliser Redis avec pattern matching
        # Ici on efface les clés communes
        common_keys = [
            'afepanou:featured_products:6',
            'afepanou:categories:tree',
        ]
        cache.delete_many(common_keys)
