# ======================================
# apps/core/views.py
# ======================================

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone
from .models import SiteSetting, NewsletterSubscriber
from .serializers import (
    SiteSettingSerializer, 
    NewsletterSubscriberSerializer,
    NewsletterUnsubscribeSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def site_settings(request):
    """
    Récupère les paramètres publics du site
    GET /api/core/settings/
    """
    # Essayer de récupérer depuis le cache
    cache_key = 'site_settings_public'
    settings_data = cache.get(cache_key)
    
    if settings_data is None:
        # Récupérer seulement les paramètres publics
        settings = SiteSetting.objects.filter(is_public=True)
        serializer = SiteSettingSerializer(settings, many=True)
        
        # Transformer en dictionnaire pour le frontend
        settings_data = {}
        for setting in serializer.data:
            settings_data[setting['setting_key']] = setting['setting_value']
        
        # Mettre en cache pour 1 heure
        cache.set(cache_key, settings_data, 3600)
    
    return Response({
        'success': True,
        'data': settings_data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def site_settings_by_group(request, group_name):
    """
    Récupère les paramètres par groupe
    GET /api/core/settings/group/{group_name}/
    """
    cache_key = f'site_settings_group_{group_name}'
    settings_data = cache.get(cache_key)
    
    if settings_data is None:
        settings = SiteSetting.objects.filter(
            group_name=group_name, 
            is_public=True
        )
        serializer = SiteSettingSerializer(settings, many=True)
        
        settings_data = {}
        for setting in serializer.data:
            settings_data[setting['setting_key']] = setting['setting_value']
        
        cache.set(cache_key, settings_data, 3600)
    
    return Response({
        'success': True,
        'group': group_name,
        'data': settings_data
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def newsletter_subscribe(request):
    """
    Inscription à la newsletter
    POST /api/core/newsletter/subscribe/
    Body: {"email": "test@example.com", "first_name": "John", "last_name": "Doe"}
    """
    serializer = NewsletterSubscriberSerializer(data=request.data)
    
    if serializer.is_valid():
        # Vérifier si l'email existe déjà (même inactif)
        email = serializer.validated_data['email']
        existing = NewsletterSubscriber.objects.filter(email=email).first()
        
        if existing:
            if existing.is_active:
                return Response({
                    'success': False,
                    'message': 'Cet email est déjà abonné à notre newsletter.'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Réactiver l'abonnement existant
                existing.is_active = True
                existing.subscribed_at = timezone.now()
                existing.unsubscribed_at = None
                existing.first_name = serializer.validated_data.get('first_name', existing.first_name)
                existing.last_name = serializer.validated_data.get('last_name', existing.last_name)
                existing.source = serializer.validated_data.get('source', existing.source)
                existing.save()
                
                return Response({
                    'success': True,
                    'message': 'Votre abonnement à notre newsletter a été réactivé avec succès!'
                })
        else:
            # Créer un nouvel abonnement
            subscriber = serializer.save(
                is_active=True,
                subscribed_at=timezone.now()
            )
            
            return Response({
                'success': True,
                'message': 'Merci de vous être abonné à notre newsletter!',
                'subscriber_id': subscriber.id
            }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Données invalides.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def newsletter_unsubscribe(request):
    """
    Désinscription de la newsletter
    POST /api/core/newsletter/unsubscribe/
    Body: {"email": "test@example.com"}
    """
    serializer = NewsletterUnsubscribeSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email, is_active=True)
            subscriber.is_active = False
            subscriber.unsubscribed_at = timezone.now()
            subscriber.save()
            
            return Response({
                'success': True,
                'message': 'Vous avez été désabonné avec succès de notre newsletter.'
            })
            
        except NewsletterSubscriber.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Cet email n\'est pas abonné à notre newsletter.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'success': False,
        'message': 'Email invalide.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def newsletter_stats(request):
    """
    Statistiques publiques de la newsletter
    GET /api/core/newsletter/stats/
    """
    cache_key = 'newsletter_stats'
    stats = cache.get(cache_key)
    
    if stats is None:
        total_subscribers = NewsletterSubscriber.objects.filter(is_active=True).count()
        
        stats = {
            'total_subscribers': total_subscribers,
            'milestone': 'Plus de 1000 abonnés!' if total_subscribers > 1000 else None
        }
        
        # Cache pour 30 minutes
        cache.set(cache_key, stats, 1800)
    
    return Response({
        'success': True,
        'data': stats
    })
