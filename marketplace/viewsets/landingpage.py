# marketplace/viewsets/landing.py
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count, Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from ..models import (
    Banner, MediaContentSection, Page, SiteSetting,
    Category, Product, ProductImage
)
from ..serializers.landingpage import (
    LandingPageSerializer,
    HeaderConfigSerializer,
    BannerSectionSerializer,
    PopularProductsSectionSerializer,
    ContentSectionsSerializer,
    FooterSectionSerializer,
    CarouselConfigSerializer
)

# ============= LANDING PAGE MASTER VIEW =============

class LandingPageViewSet(ViewSet):
    """
    ViewSet principal pour la Landing Page complète
    Orchestre toutes les sections selon design guidelines
    """
    
    def get_cache_key(self, section=None):
        """Génère clé de cache dynamique"""
        base_key = 'landing_page'
        if section:
            return f"{base_key}_{section}"
        return base_key
    
    def get_cache_timeout(self):
        """Timeout cache configurable"""
        try:
            setting = SiteSetting.objects.get(setting_key='landing_cache_timeout')
            return int(setting.setting_value)
        except (SiteSetting.DoesNotExist, ValueError):
            return 300  # 5 minutes par défaut
    
    def invalidate_cache(self):
        """Invalide tous les caches de la landing page"""
        cache_keys = [
            'landing_page',
            'landing_page_header',
            'landing_page_banners', 
            'landing_page_products',
            'landing_page_content',
            'landing_page_footer'
        ]
        
        for key in cache_keys:
            cache.delete(key)
    
    @method_decorator(vary_on_headers('User-Agent', 'Accept-Language'))
    def list(self, request):
        """
        GET /api/landing-page/
        Retourne la structure complète de la landing page
        """
        
        # Vérification cache global
        cache_key = self.get_cache_key()
        cached_data = cache.get(cache_key)
        
        if cached_data and not settings.DEBUG:
            return Response({
                'success': True,
                'timestamp': timezone.now().isoformat(),
                'data': cached_data,
                'cache_hit': True
            })
        
        try:
            # Construction de l'objet data complet
            landing_data = self._build_landing_page_data()
            
            # Sérialisation avec le master serializer
            serializer = LandingPageSerializer(landing_data)
            response_data = serializer.data
            
            # Mise en cache
            cache.set(cache_key, response_data, self.get_cache_timeout())
            
            return Response({
                'success': True,
                'timestamp': timezone.now().isoformat(),
                'data': response_data,
                'cache_hit': False,
                'cache_ttl': self.get_cache_timeout()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Erreur lors de la construction de la landing page',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _build_landing_page_data(self):
        """Construit l'objet data avec optimisations de requêtes"""
        
        # Object factice pour passer aux serializers
        # (les serializers utilisent des SerializerMethodField)
        class LandingPageData:
            pass
        
        return LandingPageData()
    
    @action(detail=False, methods=['get'], url_path='header')
    def header(self, request):
        """
        GET /api/landing-page/header/
        Section header uniquement
        """
        cache_key = self.get_cache_key('header')
        cached_data = cache.get(cache_key)
        
        if cached_data and not settings.DEBUG:
            return Response(cached_data)
        
        try:
            # Optimisation requêtes pour header
            categories = Category.objects.filter(
                is_featured=True,
                is_active=True
            ).annotate(
                products_count=Count('products', filter=Q(
                    products__is_active=True,
                    products__stock_quantity__gt=0
                ))
            ).order_by('sort_order')[:3]
            
            data = LandingPageData()
            serializer = HeaderConfigSerializer(data)
            result = serializer.data
            
            cache.set(cache_key, result, self.get_cache_timeout())
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': 'Erreur lors de la récupération du header',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='banners')
    def banners(self, request):
        """
        GET /api/landing-page/banners/
        Section bannières carrousel uniquement
        """
        cache_key = self.get_cache_key('banners')
        cached_data = cache.get(cache_key)
        
        if cached_data and not settings.DEBUG:
            return Response(cached_data)
        
        try:
            # Pré-filtrage des bannières valides
            now = timezone.now().date()
            banners = Banner.objects.filter(
                is_active=True
            ).filter(
                Q(start_date__isnull=True) | Q(start_date__lte=now)
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=now)
            ).order_by('sort_order')
            
            data = LandingPageData()
            serializer = BannerSectionSerializer(data)
            result = serializer.data
            
            cache.set(cache_key, result, self.get_cache_timeout())
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': 'Erreur lors de la récupération des bannières',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='popular-products')
    def popular_products(self, request):
        """
        GET /api/landing-page/popular-products/
        Section produits vedettes uniquement
        """
        cache_key = self.get_cache_key('products')
        cached_data = cache.get(cache_key)
        
        if cached_data and not settings.DEBUG:
            return Response(cached_data)
        
        try:
            # Optimisation requêtes pour produits vedettes
            products = Product.objects.filter(
                is_featured=True,
                is_active=True,
                stock_quantity__gt=0
            ).select_related('category', 'seller').prefetch_related(
                Prefetch(
                    'images',
                    queryset=ProductImage.objects.filter(
                        Q(is_primary=True) | Q(image_type='main')
                    ).order_by('-is_primary', 'sort_order')
                )
            ).order_by('-created_at')[:6]
            
            data = LandingPageData()
            serializer = PopularProductsSectionSerializer(data)
            result = serializer.data
            
            cache.set(cache_key, result, self.get_cache_timeout())
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': 'Erreur lors de la récupération des produits vedettes',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='content-sections')
    def content_sections(self, request):
        """
        GET /api/landing-page/content-sections/
        Section Media & Text Content uniquement
        """
        cache_key = self.get_cache_key('content')
        cached_data = cache.get(cache_key)
        
        if cached_data and not settings.DEBUG:
            return Response(cached_data)
        
        try:
            # Pré-chargement des sections actives
            sections = MediaContentSection.objects.filter(
                is_active=True
            ).order_by('sort_order')
            
            data = LandingPageData()
            serializer = ContentSectionsSerializer(data)
            result = serializer.data
            
            cache.set(cache_key, result, self.get_cache_timeout())
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': 'Erreur lors de la récupération des sections de contenu',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='footer')
    def footer(self, request):
        """
        GET /api/landing-page/footer/
        Section footer uniquement
        """
        cache_key = self.get_cache_key('footer')
        cached_data = cache.get(cache_key)
        
        if cached_data and not settings.DEBUG:
            return Response(cached_data)
        
        try:
            # Pré-chargement des pages footer
            footer_pages = Page.objects.filter(
                is_active=True,
                slug__in=[
                    'notre-mission', 'notre-histoire', 'devenir-vendeur',
                    'politique-confidentialite', 'conditions-utilisation'
                ]
            ).order_by('sort_order')
            
            data = LandingPageData()
            serializer = FooterSectionSerializer(data)
            result = serializer.data
            
            cache.set(cache_key, result, self.get_cache_timeout())
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': 'Erreur lors de la récupération du footer',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='carousel-configs')
    def carousel_configs(self, request):
        """
        GET /api/landing-page/carousel-configs/
        Configurations carrousels uniquement
        """
        try:
            data = LandingPageData()
            serializer = CarouselConfigSerializer(data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({
                'error': 'Erreur lors de la récupération des configurations carrousel',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='refresh-cache')
    def refresh_cache(self, request):
        """
        POST /api/landing-page/refresh-cache/
        Force le rafraîchissement du cache (admin uniquement)
        """
        
        # Vérification permissions admin
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({
                'error': 'Permission refusée'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Invalidation cache
            self.invalidate_cache()
            
            # Reconstruction immédiate
            landing_data = self._build_landing_page_data()
            serializer = LandingPageSerializer(landing_data)
            new_data = serializer.data
            
            # Mise en cache
            cache_key = self.get_cache_key()
            cache.set(cache_key, new_data, self.get_cache_timeout())
            
            return Response({
                'success': True,
                'message': 'Cache de la landing page rafraîchi avec succès',
                'timestamp': timezone.now().isoformat(),
                'cache_keys_invalidated': [
                    'landing_page', 'landing_page_header', 'landing_page_banners',
                    'landing_page_products', 'landing_page_content', 'landing_page_footer'
                ]
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Erreur lors du rafraîchissement du cache',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============= ALTERNATIVE: SIMPLE API VIEW =============

class LandingPageAPIView(APIView):
    """
    Alternative simple avec APIView pour la landing page complète
    Plus direct et léger que le ViewSet
    """
    
    def get(self, request):
        """GET /api/landing-page/ - Version simplifiée"""
        
        try:
            # Vérification cache
            cache_key = 'landing_page_simple'
            cached_data = cache.get(cache_key)
            
            if cached_data and not settings.DEBUG:
                return Response({
                    'success': True,
                    'data': cached_data,
                    'cache_hit': True,
                    'timestamp': timezone.now().isoformat()
                })
            
            # Construction données
            class LandingData:
                pass
            
            landing_data = LandingData()
            serializer = LandingPageSerializer(landing_data)
            result = serializer.data
            
            # Cache pendant 5 minutes
            cache.set(cache_key, result, 300)
            
            return Response({
                'success': True,
                'data': result,
                'cache_hit': False,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Erreur serveur',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============= UTILS ET HELPERS =============

class LandingPageUtils:
    """Utilitaires pour la landing page"""
    
    @staticmethod
    def get_featured_categories(limit=3):
        """Récupère les catégories featured avec optimisations"""
        return Category.objects.filter(
            is_featured=True,
            is_active=True
        ).annotate(
            active_products_count=Count(
                'products',
                filter=Q(
                    products__is_active=True,
                    products__stock_quantity__gt=0
                )
            )
        ).order_by('sort_order')[:limit]
    
    @staticmethod
    def get_featured_products(limit=6):
        """Récupère les produits vedettes avec optimisations"""
        return Product.objects.filter(
            is_featured=True,
            is_active=True,
            stock_quantity__gt=0
        ).select_related('category', 'seller').prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.filter(
                    is_primary=True
                ).order_by('sort_order')
            )
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_active_banners():
        """Récupère les bannières actives et valides"""
        now = timezone.now().date()
        return Banner.objects.filter(
            is_active=True
        ).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        ).order_by('sort_order')
    
    @staticmethod
    def get_content_sections():
        """Récupère les sections de contenu actives"""
        return MediaContentSection.objects.filter(
            is_active=True
        ).order_by('sort_order')
    
    @staticmethod
    def get_footer_pages():
        """Récupère les pages pour le footer"""
        return Page.objects.filter(
            is_active=True,
            slug__in=[
                'notre-mission', 'notre-histoire', 'devenir-vendeur',
                'politique-confidentialite', 'conditions-utilisation',
                'mentions-legales'
            ]
        ).order_by('sort_order')

# ============= CACHE MANAGEMENT =============

class LandingPageCacheManager:
    """Gestionnaire de cache pour la landing page"""
    
    CACHE_KEYS = {
        'main': 'landing_page',
        'header': 'landing_page_header',
        'banners': 'landing_page_banners',
        'products': 'landing_page_products',
        'content': 'landing_page_content',
        'footer': 'landing_page_footer'
    }
    
    @classmethod
    def invalidate_all(cls):
        """Invalide tous les caches"""
        for key in cls.CACHE_KEYS.values():
            cache.delete(key)
    
    @classmethod
    def invalidate_section(cls, section):
        """Invalide le cache d'une section spécifique"""
        if section in cls.CACHE_KEYS:
            cache.delete(cls.CACHE_KEYS[section])
    
    @classmethod
    def get_cache_info(cls):
        """Informations sur l'état du cache"""
        cache_status = {}
        for name, key in cls.CACHE_KEYS.items():
            cache_status[name] = {
                'key': key,
                'cached': cache.get(key) is not None
            }
        return cache_status