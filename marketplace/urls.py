"""
Afèpanou Marketplace - URL Configuration
SEO-friendly, comprehensive URL patterns for the Haitian e-commerce marketplace
Organized by functional areas with proper namespacing and French-friendly paths
"""
from django.urls import path, include, re_path
from django.views.generic import TemplateView

# Import views from different modules
from .views import pages, auth, seller, checkout, payment, ajax

app_name = 'marketplace'

urlpatterns = [
    # ===== HOMEPAGE & MAIN PAGES =====
    path('', pages.HomePageView.as_view(), name='home'),
    path('apropos/', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='pages/contact.html'), name='contact'),
    path('conditions/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
    path('confidentialite/', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
    
    # ===== PRODUCT CATALOG =====
    # Product detail with SEO-friendly slugs
    path('produit/<slug:slug>/', pages.ProductDetailView.as_view(), name='product_detail'),
    
    # Category hierarchy with SEO-friendly French names
    path('categorie/<slug:slug>/', pages.CategoryListView.as_view(), name='category_list'),
    path('categories/', pages.CategoryListView.as_view(), name='category_index'),
    
    # Haitian-specific categories (SEO-optimized)
    path('agricole/', pages.CategoryListView.as_view(), 
         {'category_slug': 'agricole'}, name='category_agricole'),
    path('artisanat/', pages.CategoryListView.as_view(), 
         {'category_slug': 'artisanat'}, name='category_artisanat'),
    path('mode/', pages.CategoryListView.as_view(), 
         {'category_slug': 'mode'}, name='category_mode'),
    path('services/', pages.CategoryListView.as_view(), 
         {'category_slug': 'services'}, name='category_services'),
    path('technologie/', pages.CategoryListView.as_view(), 
         {'category_slug': 'technologie'}, name='category_technologie'),
    
    # Search functionality
    path('recherche/', pages.ProductSearchView.as_view(), name='product_search'),
    path('recherche/avancee/', pages.ProductSearchView.as_view(), 
         {'advanced': True}, name='advanced_search'),
    
    # ===== USER AUTHENTICATION & ACCOUNTS =====
    path('compte/', include([
        # Registration and login (French paths)
        path('inscription/', auth.UserRegistrationView.as_view(), name='register'),
        path('connexion/', auth.user_login_view, name='login'),
        path('deconnexion/', auth.UserLogoutView.as_view(), name='logout'),
        
        # Profile management
        path('profil/', auth.profile_view, name='profile'),
        path('profil/modifier/', auth.profile_view, name='profile_edit'),
        
        # Password management
        path('mot-de-passe/oublie/', auth.password_reset_request, name='password_reset'),
        path('mot-de-passe/confirmer/', auth.password_reset_confirm, name='password_reset_confirm'),
        
        # Email verification
        path('email/verification/', auth.email_verification, name='email_verification'),
        path('email/confirmer/<str:token>/', auth.email_confirmation, name='email_confirm'),
        
        # Address management
        path('adresses/', auth.address_book, name='address_book'),
        path('adresses/ajouter/', auth.add_address, name='add_address'),
        path('adresses/<int:address_id>/modifier/', auth.edit_address, name='edit_address'),
        
        # Wishlist
        path('favoris/', pages.wishlist_view, name='wishlist'),
        path('favoris/ajouter/', ajax.toggle_wishlist_ajax, name='add_to_wishlist'),
    ])),
    
    # ===== SHOPPING CART & CHECKOUT =====
    path('panier/', include([
        path('', pages.cart_view, name='cart'),
        path('ajouter/', pages.add_to_cart, name='add_to_cart'),
        path('modifier/', pages.update_cart_item, name='update_cart'),
        path('supprimer/', pages.remove_from_cart, name='remove_from_cart'),
        path('vider/', pages.clear_cart, name='clear_cart'),
    ])),
    
    # Checkout process (French paths)
    path('commande/', include([
        path('', checkout.checkout_view, name='checkout'),
        path('livraison/', checkout.checkout_shipping, name='checkout_shipping'),
        path('paiement/', checkout.checkout_payment, name='checkout_payment'),
        path('confirmation/', checkout.OrderConfirmationView.as_view(), name='order_confirmation'),
        path('succes/', checkout.checkout_success, name='checkout_success'),
        path('erreur/', checkout.checkout_error, name='checkout_error'),
    ])),
    
    # ===== ORDER MANAGEMENT =====
    path('commandes/', include([
        path('', pages.OrderHistoryView.as_view(), name='order_history'),
        path('<int:order_id>/', pages.OrderDetailView.as_view(), name='order_detail'),
        path('<int:order_id>/facture/', pages.order_invoice, name='order_invoice'),
        path('<int:order_id>/suivi/', pages.order_tracking, name='order_tracking'),
        path('<int:order_id>/annuler/', pages.cancel_order, name='cancel_order'),
    ])),
    
    # ===== SELLER AREA =====
    path('vendeur/', include([
        # Seller application and dashboard
        path('inscription/', auth.BecomeSellerView.as_view(), name='become_seller'),
        path('tableau-de-bord/', seller.SellerDashboardView.as_view(), name='seller_dashboard'),
        
        # Product management
        path('produits/', include([
            path('', seller.SellerProductListView.as_view(), name='seller_products'),
            path('ajouter/', seller.SellerProductCreateView.as_view(), name='seller_add_product'),
            path('<int:product_id>/', seller.SellerProductDetailView.as_view(), name='seller_product_detail'),
            path('<int:product_id>/modifier/', seller.SellerProductUpdateView.as_view(), name='seller_edit_product'),
            path('<int:product_id>/supprimer/', seller.SellerProductDeleteView.as_view(), name='seller_delete_product'),
            path('actions-groupees/', seller.bulk_product_actions, name='bulk_product_actions'),
        ])),
        
        # Order management
        path('commandes/', include([
            path('', seller.SellerOrderListView.as_view(), name='seller_orders'),
            path('<int:order_id>/', seller.SellerOrderDetailView.as_view(), name='seller_order_detail'),
            path('<int:order_id>/traiter/', seller.process_order, name='seller_process_order'),
            path('<int:order_id>/expedier/', seller.ship_order, name='seller_ship_order'),
        ])),
        
        # Analytics and reports
        path('analytique/', seller.SellerAnalyticsView.as_view(), name='seller_analytics'),
        path('rapports/', seller.seller_reports, name='seller_reports'),
        path('profil/', seller.seller_profile, name='seller_profile'),
    ])),
    
    # ===== REVIEWS & RATINGS =====
    path('avis/', include([
        path('ajouter/<int:product_id>/', pages.AddReviewView.as_view(), name='add_review'),
        path('<int:review_id>/modifier/', pages.edit_review, name='edit_review'),
        path('<int:review_id>/supprimer/', pages.delete_review, name='delete_review'),
        path('produit/<int:product_id>/', pages.product_reviews, name='product_reviews'),
    ])),
    
    # ===== PAYMENT PROCESSING =====
    path('paiement/', include([
        # MonCash integration
        path('moncash/', include([
            path('initier/', payment.payment_initiate, name='moncash_payment'),
            path('callback/', payment.payment_success, name='moncash_callback'),
            path('webhook/', payment.payment_webhook, name='moncash_webhook'),
            path('verifier/', payment.payment_status_check, name='payment_status_check'),
        ])),
        
        # Cash on Delivery
        path('livraison-paiement/', payment.cod_payment, name='cod_payment'),
        
        # Payment history
        path('historique/', payment.payment_history, name='payment_history'),
        path('facture/<int:transaction_id>/', payment.payment_invoice, name='payment_invoice'),
        path('remboursement/<int:transaction_id>/', payment.request_refund, name='request_refund'),
    ])),
    
    # ===== AJAX ENDPOINTS =====
    path('ajax/', include([
        # Product interactions
        path('recherche/', ajax.search_autocomplete_ajax, name='ajax_search_autocomplete'),
        path('produit/apercu/', ajax.product_quick_view_ajax, name='ajax_product_quick_view'),
        path('produit/filtre/', ajax.product_filter_ajax, name='ajax_product_filter'),
        
        # Cart operations
        path('panier/ajouter/', ajax.add_to_cart_ajax, name='ajax_add_to_cart'),
        path('panier/modifier/', ajax.update_cart_ajax, name='ajax_update_cart'),
        path('panier/supprimer/', ajax.remove_from_cart_ajax, name='ajax_remove_from_cart'),
        path('panier/resume/', ajax.get_cart_summary_ajax, name='ajax_cart_summary'),
        
        # Wishlist
        path('favoris/basculer/', ajax.toggle_wishlist_ajax, name='ajax_toggle_wishlist'),
        
        # Form validation
        path('validation/<str:form_type>/', ajax.validate_form_field_ajax, name='ajax_validate_field'),
        
        # Location services
        path('adresse/valider/', ajax.validate_address_ajax, name='ajax_validate_address'),
        
        # Real-time updates
        path('notifications/', ajax.get_notifications_ajax, name='ajax_notifications'),
        path('stock/verifier/', ajax.check_stock_ajax, name='ajax_check_stock'),
    ])),
    
    # ===== PUBLIC VENDOR PROFILES =====
    path('boutique/<slug:vendor_slug>/', pages.vendor_profile, name='vendor_profile'),
    path('boutique/<slug:vendor_slug>/produits/', pages.vendor_products, name='vendor_products'),
    
    # ===== LOCATION-SPECIFIC PAGES (Haiti cities) =====
    path('port-au-prince/', pages.city_products, {'city': 'port-au-prince'}, name='products_port_au_prince'),
    path('cap-haitien/', pages.city_products, {'city': 'cap-haitien'}, name='products_cap_haitien'),
    path('gonaives/', pages.city_products, {'city': 'gonaives'}, name='products_gonaives'),
    path('les-cayes/', pages.city_products, {'city': 'les-cayes'}, name='products_les_cayes'),
    
    # ===== CONTENT MARKETING =====
    path('blog/', TemplateView.as_view(template_name='blog/index.html'), name='blog_index'),
    path('guides/', TemplateView.as_view(template_name='guides/index.html'), name='guides_index'),
    path('nouveautes/', pages.new_products, name='new_products'),
    path('promotions/', pages.featured_promotions, name='promotions'),
]

# Add dynamic category URLs using regex for flexibility
urlpatterns += [
    # Catch-all pattern for dynamic categories and subcategories
    re_path(r'^c/(?P<path>[\w/-]+)/$', pages.CategoryListView.as_view(), name='dynamic_category'),
    
    # Brand pages (if implementing brand filtering)
    re_path(r'^marque/(?P<brand_slug>[\w-]+)/$', pages.brand_products, name='brand_products'),
]