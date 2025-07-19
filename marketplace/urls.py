# marketplace/urls/__init__.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from marketplace.viewsets.auth import (
    AuthViewSet,
    CustomTokenObtainPairView,
    CustomTokenRefreshView
)
from marketplace.viewsets.products import ProductViewSet, CategoryViewSet

# ============= ROUTER CONFIGURATION =============
router = DefaultRouter()

# Auth endpoints
router.register(r'auth', AuthViewSet, basename='auth')

# Products & Categories endpoints  
router.register(r'products', ProductViewSet, basename='products')
router.register(r'categories', CategoryViewSet, basename='categories')

# ============= URL PATTERNS =============
urlpatterns = [
    # Routes du ViewSet automatiques
    path('', include(router.urls)),
    
    # Routes JWT alternatives (optionnelles)
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]

# ============= URLs GÉNÉRÉES AUTOMATIQUEMENT =============
"""
🔐 AUTH APIs:
POST   /api/auth/register/         - Inscription utilisateur
POST   /api/auth/login/            - Connexion avec JWT
POST   /api/auth/logout/           - Déconnexion + blacklist token
GET    /api/auth/profile/          - Profil utilisateur connecté
PUT    /api/auth/update_profile/   - Mise à jour profil
POST   /api/auth/change_password/  - Changement mot de passe sécurisé

🛒 PRODUCTS APIs:
GET    /api/products/                      - Liste produits (pagination, filtres, tri)
GET    /api/products/{slug}/               - Détail produit complet (images, specs, reviews)
GET    /api/products/featured/             - Produits vedettes pour landing page
GET    /api/products/search/?q=terme       - Recherche full-text multi-critères
GET    /api/products/{slug}/images/        - Galerie images d'un produit
GET    /api/products/{slug}/check_stock/   - Vérification stock temps réel
POST   /api/products/{slug}/reserve_stock/ - Réservation temporaire stock (panier)
POST   /api/products/{slug}/release_stock/ - Libération stock (abandon panier)
POST   /api/products/{slug}/confirm_purchase/ - Confirmation achat définitif (commande payée)

📂 CATEGORIES APIs:
GET    /api/categories/                    - Liste catégories hiérarchiques
GET    /api/categories/{slug}/             - Détail catégorie avec compteur produits
GET    /api/categories/{slug}/products/    - Produits d'une catégorie (pagination)
GET    /api/categories/featured/           - Catégories vedettes header navigation (3 max)
GET    /api/categories/tree/               - Arbre hiérarchique complet parent/enfant

🎯 JWT TOKENS (alternatives):
POST   /api/auth/token/                    - Obtenir token JWT standard
POST   /api/auth/token/refresh/            - Rafraîchir token JWT
"""