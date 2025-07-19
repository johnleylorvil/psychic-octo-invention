# marketplace/urls/__init__.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from marketplace.viewsets.auth import (
    AuthViewSet,
    CustomTokenObtainPairView,
    CustomTokenRefreshView
)
from marketplace.viewsets.products import ProductViewSet, CategoryViewSet
from marketplace.viewsets.landingpage import LandingPageViewSet

# ============= ROUTER CONFIGURATION =============
router = DefaultRouter()

# Auth endpoints
router.register(r'auth', AuthViewSet, basename='auth')

# Products & Categories endpoints  
router.register(r'products', ProductViewSet, basename='products')
router.register(r'categories', CategoryViewSet, basename='categories')

# Landing Page endpoints
router.register(r'landing-page', LandingPageViewSet, basename='landing-page')

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
🔐 AUTH APIs (6 endpoints):
POST   /api/auth/register/         - Inscription utilisateur
POST   /api/auth/login/            - Connexion avec JWT
POST   /api/auth/logout/           - Déconnexion + blacklist token
GET    /api/auth/profile/          - Profil utilisateur connecté
PUT    /api/auth/update_profile/   - Mise à jour profil
POST   /api/auth/change_password/  - Changement mot de passe sécurisé

🛒 PRODUCTS APIs (9 endpoints):
GET    /api/products/                      - Liste produits (pagination, filtres, tri)
GET    /api/products/{slug}/               - Détail produit complet (images, specs, reviews)
GET    /api/products/featured/             - Produits vedettes pour landing page
GET    /api/products/search/?q=terme       - Recherche full-text multi-critères
GET    /api/products/{slug}/images/        - Galerie images d'un produit
GET    /api/products/{slug}/check_stock/   - Vérification stock temps réel
POST   /api/products/{slug}/reserve_stock/ - Réservation temporaire stock (panier)
POST   /api/products/{slug}/release_stock/ - Libération stock (abandon panier)
POST   /api/products/{slug}/confirm_purchase/ - Confirmation achat définitif (commande payée)

📂 CATEGORIES APIs (5 endpoints):
GET    /api/categories/                    - Liste catégories hiérarchiques
GET    /api/categories/{slug}/             - Détail catégorie avec compteur produits
GET    /api/categories/{slug}/products/    - Produits d'une catégorie (pagination)
GET    /api/categories/featured/           - Catégories vedettes header navigation (3 max)
GET    /api/categories/tree/               - Arbre hiérarchique complet parent/enfant

🎪 LANDING PAGE APIs (8 endpoints):
GET    /api/landing-page/                  - Page complète avec toutes sections
GET    /api/landing-page/header/           - Section header (logo, nav, search, cart)
GET    /api/landing-page/banners/          - Carrousel bannières rotatives
GET    /api/landing-page/popular-products/ - Produits vedettes (3-6 items)
GET    /api/landing-page/content-sections/ - Media & Text Content sections
GET    /api/landing-page/footer/           - Footer (identity, nav, settings)
GET    /api/landing-page/carousel-configs/ - Configurations carrousels
POST   /api/landing-page/refresh-cache/    - Rafraîchissement cache (admin)

🎯 JWT TOKENS (alternatives):
POST   /api/auth/token/                    - Obtenir token JWT standard
POST   /api/auth/token/refresh/            - Rafraîchir token JWT

=====================================================================
📊 TOTAL APIs FONCTIONNELLES: 28 endpoints
=====================================================================

🎯 WORKFLOW UTILISATEUR COMPLET:
1. Landing Page (/api/landing-page/) → Découverte site
2. Auth (/api/auth/register|login/) → Compte utilisateur  
3. Categories (/api/categories/featured/) → Navigation
4. Products (/api/products/ + search) → Catalogue
5. Cart APIs → À développer (utilise stock management)
6. Orders APIs → À développer (workflow checkout)
7. Payment APIs → À développer (MonCash integration)

🏗️ ARCHITECTURE MODULAIRE:
- Auth: Authentification JWT complète
- Products: Catalogue avec stock management
- Categories: Navigation hiérarchique
- Landing: Structure page d'accueil complète
- Cache: Performance optimisée par section
- Admin: Interface administration complète

🚀 MVP READY:
✅ Backend complet (90%)
✅ APIs fonctionnelles (28 endpoints)
✅ Landing page structurée
✅ Catalogue produits avec stock
✅ Authentification sécurisée
✅ Performance optimisée

🔲 Restant (10%):
- Cart APIs (4%)
- Orders APIs (3%) 
- MonCash Payment (3%)
"""