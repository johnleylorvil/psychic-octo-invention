## Phase 7: URL Configuration

### Task 7: Implement Complete URL Routing System
**Priority**: Medium | **Estimated Time**: 6 hours

#### Objective
Create a comprehensive, SEO-friendly URL structure that supports the full marketplace functionality with proper namespacing and error handling.

#### Deliverables
- [ ] Main URL configuration
- [ ] App-specific URL patterns
- [ ] SEO-friendly URL structures
- [ ] API endpoint organization
- [ ] Error page routing

#### Implementation Steps

1. **Main URL Configuration**
   ```python
   # config/urls.py
   from django.contrib import admin
   from django.urls import path, include
   from django.conf import settings
   from django.conf.urls.static import static
   from django.views.generic import TemplateView
   
   urlpatterns = [
       # Admin
       path('admin/', admin.site.urls),
       
       # Authentication
       path('auth/', include('django.contrib.auth.urls')),
       
       # Main marketplace
       path('', include('marketplace.urls', namespace='marketplace')),
       
       # API endpoints
       path('api/v1/', include('marketplace.api.urls', namespace='api')),
       
       # Static pages
       path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about'),
       path('contact/', TemplateView.as_view(template_name='pages/contact.html'), name='contact'),
       path('terms/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
       path('privacy/', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
   ]
   
   # Development media serving
   if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   
   # Custom error handlers
   handler404 = 'marketplace.views.errors.handler404'
   handler500 = 'marketplace.views.errors.handler500'
   ```

2. **Marketplace URL Patterns**
   ```python
   # marketplace/urls.py
   from django.urls import path, include
   from . import views
   
   app_name = 'marketplace'
   
   urlpatterns = [
       # Homepage
       path('', views.HomePageView.as_view(), name='home'),
       
       # Product URLs
       path('produit/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
       path('produits/', views.ProductListView.as_view(), name='product_list'),
       path('recherche/', views.ProductSearchView.as_view(), name='product_search'),
       
       # Category URLs
       path('categorie/<slug:slug>/', views.CategoryListView.as_view(), name='category_list'),
       path('categories/', views.CategoryIndexView.as_view(), name='category_index'),
       
       # Specific category pages (SEO-friendly)
       path('agricole/', views.AgricultureCategoryView.as_view(), name='agriculture'),
       path('patriotiques/', views.PatrioticCategoryView.as_view(), name='patriotic'),
       path('petite-industrie/', views.SmallIndustryCategoryView.as_view(), name='small_industry'),
       path('services/', views.ServicesView.as_view(), name='services'),
       path('premiere-necessite/', views.EssentialsCategoryView.as_view(), name='essentials'),
       
       # Cart & Checkout
       path('panier/', views.CartView.as_view(), name='cart'),
       path('panier/ajouter/', views.AddToCartView.as_view(), name='add_to_cart'),
       path('panier/supprimer/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
       path('panier/vider/', views.ClearCartView.as_view(), name='clear_cart'),
       path('commande/', views.CheckoutView.as_view(), name='checkout'),
       path('commande/confirmation/<int:order_id>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
       
       # User Account
       path('compte/', include([
           path('', views.UserProfileView.as_view(), name='profile'),
           path('inscription/', views.UserRegistrationView.as_view(), name='register'),
           path('connexion/', views.UserLoginView.as_view(), name='login'),
           path('deconnexion/', views.UserLogoutView.as_view(), name='logout'),
           path('commandes/', views.OrderHistoryView.as_view(), name='order_history'),
           path('commandes/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
           path('favoris/', views.WishlistView.as_view(), name='wishlist'),
           path('devenir-vendeur/', views.SellerApplicationView.as_view(), name='become_seller'),
       ])),
       
       # Seller Dashboard
       path('vendeur/', include([
           path('', views.SellerDashboardView.as_view(), name='seller_dashboard'),
           path('produits/', views.SellerProductListView.as_view(), name='seller_products'),
           path('produits/ajouter/', views.SellerProductCreateView.as_view(), name='seller_product_create'),
           path('produits/<int:pk>/modifier/', views.SellerProductUpdateView.as_view(), name='seller_product_update'),
           path('commandes/', views.SellerOrderListView.as_view(), name='seller_orders'),
           path('commandes/<int:pk>/', views.SellerOrderDetailView.as_view(), name='seller_order_detail'),
           path('statistiques/', views.SellerAnalyticsView.as_view(), name='seller_analytics'),
       ])),
       
       # Payment Processing
       path('paiement/', include([
           path('moncash/redirect/', views.MonCashRedirectView.as_view(), name='moncash_redirect'),
           path('moncash/callback/', views.MonCashCallbackView.as_view(), name='moncash_callback'),
           path('moncash/webhook/', views.MonCashWebhookView.as_view(), name='moncash_webhook'),
       ])),
       
       # AJAX Endpoints
       path('ajax/', include([
           path('produit/<int:pk>/apercu/', views.ProductQuickViewView.as_view(), name='product_quick_view'),
           path('avis/ajouter/', views.AddReviewView.as_view(), name='add_review'),
           path('favoris/toggle/', views.ToggleWishlistView.as_view(), name='toggle_wishlist'),
           path('panier/count/', views.CartCountView.as_view(), name='cart_count'),
       ])),
   ]
   ```

3. **API URL Configuration**
   ```python
   # marketplace/api/urls.py
   from django.urls import path, include
   from rest_framework.routers import DefaultRouter
   from . import views
   
   app_name = 'api'
   
   router = DefaultRouter()
   router.register(r'products', views.ProductViewSet)
   router.register(r'categories', views.CategoryViewSet)
   router.register(r'orders', views.OrderViewSet)
   router.register(r'reviews', views.ReviewViewSet)
   
   urlpatterns = [
       # DRF Router URLs
       path('', include(router.urls)),
       
       # Authentication
       path('auth/', include([
           path('login/', views.LoginAPIView.as_view(), name='login'),
           path('register/', views.RegisterAPIView.as_view(), name='register'),
           path('refresh/', views.RefreshTokenAPIView.as_view(), name='refresh_token'),
           path('logout/', views.LogoutAPIView.as_view(), name='logout'),
       ])),
       
       # Cart Management
       path('cart/', include([
           path('', views.CartAPIView.as_view(), name='cart'),
           path('add/', views.AddToCartAPIView.as_view(), name='add_to_cart'),
           path('remove/', views.RemoveFromCartAPIView.as_view(), name='remove_from_cart'),
           path('clear/', views.ClearCartAPIView.as_view(), name='clear_cart'),
       ])),
       
       # Search & Filtering
       path('search/', views.ProductSearchAPIView.as_view(), name='search'),
       path('autocomplete/', views.SearchAutocompleteAPIView.as_view(), name='autocomplete'),
       
       # MonCash Integration
       path('payments/', include([
           path('create/', views.CreatePaymentAPIView.as_view(), name='create_payment'),
           path('verify/', views.VerifyPaymentAPIView.as_view(), name='verify_payment'),
           path('webhook/', views.PaymentWebhookAPIView.as_view(), name='payment_webhook'),
       ])),
       
       # Analytics & Reporting
       path('analytics/', include([
           path('popular-products/', views.PopularProductsAPIView.as_view(), name='popular_products'),
           path('sales-stats/', views.SalesStatsAPIView.as_view(), name='sales_stats'),
       ])),
   ]
   ```

4. **SEO-Optimized URL Patterns**
   ```python
   # marketplace/seo_urls.py
   """
   Additional SEO-friendly URL patterns for better search engine optimization
   """
   from django.urls import path
   from . import views
   
   seo_urlpatterns = [
       # Location-specific URLs
       path('port-au-prince/', views.LocationView.as_view(), {'location': 'port-au-prince'}, name='port_au_prince'),
       path('cap-haitien/', views.LocationView.as_view(), {'location': 'cap-haitien'}, name='cap_haitien'),
       
       # Seasonal/promotional URLs
       path('nouveautes/', views.NewProductsView.as_view(), name='new_products'),
       path('promotions/', views.PromotionsView.as_view(), name='promotions'),
       path('meilleures-ventes/', views.BestSellersView.as_view(), name='best_sellers'),
       
       # Content marketing URLs
       path('blog/', views.BlogIndexView.as_view(), name='blog_index'),
       path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
       path('guides/', views.GuideIndexView.as_view(), name='guide_index'),
       path('guides/<slug:slug>/', views.GuideDetailView.as_view(), name='guide_detail'),
       
       # Seller profiles (public)
       path('boutique/<slug:seller_slug>/', views.SellerPublicProfileView.as_view(), name='seller_profile'),
       path('boutiques/', views.SellerDirectoryView.as_view(), name='seller_directory'),
   ]
   ```

5. **Error Handler Views**
   ```python
   # marketplace/views/errors.py
   from django.shortcuts import render
   from django.http import HttpResponseNotFound, HttpResponseServerError
   
   def handler404(request, exception):
       """Custom 404 error handler"""
       context = {
           'error_code': '404',
           'error_message': 'Page non trouvée',
           'error_description': 'La page que vous recherchez n\'existe pas ou a été déplacée.',
           'suggested_actions': [
               'Retourner à l\'accueil',
               'Rechercher des produits',
               'Parcourir les catégories',
           ]
       }
       return render(request, 'errors/404.html', context, status=404)
   
   def handler500(request):
       """Custom 500 error handler"""
       context = {
           'error_code': '500',
           'error_message': 'Erreur du serveur',
           'error_description': 'Une erreur inattendue s\'est produite. Notre équipe technique a été notifiée.',
           'suggested_actions': [
               'Actualiser la page',
               'Réessayer plus tard',
               'Contacter le support',
           ]
       }
       return render(request, 'errors/500.html', context, status=500)
   ```

#### Acceptance Criteria
- [ ] All URLs follow SEO-friendly patterns
- [ ] Proper namespacing implemented
- [ ] API endpoints organized logically
- [ ] Error handling provides helpful user experience
- [ ] URL patterns support internationalization
- [ ] No broken or conflicting URL patterns

---