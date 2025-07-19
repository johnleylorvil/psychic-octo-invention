from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from marketplace.models import User
from marketplace.serializers.auth import (
    UserSerializer,
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    LoginSerializer,
    UserProfileUpdateSerializer,
    ChangePasswordSerializer
)


class AuthViewSet(viewsets.GenericViewSet):
    """ViewSet pour l'authentification"""
    
    def get_permissions(self):
        """Permissions selon l'action"""
        if self.action in ['register', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Serializer selon l'action"""
        if self.action == 'register':
            return UserRegistrationSerializer
        elif self.action == 'login':
            return LoginSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Inscription d'un nouvel utilisateur
        
        POST /api/auth/register/
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "motdepasse123",
            "password_confirm": "motdepasse123",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+509 1234-5678",
            "city": "Port-au-Prince",
            "country": "Haïti",
            "is_seller": false
        }
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Générer les tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Données utilisateur
            user_data = UserSerializer(user).data
            
            return Response({
                'success': True,
                'message': 'Inscription réussie!',
                'user': user_data,
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Erreur lors de l\'inscription',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Connexion utilisateur
        
        POST /api/auth/login/
        {
            "username": "john_doe",  // ou email
            "password": "motdepasse123"
        }
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Générer les tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Données utilisateur
            user_data = UserSerializer(user).data
            
            # Mettre à jour last_login
            user.save(update_fields=['last_login'])
            
            return Response({
                'success': True,
                'message': 'Connexion réussie!',
                'user': user_data,
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Identifiants invalides',
            'errors': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Déconnexion utilisateur (blacklist refresh token)
        
        POST /api/auth/logout/
        {
            "refresh": "refresh_token_here"
        }
        """
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                # CORRECTION: Utiliser la méthode correcte pour blacklister le token
                try:
                    # Méthode 1: Si le package token_blacklist est installé
                    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
                    outstanding_token = OutstandingToken.objects.get(token=token)
                    BlacklistedToken.objects.get_or_create(token=outstanding_token)
                except ImportError:
                    # Méthode 2: Si pas de token_blacklist, on peut simplement valider le token
                    # Le token sera invalidé naturellement à l'expiration
                    pass
                except Exception:
                    # Méthode 3: Alternative simple - le token sera invalidé à l'expiration
                    pass
            
            return Response({
                'success': True,
                'message': 'Déconnexion réussie!'
            }, status=status.HTTP_200_OK)
        
        except TokenError:
            return Response({
                'success': False,
                'message': 'Token invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Erreur lors de la déconnexion: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        Récupérer le profil utilisateur
        
        GET /api/auth/profile/
        """
        user_data = UserSerializer(request.user).data
        return Response({
            'success': True,
            'user': user_data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        Mettre à jour le profil utilisateur
        
        PUT/PATCH /api/auth/update_profile/
        {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+509 1234-5678",
            "address": "123 Rue Example",
            "city": "Port-au-Prince"
        }
        """
        serializer = UserProfileUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            
            return Response({
                'success': True,
                'message': 'Profil mis à jour avec succès!',
                'user': user_data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Erreur lors de la mise à jour',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Changer le mot de passe
        
        POST /api/auth/change_password/
        {
            "old_password": "ancien_mot_de_passe",
            "new_password": "nouveau_mot_de_passe",
            "new_password_confirm": "nouveau_mot_de_passe"
        }
        """
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'success': True,
                'message': 'Mot de passe modifié avec succès!'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Erreur lors du changement de mot de passe',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vue personnalisée pour l'obtention de tokens JWT"""
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            return Response({
                'success': True,
                'message': 'Connexion réussie!',
                **serializer.validated_data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Identifiants invalides',
                'errors': {'detail': 'Nom d\'utilisateur ou mot de passe incorrect'}
            }, status=status.HTTP_401_UNAUTHORIZED)


class CustomTokenRefreshView(TokenRefreshView):
    """Vue personnalisée pour le refresh de tokens JWT"""
    
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                return Response({
                    'success': True,
                    'message': 'Token rafraîchi avec succès!',
                    **response.data
                }, status=status.HTTP_200_OK)
            return response
        
        except InvalidToken:
            return Response({
                'success': False,
                'message': 'Token de rafraîchissement invalide',
                'errors': {'detail': 'Le token de rafraîchissement est invalide ou expiré'}
            }, status=status.HTTP_401_UNAUTHORIZED)