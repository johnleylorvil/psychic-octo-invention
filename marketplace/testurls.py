from django.urls import path
from . import testview

urlpatterns = [
    # Page d'accueil
    path('', testview.homewert, name='home'),
    
    # Store et produits
    path('store/', testview.store, name='store'),
    path('product/<slug:slug>/', testview.product_detail, name='product_detail'),
    
    # Panier
    path('cart/', testview.cart, name='cart'),
    path('cart/add/', testview.add_to_cart, name='add_to_cart'),
    path('cart/update/', testview.update_cart, name='update_cart'),
    path('cart/remove/', testview.remove_from_cart, name='remove_from_cart'),
    
    # Checkout et paiement
    path('checkout/', testview.checkout, name='checkout'),
    path('success/', testview.success, name='success'),
    
    # Commandes
    path('orders/', testview.orders, name='orders'),
    
    # ENDPOINTS MONCASH (OBLIGATOIRES)
    path('moncash/return/', testview.moncash_return, name='moncash_return'),
    path('moncash/notify/', testview.moncash_notify, name='moncash_notify'),
]