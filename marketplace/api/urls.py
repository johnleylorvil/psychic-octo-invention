"""
Afèpanou Marketplace - API URL Configuration (v1)
RESTful API endpoints for mobile app and frontend JavaScript consumption
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Import API viewsets when they're implemented
# from .viewsets import (
#     ProductViewSet, CategoryViewSet, OrderViewSet,
#     UserViewSet, ReviewViewSet, CartViewSet
# )

# Import API views when they're implemented
# from .views import (
#     ProductListAPIView, ProductDetailAPIView,
#     CategoryListAPIView, UserProfileAPIView,
#     CartAPIView, OrderAPIView
# )

app_name = 'api_v1'

# DRF Router for ViewSets (when implemented)
router = DefaultRouter()
# router.register(r'products', ProductViewSet)
# router.register(r'categories', CategoryViewSet)
# router.register(r'orders', OrderViewSet)
# router.register(r'reviews', ReviewViewSet)
# router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    # ===== AUTHENTICATION ENDPOINTS =====
    path('auth/', include([
        # JWT Authentication
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
        
        # User authentication (when implemented)
        # path('register/', UserRegisterAPIView.as_view(), name='api_register'),
        # path('login/', UserLoginAPIView.as_view(), name='api_login'),
        # path('logout/', UserLogoutAPIView.as_view(), name='api_logout'),
        # path('profile/', UserProfileAPIView.as_view(), name='api_profile'),
        # path('change-password/', ChangePasswordAPIView.as_view(), name='api_change_password'),
    ])),
    
    # ===== PRODUCT CATALOG API =====
    path('products/', include([
        # Product endpoints (when implemented)
        # path('', ProductListAPIView.as_view(), name='api_product_list'),
        # path('<int:pk>/', ProductDetailAPIView.as_view(), name='api_product_detail'),
        # path('search/', ProductSearchAPIView.as_view(), name='api_product_search'),
        # path('featured/', FeaturedProductsAPIView.as_view(), name='api_featured_products'),
        # path('related/<int:product_id>/', RelatedProductsAPIView.as_view(), name='api_related_products'),
    ])),
    
    path('categories/', include([
        # Category endpoints (when implemented)
        # path('', CategoryListAPIView.as_view(), name='api_category_list'),
        # path('<int:pk>/', CategoryDetailAPIView.as_view(), name='api_category_detail'),
        # path('<int:category_id>/products/', CategoryProductsAPIView.as_view(), name='api_category_products'),
        # path('tree/', CategoryTreeAPIView.as_view(), name='api_category_tree'),
    ])),
    
    # ===== SHOPPING CART API =====
    path('cart/', include([
        # Cart management (when implemented)
        # path('', CartAPIView.as_view(), name='api_cart'),
        # path('add/', AddToCartAPIView.as_view(), name='api_cart_add'),
        # path('update/', UpdateCartAPIView.as_view(), name='api_cart_update'),
        # path('remove/', RemoveFromCartAPIView.as_view(), name='api_cart_remove'),
        # path('clear/', ClearCartAPIView.as_view(), name='api_cart_clear'),
        # path('summary/', CartSummaryAPIView.as_view(), name='api_cart_summary'),
    ])),
    
    # ===== ORDER MANAGEMENT API =====
    path('orders/', include([
        # Order endpoints (when implemented)
        # path('', OrderListAPIView.as_view(), name='api_order_list'),
        # path('<int:pk>/', OrderDetailAPIView.as_view(), name='api_order_detail'),
        # path('create/', CreateOrderAPIView.as_view(), name='api_order_create'),
        # path('<int:order_id>/cancel/', CancelOrderAPIView.as_view(), name='api_order_cancel'),
        # path('<int:order_id>/track/', TrackOrderAPIView.as_view(), name='api_order_track'),
    ])),
    
    # ===== PAYMENT API =====
    path('payments/', include([
        # Payment processing (when implemented)
        # path('initiate/', InitiatePaymentAPIView.as_view(), name='api_payment_initiate'),
        # path('verify/', VerifyPaymentAPIView.as_view(), name='api_payment_verify'),
        # path('status/<str:transaction_id>/', PaymentStatusAPIView.as_view(), name='api_payment_status'),
        # path('history/', PaymentHistoryAPIView.as_view(), name='api_payment_history'),
        
        # MonCash specific endpoints
        path('moncash/', include([
            # path('create/', MonCashCreatePaymentAPIView.as_view(), name='api_moncash_create'),
            # path('callback/', MonCashCallbackAPIView.as_view(), name='api_moncash_callback'),
            # path('webhook/', MonCashWebhookAPIView.as_view(), name='api_moncash_webhook'),
        ])),
    ])),
    
    # ===== REVIEW SYSTEM API =====
    path('reviews/', include([
        # Review management (when implemented)
        # path('', ReviewListAPIView.as_view(), name='api_review_list'),
        # path('<int:pk>/', ReviewDetailAPIView.as_view(), name='api_review_detail'),
        # path('create/', CreateReviewAPIView.as_view(), name='api_review_create'),
        # path('product/<int:product_id>/', ProductReviewsAPIView.as_view(), name='api_product_reviews'),
        # path('<int:review_id>/update/', UpdateReviewAPIView.as_view(), name='api_review_update'),
        # path('<int:review_id>/delete/', DeleteReviewAPIView.as_view(), name='api_review_delete'),
    ])),
    
    # ===== USER MANAGEMENT API =====
    path('users/', include([
        # User profile and management (when implemented)
        # path('profile/', UserProfileAPIView.as_view(), name='api_user_profile'),
        # path('profile/update/', UpdateProfileAPIView.as_view(), name='api_update_profile'),
        # path('addresses/', AddressListAPIView.as_view(), name='api_address_list'),
        # path('addresses/create/', CreateAddressAPIView.as_view(), name='api_address_create'),
        # path('addresses/<int:address_id>/', AddressDetailAPIView.as_view(), name='api_address_detail'),
        # path('wishlist/', WishlistAPIView.as_view(), name='api_wishlist'),
        # path('wishlist/toggle/', ToggleWishlistAPIView.as_view(), name='api_toggle_wishlist'),
    ])),
    
    # ===== SELLER API =====
    path('seller/', include([
        # Seller dashboard and management (when implemented)
        # path('dashboard/', SellerDashboardAPIView.as_view(), name='api_seller_dashboard'),
        # path('products/', SellerProductListAPIView.as_view(), name='api_seller_products'),
        # path('products/create/', CreateSellerProductAPIView.as_view(), name='api_seller_product_create'),
        # path('products/<int:product_id>/', SellerProductDetailAPIView.as_view(), name='api_seller_product_detail'),
        # path('orders/', SellerOrderListAPIView.as_view(), name='api_seller_orders'),
        # path('orders/<int:order_id>/', SellerOrderDetailAPIView.as_view(), name='api_seller_order_detail'),
        # path('analytics/', SellerAnalyticsAPIView.as_view(), name='api_seller_analytics'),
    ])),
    
    # ===== SEARCH & FILTERING API =====
    path('search/', include([
        # Search endpoints (when implemented)
        # path('products/', ProductSearchAPIView.as_view(), name='api_search_products'),
        # path('suggestions/', SearchSuggestionsAPIView.as_view(), name='api_search_suggestions'),
        # path('autocomplete/', AutocompleteAPIView.as_view(), name='api_autocomplete'),
        # path('filters/', SearchFiltersAPIView.as_view(), name='api_search_filters'),
    ])),
    
    # ===== UTILITY ENDPOINTS =====
    path('utils/', include([
        # Utility endpoints (when implemented)
        # path('validate-address/', ValidateAddressAPIView.as_view(), name='api_validate_address'),
        # path('shipping-rates/', ShippingRatesAPIView.as_view(), name='api_shipping_rates'),
        # path('currency-rates/', CurrencyRatesAPIView.as_view(), name='api_currency_rates'),
        # path('system-status/', SystemStatusAPIView.as_view(), name='api_system_status'),
    ])),
]

# Include router URLs (when ViewSets are implemented)
# urlpatterns += router.urls

# API documentation endpoints (when implemented)
urlpatterns += [
    # path('docs/', APIDocumentationView.as_view(), name='api_docs'),
    # path('schema/', APISchemaView.as_view(), name='api_schema'),
]