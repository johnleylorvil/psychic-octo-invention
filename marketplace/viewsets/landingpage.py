# marketplace/viewsets/landing.py

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
# ✨ CHANGEMENT: Imports pour la gestion des permissions
from rest_framework.permissions import AllowAny, IsAdminUser

from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count, Prefetch
from django.utils.decorators import method_decorator
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


# ============= CLASSE HELPER POUR SERIALIZERS =============

class LandingPageData:
    """
    Classe factice pour passer aux serializers qui utilisent SerializerMethodField.
    """
    pass


# ============= LANDING PAGE MASTER VIEW =============

class LandingPageViewSet(ViewSet):
    """
    ViewSet principal pour la Landing Page complète, avec accès public.
    """

    # ✨ CHANGEMENT: Gestion dynamique des permissions
    def get_permissions(self):
        """
        Définit les permissions en fonction de l'action.
        - L'accès est public par défaut.
        - Seul un admin peut rafraîchir le cache.
        """
        if self.action == 'refresh_cache':
            return [IsAdminUser()]
        return [AllowAny()]

    def get_cache_key(self, section=None):
        """Génère une clé de cache dynamique."""
        base_key = 'landing_page'
        if section:
            return f"{base_key}_{section}"
        return base_key

    def get_cache_timeout(self):
        """Récupère le timeout du cache depuis les paramètres."""
        try:
            setting = SiteSetting.objects.get(setting_key='landing_cache_timeout')
            return int(setting.setting_value)
        except (SiteSetting.DoesNotExist, ValueError):
            return 300  # 5 minutes par défaut

    # ✨ CHANGEMENT: Utilisation du CacheManager pour invalider les clés
    def invalidate_cache(self):
        """Invalide tous les caches de la landing page via le manager."""
        LandingPageCacheManager.invalidate_all()

    @method_decorator(vary_on_headers('User-Agent', 'Accept-Language'))
    def list(self, request):
        """
        GET /api/landing-page/
        Retourne la structure complète de la landing page.
        """
        cache_key = self.get_cache_key()
        cached_data = cache.get(cache_key)

        if cached_data and not settings.DEBUG:
            return Response({
                'success': True, 'timestamp': timezone.now().isoformat(),
                'data': cached_data, 'cache_hit': True
            })

        try:
            serializer = LandingPageSerializer(instance=LandingPageData())
            response_data = serializer.data
            cache.set(cache_key, response_data, self.get_cache_timeout())

            return Response({
                'success': True, 'timestamp': timezone.now().isoformat(),
                'data': response_data, 'cache_hit': False,
                'cache_ttl': self.get_cache_timeout()
            })
        except Exception as e:
            return Response({
                'success': False, 'error': 'Erreur lors de la construction de la landing page',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Cette méthode n'est plus vraiment utilisée si les serializers font leurs requêtes,
    # mais on la garde pour la structure.
    def _build_landing_page_data(self):
        return LandingPageData()

    @action(detail=False, methods=['get'], url_path='header')
    def header(self, request):
        """GET /api/landing-page/header/"""
        cache_key = self.get_cache_key('header')
        cached_data = cache.get(cache_key)
        if cached_data and not settings.DEBUG:
            return Response(cached_data)

        try:
            # ✨ CHANGEMENT: La vue ne fait plus de requêtes, le serializer s'en charge.
            # Si on voulait appliquer le pattern complet, la vue ferait l'appel à LandingPageUtils
            # et passerait les données au serializer. Pour l'instant on garde le comportement initial.
            serializer = HeaderConfigSerializer(instance=LandingPageData())
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
        """GET /api/landing-page/banners/"""
        cache_key = self.get_cache_key('banners')
        cached_data = cache.get(cache_key)
        if cached_data and not settings.DEBUG:
            return Response(cached_data)

        try:
            serializer = BannerSectionSerializer(instance=LandingPageData())
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
        """GET /api/landing-page/popular-products/"""
        cache_key = self.get_cache_key('products')
        cached_data = cache.get(cache_key)
        if cached_data and not settings.DEBUG:
            return Response(cached_data)

        try:
            serializer = PopularProductsSectionSerializer(instance=LandingPageData())
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
        """GET /api/landing-page/content-sections/"""
        cache_key = self.get_cache_key('content')
        cached_data = cache.get(cache_key)
        if cached_data and not settings.DEBUG:
            return Response(cached_data)

        try:
            serializer = ContentSectionsSerializer(instance=LandingPageData())
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
        """GET /api/landing-page/footer/"""
        cache_key = self.get_cache_key('footer')
        cached_data = cache.get(cache_key)
        if cached_data and not settings.DEBUG:
            return Response(cached_data)
        
        try:
            serializer = FooterSectionSerializer(instance=LandingPageData())
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
        """GET /api/landing-page/carousel-configs/"""
        try:
            serializer = CarouselConfigSerializer(instance=LandingPageData())
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
        Force le rafraîchissement du cache (admin uniquement).
        """
        # ✨ CHANGEMENT: Le check manuel de permission est retiré,
        # car get_permissions() s'en charge en amont.
        try:
            self.invalidate_cache()
            
            # Reconstruction du cache principal
            serializer = LandingPageSerializer(instance=LandingPageData())
            new_data = serializer.data
            cache.set(self.get_cache_key(), new_data, self.get_cache_timeout())

            return Response({
                'success': True,
                'message': 'Cache de la landing page rafraîchi avec succès.',
                'timestamp': timezone.now().isoformat()
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
    Alternative simple avec APIView pour la landing page complète.
    """
    # ✨ CHANGEMENT: Ajout de la permission pour rendre la vue publique
    permission_classes = [AllowAny]

    def get(self, request):
        """GET /api/landing-page/ - Version simplifiée"""
        cache_key = 'landing_page_simple'
        cached_data = cache.get(cache_key)
        if cached_data and not settings.DEBUG:
            return Response({
                'success': True, 'data': cached_data,
                'cache_hit': True, 'timestamp': timezone.now().isoformat()
            })
        try:
            serializer = LandingPageSerializer(instance=LandingPageData())
            result = serializer.data
            cache.set(cache_key, result, 300)
            return Response({
                'success': True, 'data': result,
                'cache_hit': False, 'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            return Response({
                'success': False, 'error': 'Erreur serveur',
                'details': str(e) if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============= UTILS ET HELPERS =============

class LandingPageUtils:
    """
    Utilitaires pour la landing page.
    Ces méthodes devraient être appelées par les SerializerMethodField des serializers.
    """
    @staticmethod
    def get_featured_categories(limit=3):
        return Category.objects.filter(
            is_featured=True, is_active=True
        ).annotate(
            active_products_count=Count(
                'products',
                filter=Q(products__is_active=True, products__stock_quantity__gt=0)
            )
        ).order_by('sort_order')[:limit]

    @staticmethod
    def get_featured_products(limit=6):
        return Product.objects.filter(
            is_featured=True, is_active=True, stock_quantity__gt=0
        ).select_related('category', 'seller').prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.filter(is_primary=True).order_by('sort_order')
            )
        ).order_by('-created_at')[:limit]

    @staticmethod
    def get_active_banners():
        now = timezone.now().date()
        return Banner.objects.filter(is_active=True).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        ).order_by('sort_order')

    @staticmethod
    def get_content_sections():
        return MediaContentSection.objects.filter(is_active=True).order_by('sort_order')

    @staticmethod
    def get_footer_pages():
        # ✨ NOTE: Pour plus de flexibilité, envisagez d'ajouter un champ booléen
        # `show_in_footer` au modèle Page au lieu de hardcoder les slugs ici.
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
    """Gestionnaire de cache centralisé pour la landing page."""
    CACHE_KEYS = {
        'main': 'landing_page', 'header': 'landing_page_header',
        'banners': 'landing_page_banners', 'products': 'landing_page_products',
        'content': 'landing_page_content', 'footer': 'landing_page_footer'
    }

    @classmethod
    def invalidate_all(cls):
        """Invalide tous les caches connus."""
        for key in cls.CACHE_KEYS.values():
            cache.delete(key)

    @classmethod
    def invalidate_section(cls, section):
        """Invalide le cache d'une section spécifique."""
        if section in cls.CACHE_KEYS:
            cache.delete(cls.CACHE_KEYS[section])

    @classmethod
    def get_cache_info(cls):
        """Retourne l'état actuel du cache."""
        return {
            name: {'key': key, 'cached': cache.get(key) is not None}
            for name, key in cls.CACHE_KEYS.items()
        }