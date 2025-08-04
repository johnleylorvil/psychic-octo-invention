# Dans app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # URLs principales
    path('', views.home, name='home'),
    path('store/', views.store, name='store'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # URLs pour le panier et le processus de paiement

    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success, name='success'),
    
    # Page de détail d'un produit (ex: /store/produit/mon-super-produit/)
    path('produit/<slug:slug>/', views.product_detail, name='product_detail'),

    # ==================
    # URLs pour le Panier
    # ==================
    # Page du panier (ex: /store/cart/)
    path('cart/', views.cart_detail, name='cart'),
    
    # URLs pour les actions AJAX (ne sont pas faites pour être visitées directement)
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/count/', views.get_cart_count, name='get_cart_count'),

    # URLs d'authentification
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    # 'logout' est généralement géré par Django auth, mais on peut le pointer vers une vue si besoin.

    # URLs du compte utilisateur
    path('account/', views.account, name='account'),
    path('orders/', views.orders, name='orders'),
    path('track-order/<str:order_id>/', views.track_order, name='track_order'),

    # URLs pour les pages statiques (ex: about, contact, etc.)
    # path('about/', views.about_page, name='about_us'),
    # path('contact/', views.contact_page, name='contact'),
    # path('faq/', views.faq_page, name='faq'),
    # path('legal/', views.legal_page, name='legal_mentions'),
    # path('privacy/', views.privacy_page, name='privacy_policy'),
]