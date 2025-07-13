from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Panier
    path('cart/', views.get_cart, name='get-cart'),
    path('cart/add/', views.add_to_cart, name='add-to-cart'),
    path('cart/items/<int:item_id>/', views.update_cart_item, name='update-cart-item'),
    path('cart/items/<int:item_id>/remove/', views.remove_from_cart, name='remove-from-cart'),
    
    # Commandes
    path('checkout/', views.create_order, name='create-order'),
    path('', views.user_orders, name='user-orders'),
    path('<int:order_id>/', views.order_detail, name='order-detail'),
]
