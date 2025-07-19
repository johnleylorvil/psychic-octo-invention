from rest_framework.response import Response
from utils.cache import ProductsCache


class CacheableViewMixin:
    """Mixin pour ajouter le cache aux ViewSets"""
    
    def cached_list(self, request, cache_method_get, cache_method_set, *args, **kwargs):
        """Méthode générique pour liste avec cache"""
        # Tente de récupérer depuis le cache
        cached_data = cache_method_get(*args, **kwargs)
        if cached_data:
            return Response(cached_data)
        
        # Si pas en cache, exécute la requête normale
        response = super().list(request)
        
        # Met en cache si la requête a réussi
        if response.status_code == 200:
            cache_method_set(response.data, *args, **kwargs)
        
        return response