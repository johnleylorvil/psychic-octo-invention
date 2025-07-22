# marketplace/urls.py (MISE À JOUR)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from marketplace.viewsets.auth import (
    AuthViewSet,
    CustomTokenObtainPairView,
    CustomTokenRefreshView
)
from marketplace.viewsets.products import ProductViewSet, CategoryViewSet
from marketplace.viewsets.landingpage import LandingPageViewSet
from marketplace.viewsets.cart_views import CartViewSet  # 🎯 NOUVEAU
from marketplace.viewsets.order_views import OrderViewSet # 🎯 NOUVEAU
from marketplace.viewsets.payment_viewsets import PaymentViewSet
# ============= ROUTER CONFIGURATION =============
# ============= ROUTER CONFIGURATION =============
router = DefaultRouter()

# Auth endpoints
router.register(r'auth', AuthViewSet, basename='auth')

# Products & Categories endpoints
router.register(r'products', ProductViewSet, basename='products')
router.register(r'categories', CategoryViewSet, basename='categories')

# Cart, Orders & Payments endpoints
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'payments', PaymentViewSet, basename='payments') # ✅ FINAL

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

# =====================================================================
# 📚 DOCUMENTATION COMPLÈTE DES ENDPOINTS DE L'API
# =====================================================================
"""
🔐 AUTH APIs (6 endpoints):
POST   /api/auth/register/           - Inscription utilisateur
POST   /api/auth/login/              - Connexion avec JWT
POST   /api/auth/logout/             - Déconnexion + blacklist token
GET    /api/auth/profile/            - Profil utilisateur connecté
PUT    /api/auth/update_profile/     - Mise à jour profil
POST   /api/auth/change_password/    - Changement mot de passe sécurisé

🛒 PRODUCTS APIs (9 endpoints):
GET    /api/products/                - Liste produits (pagination, filtres, tri)
GET    /api/products/{slug}/         - Détail produit complet (images, specs, reviews)
GET    /api/products/featured/       - Produits vedettes pour landing page
GET    /api/products/search/?q=terme - Recherche full-text multi-critères
GET    /api/products/{slug}/images/  - Galerie images d'un produit
GET    /api/products/{slug}/check_stock/ - Vérification stock temps réel
POST   /api/products/{slug}/reserve_stock/ - Réservation temporaire stock (panier)
POST   /api/products/{slug}/release_stock/ - Libération stock (abandon panier)
POST   /api/products/{slug}/confirm_purchase/ - Confirmation achat définitif

📂 CATEGORIES APIs (5 endpoints):
GET    /api/categories/              - Liste catégories hiérarchiques
GET    /api/categories/{slug}/       - Détail catégorie avec compteur produits
GET    /api/categories/{slug}/products/ - Produits d'une catégorie (pagination)
GET    /api/categories/featured/     - Catégories vedettes header (3 max)
GET    /api/categories/tree/         - Arbre hiérarchique complet

🛍️ CART APIs (7 endpoints):
GET    /api/cart/                    - Panier actuel utilisateur (auto-création)
POST   /api/cart/add_item/           - Ajouter produit + réservation stock
PUT    /api/cart/update_item/        - Modifier quantité + validation stock
DELETE /api/cart/remove_item/       - Supprimer article + libération stock
DELETE /api/cart/clear/             - Vider panier + libération stock globale
POST   /api/cart/validate_stock/     - Validation stock avant checkout
GET    /api/cart/summary/            - Résumé rapide (header count)

📦 ORDERS APIs (7 endpoints):
GET    /api/orders/                  - Liste commandes paginée + filtres
GET    /api/orders/{order_number}/   - Détail complet + timeline
POST   /api/orders/create_from_cart/ - Checkout principal
PUT    /api/orders/{order_number}/cancel/ - Annulation utilisateur
PUT    /api/orders/{order_number}/update_status/ - Admin seulement
GET    /api/orders/summary/          - Résumé commandes utilisateur
GET    /api/orders/status_options/   - Options de statuts pour le frontend

💳 PAYMENT APIs (3 endpoints):
POST   /api/payments/initiate/       - Initier un paiement pour une commande
POST   /api/payments/webhook/        - Réception des notifications MonCash (public)
GET    /api/payments/{pk}/status/    - Vérifier le statut d'une transaction

🎪 LANDING PAGE APIs (8 endpoints):
GET    /api/landing-page/            - Page complète avec toutes sections
GET    /api/landing-page/header/     - Section header (logo, nav, etc.)
GET    /api/landing-page/banners/    - Carrousel bannières rotatives
GET    /api/landing-page/popular-products/ - Produits vedettes (3-6 items)
GET    /api/landing-page/content-sections/ - Sections de contenu média & texte
GET    /api/landing-page/footer/     - Footer (identité, navigation, etc.)
GET    /api/landing-page/carousel-configs/ - Configurations des carrousels
POST   /api/landing-page/refresh-cache/ - Rafraîchissement du cache (admin)

=====================================================================
📊 TOTAL APIs FONCTIONNELLES: 45 endpoints
=====================================================================
"""