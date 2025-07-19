# marketplace/serializers/landing.py
from rest_framework import serializers
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Q
from ..models import (
    Banner, MediaContentSection, Page, SiteSetting, 
    Category, Product, ProductImage, User
)

# ============= HEADER SECTION SERIALIZERS =============

class HeaderCategoryButtonSerializer(serializers.ModelSerializer):
    """Serializer pour les 3 boutons catégories du header"""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'icon', 'products_count', 
            'sort_order', 'banner_image'
        ]
    
    def get_products_count(self, obj):
        """Compte les produits actifs dans la catégorie"""
        return obj.products.filter(is_active=True, stock_quantity__gt=0).count()

class HeaderConfigSerializer(serializers.Serializer):
    """Configuration complète du header"""
    logo = serializers.SerializerMethodField()
    search_config = serializers.SerializerMethodField()
    category_buttons = serializers.SerializerMethodField()
    account_button = serializers.SerializerMethodField()
    cart_button = serializers.SerializerMethodField()
    
    def get_logo(self, obj):
        """Récupère le logo du site"""
        try:
            logo_setting = SiteSetting.objects.get(setting_key='site_logo')
            return logo_setting.setting_value
        except SiteSetting.DoesNotExist:
            return "/static/images/logo-afepanou.png"
    
    def get_search_config(self, obj):
        """Configuration du champ de recherche"""
        return {
            "placeholder": "Rechercher produits haïtiens...",
            "suggestions_endpoint": "/api/products/search/",
            "min_chars": 2,
            "max_suggestions": 5
        }
    
    def get_category_buttons(self, obj):
        """3 catégories featured pour navigation principale"""
        categories = Category.objects.filter(
            is_featured=True, 
            is_active=True
        ).order_by('sort_order')[:3]
        
        return HeaderCategoryButtonSerializer(categories, many=True).data
    
    def get_account_button(self, obj):
        """Configuration bouton compte utilisateur"""
        return {
            "login_url": "/api/auth/login/",
            "register_url": "/api/auth/register/",
            "profile_url": "/api/auth/profile/",
            "logout_url": "/api/auth/logout/"
        }
    
    def get_cart_button(self, obj):
        """Configuration bouton panier - sera étendu avec état réel"""
        return {
            "items_count": 0,  # À connecter avec session/user cart
            "total_amount": "0.00",
            "currency": "HTG",
            "cart_url": "/api/cart/",
            "checkout_url": "/api/checkout/"
        }

# ============= BANNER SECTION SERIALIZERS =============

class BannerCarouselSerializer(serializers.ModelSerializer):
    """Serializer pour chaque bannière du carrousel"""
    is_valid_period = serializers.SerializerMethodField()
    
    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'subtitle', 'description', 'image_url', 
            'mobile_image_url', 'link_url', 'button_text', 'button_color',
            'text_color', 'overlay_opacity', 'sort_order', 'click_count',
            'is_valid_period'
        ]
    
    def get_is_valid_period(self, obj):
        """Vérifie si la bannière est dans sa période de validité"""
        now = timezone.now().date()
        
        if obj.start_date and obj.start_date > now:
            return False
        if obj.end_date and obj.end_date < now:
            return False
        return True

class BannerSectionSerializer(serializers.Serializer):
    """Section bannière complète avec configuration carrousel"""
    auto_rotation = serializers.SerializerMethodField()
    rotation_interval = serializers.SerializerMethodField()
    transition_effect = serializers.SerializerMethodField()
    navigation_dots = serializers.SerializerMethodField()
    banners = serializers.SerializerMethodField()
    total_banners = serializers.SerializerMethodField()
    active_banners = serializers.SerializerMethodField()
    
    def get_auto_rotation(self, obj):
        """Configuration rotation automatique"""
        try:
            setting = SiteSetting.objects.get(setting_key='banner_auto_rotation')
            return setting.setting_value.lower() == 'true'
        except SiteSetting.DoesNotExist:
            return True
    
    def get_rotation_interval(self, obj):
        """Intervalle de rotation en millisecondes"""
        try:
            setting = SiteSetting.objects.get(setting_key='banner_rotation_interval')
            return int(setting.setting_value)
        except (SiteSetting.DoesNotExist, ValueError):
            return 5000
    
    def get_transition_effect(self, obj):
        """Effet de transition"""
        try:
            setting = SiteSetting.objects.get(setting_key='banner_transition_effect')
            return setting.setting_value
        except SiteSetting.DoesNotExist:
            return "fade"
    
    def get_navigation_dots(self, obj):
        """Affichage des points de navigation"""
        return True
    
    def get_banners(self, obj):
        """Liste des bannières actives triées"""
        banners = Banner.objects.filter(is_active=True).order_by('sort_order')
        return BannerCarouselSerializer(banners, many=True).data
    
    def get_total_banners(self, obj):
        """Nombre total de bannières"""
        return Banner.objects.count()
    
    def get_active_banners(self, obj):
        """Nombre de bannières actives"""
        return Banner.objects.filter(is_active=True).count()

# ============= POPULAR PRODUCTS SECTION SERIALIZERS =============

class PopularProductImageSerializer(serializers.ModelSerializer):
    """Images pour produits vedettes"""
    class Meta:
        model = ProductImage
        fields = ['image_url', 'alt_text', 'is_primary']

class PopularProductCategorySerializer(serializers.ModelSerializer):
    """Catégorie simplifiée pour produits vedettes"""
    class Meta:
        model = Category
        fields = ['name', 'slug']

class PopularProductSerializer(serializers.ModelSerializer):
    """Serializer optimisé pour produits vedettes"""
    current_price = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()
    primary_image = serializers.SerializerMethodField()
    category = PopularProductCategorySerializer(read_only=True)
    featured_badge = serializers.SerializerMethodField()
    quick_add_enabled = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'current_price',
            'promotional_price', 'price', 'in_stock', 'stock_quantity',
            'primary_image', 'category', 'is_featured', 'featured_badge',
            'quick_add_enabled', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Image principale du produit"""
        primary_img = obj.images.filter(is_primary=True).first()
        if primary_img:
            return PopularProductImageSerializer(primary_img).data
        
        # Fallback vers première image disponible
        first_img = obj.images.first()
        if first_img:
            return PopularProductImageSerializer(first_img).data
        return None
    
    def get_featured_badge(self, obj):
        """Badge à afficher sur le produit vedette"""
        if obj.promotional_price:
            discount_percent = int(((obj.price - obj.promotional_price) / obj.price) * 100)
            return f"-{discount_percent}%"
        
        # Produit récent (moins de 30 jours)
        if obj.created_at and (timezone.now() - obj.created_at).days <= 30:
            return "Nouveau"
        
        if obj.stock_quantity and obj.stock_quantity <= obj.min_stock_alert:
            return "Stock limité"
        
        return None
    
    def get_quick_add_enabled(self, obj):
        """Permet ajout rapide au panier"""
        return obj.in_stock and not obj.is_digital

class PopularProductsSectionSerializer(serializers.Serializer):
    """Section produits vedettes complète"""
    section_title = serializers.SerializerMethodField()
    display_mode = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    view_all_url = serializers.SerializerMethodField()
    total_featured = serializers.SerializerMethodField()
    
    def get_section_title(self, obj):
        """Titre de la section"""
        try:
            setting = SiteSetting.objects.get(setting_key='featured_products_title')
            return setting.setting_value
        except SiteSetting.DoesNotExist:
            return "Produits Vedettes"
    
    def get_display_mode(self, obj):
        """Mode d'affichage des produits"""
        return "grid_4x2"  # 4 colonnes, 2 rangées max
    
    def get_products(self, obj):
        """3-6 produits vedettes selon design guideline"""
        products = Product.objects.filter(
            is_featured=True,
            is_active=True,
            stock_quantity__gt=0
        ).select_related('category').prefetch_related('images').order_by('-created_at')[:6]
        
        return PopularProductSerializer(products, many=True).data
    
    def get_view_all_url(self, obj):
        """URL pour voir tous les produits vedettes"""
        return "/api/products/?featured=true"
    
    def get_total_featured(self, obj):
        """Nombre total de produits vedettes"""
        return Product.objects.filter(is_featured=True, is_active=True).count()

# ============= MEDIA CONTENT SECTION SERIALIZERS =============

class MediaContentSectionSerializer(serializers.ModelSerializer):
    """Serializer pour sections de contenu média"""
    category_tags_list = serializers.SerializerMethodField()
    product_tags_list = serializers.SerializerMethodField()
    associated_products_count = serializers.SerializerMethodField()
    shopping_redirect = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaContentSection
        fields = [
            'id', 'title', 'subtitle', 'description', 'detailed_description',
            'image_url', 'button_text', 'button_link', 'category_tags',
            'product_tags', 'layout_type', 'background_color', 'text_color',
            'sort_order', 'category_tags_list', 'product_tags_list',
            'associated_products_count', 'shopping_redirect'
        ]
    
    def get_category_tags_list(self, obj):
        """Liste des catégories associées"""
        if not obj.category_tags:
            return []
        
        try:
            category_ids = [int(id.strip()) for id in obj.category_tags.split(',')]
            categories = Category.objects.filter(id__in=category_ids, is_active=True)
            return [{'id': cat.id, 'name': cat.name, 'slug': cat.slug} for cat in categories]
        except (ValueError, TypeError):
            return []
    
    def get_product_tags_list(self, obj):
        """Liste des tags produits"""
        if not obj.product_tags:
            return []
        return [tag.strip() for tag in obj.product_tags.split(',')]
    
    def get_associated_products_count(self, obj):
        """Nombre de produits associés à cette section"""
        if obj.category_tags:
            try:
                category_ids = [int(id.strip()) for id in obj.category_tags.split(',')]
                return Product.objects.filter(
                    category_id__in=category_ids,
                    is_active=True,
                    stock_quantity__gt=0
                ).count()
            except (ValueError, TypeError):
                pass
        return 0
    
    def get_shopping_redirect(self, obj):
        """Configuration de redirection du bouton shopping"""
        if obj.category_tags:
            try:
                category_ids = [int(id.strip()) for id in obj.category_tags.split(',')]
                if len(category_ids) == 1:
                    category = Category.objects.filter(id=category_ids[0]).first()
                    if category:
                        return {
                            "type": "category",
                            "target": category.slug,
                            "url": f"/api/categories/{category.slug}/products/",
                            "filter_applied": True
                        }
                else:
                    return {
                        "type": "multi_category",
                        "target": "mixed",
                        "url": f"/api/products/?categories={','.join(map(str, category_ids))}",
                        "filter_applied": True
                    }
            except (ValueError, TypeError):
                pass
        
        return {
            "type": "general",
            "target": "all_products", 
            "url": "/api/products/",
            "filter_applied": False
        }

class ContentSectionsSerializer(serializers.Serializer):
    """Ensemble des sections de contenu média"""
    total_sections = serializers.SerializerMethodField()
    active_sections = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()
    initial_content_list = serializers.SerializerMethodField()
    
    def get_total_sections(self, obj):
        """Nombre total de sections"""
        return MediaContentSection.objects.count()
    
    def get_active_sections(self, obj):
        """Nombre de sections actives"""
        return MediaContentSection.objects.filter(is_active=True).count()
    
    def get_sections(self, obj):
        """Sections actives triées"""
        sections = MediaContentSection.objects.filter(
            is_active=True
        ).order_by('sort_order')
        
        return MediaContentSectionSerializer(sections, many=True).data
    
    def get_initial_content_list(self, obj):
        """Liste initiale du contenu selon design guidelines"""
        return [
            "Produits de Premiere Necessite",
            "Produits Patriotiques", 
            "Produits Locales",
            "Artisanats",
            "Petite industrie",
            "Production Agricole",
            "Services Divers"
        ]

# ============= FOOTER SECTION SERIALIZERS =============

class FooterPageSerializer(serializers.ModelSerializer):
    """Pages pour le footer"""
    content_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Page
        fields = ['title', 'slug', 'content_preview', 'sort_order']
    
    def get_content_preview(self, obj):
        """Aperçu du contenu (premiers 100 caractères)"""
        if obj.content:
            return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
        return obj.excerpt or ""

class FooterSectionSerializer(serializers.Serializer):
    """Section footer complète"""
    identity_section = serializers.SerializerMethodField()
    navigation_links = serializers.SerializerMethodField()
    public_settings = serializers.SerializerMethodField()
    
    def get_identity_section(self, obj):
        """Informations d'identité du site"""
        site_name = self._get_setting('site_name', 'Afèpanou')
        tagline = self._get_setting('site_tagline', 'Marketplace Haïtien')
        
        # Mission depuis page ou setting
        mission = ""
        try:
            mission_page = Page.objects.get(slug='notre-mission')
            mission = mission_page.content[:200] + "..." if mission_page.content else ""
        except Page.DoesNotExist:
            mission = self._get_setting('site_mission', 'Créer un écosystème économique durable en Haïti...')
        
        return {
            "site_name": site_name,
            "tagline": tagline,
            "mission_statement": mission,
            "logo_footer": self._get_setting('footer_logo', '/static/images/logo-footer.png')
        }
    
    def get_navigation_links(self, obj):
        """Liens de navigation organisés par catégorie"""
        
        # Pages À propos
        about_pages = Page.objects.filter(
            slug__in=['notre-mission', 'notre-histoire'],
            is_active=True
        ).order_by('sort_order')
        
        # Pages vendeurs
        seller_pages = Page.objects.filter(
            slug__in=['devenir-vendeur', 'support-vendeurs'],
            is_active=True
        ).order_by('sort_order')
        
        # Pages légales
        legal_pages = Page.objects.filter(
            slug__in=['politique-confidentialite', 'conditions-utilisation', 'mentions-legales'],
            is_active=True
        ).order_by('sort_order')
        
        return {
            "about": FooterPageSerializer(about_pages, many=True).data,
            "sellers": FooterPageSerializer(seller_pages, many=True).data,
            "legal": FooterPageSerializer(legal_pages, many=True).data
        }
    
    def get_public_settings(self, obj):
        """Paramètres publics du site"""
        return {
            "contact_email": self._get_setting('contact_email', 'contact@afepanou.com'),
            "support_phone": self._get_setting('support_phone', '+509 1234-5678'),
            "default_currency": self._get_setting('default_currency', 'HTG'),
            "business_hours": self._get_setting('business_hours', '9h-17h (GMT-5)'),
            "social_media": {
                "facebook": self._get_setting('facebook_url', ''),
                "instagram": self._get_setting('instagram_url', ''),
                "twitter": self._get_setting('twitter_url', '')
            }
        }
    
    def _get_setting(self, key, default=''):
        """Utilitaire pour récupérer un setting"""
        try:
            setting = SiteSetting.objects.get(setting_key=key)
            return setting.setting_value or default
        except SiteSetting.DoesNotExist:
            return default

# ============= CARROUSEL CONFIGURATIONS =============

class CarouselConfigSerializer(serializers.Serializer):
    """Configurations pour tous les carrousels du site"""
    banners_slideshow = serializers.SerializerMethodField()
    featured_products_carousel = serializers.SerializerMethodField()
    categories_showcase = serializers.SerializerMethodField()
    
    def get_banners_slideshow(self, obj):
        """Config carrousel bannières"""
        return {
            "source": "banners",
            "auto_play": True,
            "interval": 5000,
            "show_indicators": True,
            "show_controls": True,
            "transition": "fade",
            "infinite_loop": True
        }
    
    def get_featured_products_carousel(self, obj):
        """Config carrousel produits vedettes"""
        return {
            "source": "products_featured",
            "items_per_slide": 4,
            "responsive_breakpoints": {
                "mobile": 1,
                "tablet": 2,
                "desktop": 4
            },
            "auto_play": False,
            "show_arrows": True,
            "infinite_scroll": True
        }
    
    def get_categories_showcase(self, obj):
        """Config showcase catégories"""
        return {
            "source": "categories_featured",
            "layout": "grid",
            "animation": "fade",
            "hover_effects": True,
            "show_product_count": True
        }

# ============= LANDING PAGE MASTER SERIALIZER =============

class LandingPageSerializer(serializers.Serializer):
    """Serializer maître pour toute la landing page"""
    header = HeaderConfigSerializer()
    banner_carousel = BannerSectionSerializer()
    popular_products = PopularProductsSectionSerializer()
    content_sections = ContentSectionsSerializer()
    footer = FooterSectionSerializer()
    carousel_configs = CarouselConfigSerializer()
    metadata = serializers.SerializerMethodField()
    
    def get_metadata(self, obj):
        """Métadonnées de la page"""
        return {
            "total_sections": 5,
            "cache_ttl": 300,  # 5 minutes
            "last_updated": timezone.now().isoformat(),
            "admin_editable": True,
            "version": "1.0",
            "responsive": True,
            "supported_devices": ["mobile", "tablet", "desktop"]
        }