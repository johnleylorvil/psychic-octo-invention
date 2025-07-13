# ======================================
# apps/content/views.py
# ======================================

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.utils import timezone
from django.db.models import F
from .models import Banner, Page, MediaContentSection
from .serializers import BannerSerializer, PageSerializer, MediaContentSectionSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def active_banners(request):
    """
    Récupère les bannières actives
    GET /api/v1/content/banners/
    """
    cache_key = 'active_banners'
    banners_data = cache.get(cache_key)
    
    if banners_data is None:
        today = timezone.now().date()
        
        banners = Banner.objects.filter(
            is_active=True
        ).filter(
            # Filtrer par dates si définies
            models.Q(start_date__isnull=True) | models.Q(start_date__lte=today),
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
        ).order_by('sort_order', 'created_at')
        
        serializer = BannerSerializer(banners, many=True)
        banners_data = serializer.data
        cache.set(cache_key, banners_data, 1800)  # 30 minutes
    
    return Response({
        'success': True,
        'data': banners_data
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def track_banner_click(request, banner_id):
    """
    Enregistre un clic sur une bannière
    POST /api/v1/content/banners/{banner_id}/click/
    """
    try:
        banner = Banner.objects.get(id=banner_id, is_active=True)
        
        # Incrémenter le compteur de clics
        Banner.objects.filter(id=banner_id).update(click_count=F('click_count') + 1)
        
        return Response({
            'success': True,
            'message': 'Clic enregistré',
            'redirect_url': banner.link_url
        })
        
    except Banner.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Bannière non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def page_detail(request, slug):
    """
    Récupère une page par son slug
    GET /api/v1/content/pages/{slug}/
    """
    cache_key = f'page_detail_{slug}'
    page_data = cache.get(cache_key)
    
    if page_data is None:
        page = get_object_or_404(Page, slug=slug, is_active=True)
        serializer = PageSerializer(page)
        page_data = serializer.data
        cache.set(cache_key, page_data, 3600)  # 1 heure
    
    return Response({
        'success': True,
        'data': page_data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def featured_pages(request):
    """
    Récupère les pages vedettes
    GET /api/v1/content/pages/featured/
    """
    cache_key = 'featured_pages'
    pages_data = cache.get(cache_key)
    
    if pages_data is None:
        pages = Page.objects.filter(
            is_active=True,
            is_featured=True
        ).order_by('sort_order', '-created_at')[:6]
        
        serializer = PageSerializer(pages, many=True)
        pages_data = serializer.data
        cache.set(cache_key, pages_data, 3600)  # 1 heure
    
    return Response({
        'success': True,
        'data': pages_data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def media_content_sections(request):
    """
    Récupère les sections de contenu média actives
    GET /api/v1/content/sections/
    """
    cache_key = 'media_content_sections'
    sections_data = cache.get(cache_key)
    
    if sections_data is None:
        sections = MediaContentSection.objects.filter(
            is_active=True
        ).order_by('sort_order', 'created_at')
        
        serializer = MediaContentSectionSerializer(sections, many=True)
        sections_data = serializer.data
        cache.set(cache_key, sections_data, 1800)  # 30 minutes
    
    return Response({
        'success': True,
        'data': sections_data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def section_products(request, section_id):
    """
    Récupère les produits liés à une section de contenu
    GET /api/v1/content/sections/{section_id}/products/
    """
    section = get_object_or_404(MediaContentSection, id=section_id, is_active=True)
    
    from apps.products.models import Product
    from apps.products.serializers import ProductListSerializer
    
    products = Product.objects.filter(is_active=True)
    
    # Filtrer par catégories si définis
    if section.category_tags:
        try:
            category_ids = [int(id.strip()) for id in section.category_tags.split(',') if id.strip().isdigit()]
            if category_ids:
                products = products.filter(category_id__in=category_ids)
        except:
            pass
    
    # Filtrer par tags produits si définis
    if section.product_tags:
        try:
            tags = [tag.strip() for tag in section.product_tags.split(',') if tag.strip()]
            if tags:
                for tag in tags:
                    products = products.filter(tags__icontains=tag)
        except:
            pass
    
    # Limiter à 8 produits
    products = products.select_related('category')[:8]
    
    serializer = ProductListSerializer(products, many=True)
    
    return Response({
        'success': True,
        'data': {
            'section': MediaContentSectionSerializer(section).data,
            'products': serializer.data
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def all_pages(request):
    """
    Récupère toutes les pages actives (pour navigation)
    GET /api/v1/content/pages/
    """
    cache_key = 'all_pages_nav'
    pages_data = cache.get(cache_key)
    
    if pages_data is None:
        pages = Page.objects.filter(
            is_active=True
        ).values('id', 'title', 'slug', 'excerpt').order_by('sort_order', 'title')
        
        pages_data = list(pages)
        cache.set(cache_key, pages_data, 3600)  # 1 heure
    
    return Response({
        'success': True,
        'data': pages_data
    })