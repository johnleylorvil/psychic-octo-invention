# ======================================
# apps/users/views.py
# ======================================

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.utils import timezone
from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer, 
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    PasswordChangeSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Inscription utilisateur
    POST /api/v1/users/register/
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Compte créé avec succès!',
            'data': {
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Erreur lors de la création du compte.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Connexion utilisateur
    POST /api/v1/users/login/
    """
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Mettre à jour last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Connexion réussie!',
            'data': {
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
        })
    
    return Response({
        'success': False,
        'message': 'Identifiants invalides.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Déconnexion utilisateur
    POST /api/v1/users/logout/
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Déconnexion réussie!'
        })
    
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Erreur lors de la déconnexion.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Récupérer le profil utilisateur
    GET /api/v1/users/profile/
    """
    serializer = UserProfileSerializer(request.user)
    
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Mettre à jour le profil utilisateur
    PUT /api/v1/users/profile/update/
    """
    serializer = UserProfileUpdateSerializer(
        request.user, 
        data=request.data, 
        partial=True
    )
    
    if serializer.is_valid():
        user = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Profil mis à jour avec succès!',
            'data': UserProfileSerializer(user).data
        })
    
    return Response({
        'success': False,
        'message': 'Erreur lors de la mise à jour.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Changer le mot de passe
    POST /api/v1/users/change-password/
    """
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'success': True,
            'message': 'Mot de passe modifié avec succès!'
        })
    
    return Response({
        'success': False,
        'message': 'Erreur lors du changement de mot de passe.',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_seller_status(request):
    """
    Demander le statut vendeur
    POST /api/v1/users/request-seller/
    """
    user = request.user
    
    if user.is_seller:
        return Response({
            'success': False,
            'message': 'Vous êtes déjà vendeur.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Ici vous pouvez ajouter une logique d'approbation
    # Pour l'instant, on approuve automatiquement
    user.is_seller = True
    user.save()
    
    return Response({
        'success': True,
        'message': 'Félicitations! Vous êtes maintenant vendeur sur Afèpanou.',
        'data': UserProfileSerializer(user).data
    })
