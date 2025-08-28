# marketplace/urls.py
from django.urls import path, include
from . import views

# Import views from different modules
from .views import pages, auth, seller, checkout, payment, ajax

urlpatterns = [
    # Homepage
    path('', pages.HomePageView.as_view(), name='home'),
    
    # Product pages
    path('product/<slug:slug>/', pages.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:slug>/', pages.CategoryListView.as_view(), name='category_list'),
    path('search/', pages.ProductSearchView.as_view(), name='product_search'),
    
    # Authentication
    path('register/', auth.UserRegistrationView.as_view(), name='register'),
    path('login/', auth.UserLoginView.as_view(), name='login'),
    path('logout/', auth.UserLogoutView.as_view(), name='logout'),
    path('profile/', auth.UserProfileView.as_view(), name='profile'),
    path('become-seller/', auth.BecomeSellerView.as_view(), name='become_seller'),
    
    # Cart functionality
    path('cart/', pages.CartView.as_view(), name='cart'),
    path('cart/add/', pages.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/', pages.UpdateCartView.as_view(), name='update_cart'),
    path('cart/remove/', pages.RemoveFromCartView.as_view(), name='remove_from_cart'),
    
    # Checkout
    path('checkout/', checkout.CheckoutView.as_view(), name='checkout'),
    path('checkout/success/', checkout.CheckoutSuccessView.as_view(), name='checkout_success'),
    
    # Orders
    path('orders/', pages.OrderHistoryView.as_view(), name='order_history'),
    path('orders/<int:order_id>/', pages.OrderDetailView.as_view(), name='order_detail'),
    
    # Seller dashboard
    path('seller/', seller.SellerDashboardView.as_view(), name='seller_dashboard'),
    path('seller/products/', seller.SellerProductListView.as_view(), name='seller_products'),
    path('seller/products/add/', seller.SellerAddProductView.as_view(), name='seller_add_product'),
    path('seller/orders/', seller.SellerOrderListView.as_view(), name='seller_orders'),
    path('seller/orders/<int:order_id>/', seller.SellerOrderDetailView.as_view(), name='seller_order_detail'),
    path('seller/orders/update/', seller.SellerUpdateOrderView.as_view(), name='seller_update_order'),
    
    # Reviews
    path('reviews/add/<int:product_id>/', pages.AddReviewView.as_view(), name='add_review'),
    
    # AJAX endpoints
    path('ajax/search/', ajax.ProductSearchAjaxView.as_view(), name='ajax_product_search'),
    path('ajax/cart/add/', ajax.AddToCartAjaxView.as_view(), name='ajax_add_to_cart'),
    path('ajax/cart/update/', ajax.UpdateCartAjaxView.as_view(), name='ajax_update_cart'),
    
    # Payment
    path('payment/', include([
        path('moncash/', payment.MonCashPaymentView.as_view(), name='moncash_payment'),
        path('moncash/callback/', payment.MonCashCallbackView.as_view(), name='moncash_callback'),
        path('moncash/webhook/', payment.MonCashWebhookView.as_view(), name='moncash_webhook'),
    ])),
]