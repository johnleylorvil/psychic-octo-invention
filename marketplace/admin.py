# marketplace/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from django.utils import timezone
from .models import *

# ============= CONFIGURATION GÉNÉRALE ADMIN =============
admin.site.site_header = "🏪 Administration Afèpanou Marketplace"
admin.site.site_title = "Afèpanou Admin"
admin.site.index_title = "Tableau de bord du Marketplace Haïtien"

# ============= UTILISATEURS =============
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'email', 'full_name_display', 'phone', 
        'is_seller', 'is_active', 'is_staff', 'date_joined'
    ]
    list_filter = [
        'is_seller', 'is_active', 'is_staff', 'is_superuser', 
        'email_verified', 'gender', 'city', 'date_joined'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    list_editable = ['is_seller', 'is_active']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('📋 Informations Marketplace', {
            'fields': (
                'phone', 'address', 'city', 'country', 
                'is_seller', 'email_verified', 'profile_image'
            )
        }),
        ('👤 Informations Personnelles', {
            'fields': ('birth_date', 'gender'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('📋 Informations Marketplace', {
            'fields': ('email', 'first_name', 'last_name', 'phone', 'is_seller')
        }),
    )

    def full_name_display(self, obj):
        return obj.full_name or obj.username
    full_name_display.short_description = 'Nom complet'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

# ============= CATÉGORIES =============
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'slug', 'parent', 'products_count', 
        'is_featured', 'is_active', 'sort_order'
    ]
    list_filter = ['is_featured', 'is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured', 'is_active', 'sort_order']
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        ('📂 Informations de base', {
            'fields': ('name', 'slug', 'parent', 'description')
        }),
        ('🖼️ Images et médias', {
            'fields': ('banner_image', 'banner_image_path', 'icon', 'folder_path'),
            'classes': ('collapse',)
        }),
        ('⚙️ Paramètres', {
            'fields': ('is_featured', 'is_active', 'sort_order')
        }),
        ('🔍 SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('📝 Description détaillée', {
            'fields': ('detailed_description',),
            'classes': ('collapse',)
        })
    )

    def products_count(self, obj):
        count = obj.products.count()
        if count > 0:
            url = reverse('admin:marketplace_product_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} produit(s)</a>', url, count)
        return "0 produit"
    products_count.short_description = 'Produits'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        ).select_related('parent')

# ============= PRODUITS =============
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image_url', 'image_path', 'alt_text', 'is_primary', 'sort_order']
    ordering = ['sort_order']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'seller_name', 'price_display', 
        'stock_status', 'is_featured', 'is_active', 'created_at'
    ]
    list_filter = [
        'category', 'is_active', 'is_featured', 'condition_type',
        'origin_country', 'seller', 'created_at'
    ]
    search_fields = ['name', 'description', 'sku', 'seller__username']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured', 'is_active']
    ordering = ['-created_at']
    raw_id_fields = ['seller', 'category']
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('📦 Informations produit', {
            'fields': (
                'name', 'slug', 'category', 'seller',
                'short_description', 'description'
            )
        }),
        ('💰 Prix et stock', {
            'fields': (
                ('price', 'promotional_price'),
                ('stock_quantity', 'min_stock_alert'),
                ('cost_price', 'sku')
            )
        }),
        ('📋 Détails produit', {
            'fields': (
                ('brand', 'model', 'color'),
                ('material', 'origin_country', 'condition_type'),
                ('weight', 'dimensions'),
                'specifications', 'tags'
            ),
            'classes': ('collapse',)
        }),
        ('🚚 Livraison', {
            'fields': ('is_digital', 'requires_shipping', 'warranty_period'),
            'classes': ('collapse',)
        }),
        ('⚙️ Paramètres', {
            'fields': ('is_featured', 'is_active', 'barcode', 'video_url')
        }),
        ('🔍 SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('📝 Description détaillée', {
            'fields': ('detailed_description',),
            'classes': ('collapse',)
        })
    )

    def seller_name(self, obj):
        return obj.seller.full_name or obj.seller.username
    seller_name.short_description = 'Vendeur'

    def price_display(self, obj):
        if obj.promotional_price:
            return format_html(
                '<span style="text-decoration: line-through;">{} HTG</span><br>'
                '<strong style="color: green;">{} HTG</strong>',
                obj.price, obj.promotional_price
            )
        return f"{obj.price} HTG"
    price_display.short_description = 'Prix'

    def stock_status(self, obj):
        if obj.stock_quantity is None:
            return format_html('<span style="color: gray;">Non géré</span>')
        elif obj.stock_quantity <= 0:
            return format_html('<span style="color: red;">Rupture</span>')
        elif obj.stock_quantity <= obj.min_stock_alert:
            return format_html('<span style="color: orange;">Stock faible ({})</span>', obj.stock_quantity)
        else:
            return format_html('<span style="color: green;">En stock ({})</span>', obj.stock_quantity)
    stock_status.short_description = 'Stock'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'seller')

# ============= COMMANDES =============
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price', 'product_name', 'product_sku']
    fields = ['product', 'product_name', 'quantity', 'unit_price', 'total_price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer_name', 'user_link', 'total_amount_display',
        'status_display', 'payment_status_display', 'created_at'
    ]
    list_filter = [
        'status', 'payment_status', 'payment_method', 
        'shipping_method', 'created_at', 'shipping_city'
    ]
    search_fields = [
        'order_number', 'customer_name', 'customer_email', 
        'customer_phone', 'user__username'
    ]
    readonly_fields = [
        'order_number', 'created_at', 'updated_at', 
        'subtotal_calculated', 'total_calculated'
    ]
    ordering = ['-created_at']
    raw_id_fields = ['user']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('📋 Informations commande', {
            'fields': (
                'order_number', 'user', 'status', 'payment_status',
                'created_at', 'updated_at'
            )
        }),
        ('👤 Informations client', {
            'fields': (
                ('customer_name', 'customer_email'),
                'customer_phone'
            )
        }),
        ('📦 Adresse de livraison', {
            'fields': (
                'shipping_address', 
                ('shipping_city', 'shipping_country')
            )
        }),
        ('💰 Facturation', {
            'fields': (
                ('subtotal', 'shipping_cost'),
                ('tax_amount', 'discount_amount'),
                'total_amount', 'currency'
            )
        }),
        ('🚚 Livraison et paiement', {
            'fields': (
                ('payment_method', 'shipping_method'),
                ('tracking_number', 'estimated_delivery'),
                'delivered_at'
            )
        }),
        ('📝 Notes', {
            'fields': ('notes', 'admin_notes', 'coupon_code'),
            'classes': ('collapse',)
        })
    )

    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:marketplace_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "Invité"
    user_link.short_description = 'Utilisateur'

    def total_amount_display(self, obj):
        return f"{obj.total_amount} {obj.currency}"
    total_amount_display.short_description = 'Total'

    def status_display(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'blue',
            'processing': 'purple',
            'shipped': 'teal',
            'delivered': 'green',
            'cancelled': 'red',
            'refunded': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Statut'

    def payment_status_display(self, obj):
        colors = {
            'pending': 'orange',
            'paid': 'green',
            'failed': 'red',
            'refunded': 'gray'
        }
        color = colors.get(obj.payment_status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_display.short_description = 'Paiement'

    def subtotal_calculated(self, obj):
        total = sum(item.total_price for item in obj.items.all())
        return f"{total} HTG"
    subtotal_calculated.short_description = 'Sous-total calculé'

    def total_calculated(self, obj):
        subtotal = sum(item.total_price for item in obj.items.all())
        total = subtotal + (obj.shipping_cost or 0) + (obj.tax_amount or 0) - (obj.discount_amount or 0)
        return f"{total} HTG"
    total_calculated.short_description = 'Total calculé'

# ============= BANNIÈRES =============
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'is_active', 'sort_order', 
        'start_date', 'end_date', 'click_count'
    ]
    list_filter = ['is_active', 'start_date', 'end_date']
    list_editable = ['is_active', 'sort_order']
    ordering = ['sort_order', '-created_at']
    
    fieldsets = (
        ('📋 Contenu bannière', {
            'fields': ('title', 'subtitle', 'description')
        }),
        ('🖼️ Images', {
            'fields': ('image_url', 'image_path', 'mobile_image_url')
        }),
        ('🎨 Style', {
            'fields': (
                ('button_text', 'button_color'),
                ('text_color', 'overlay_opacity')
            )
        }),
        ('🔗 Action', {
            'fields': ('link_url',)
        }),
        ('⚙️ Paramètres', {
            'fields': (
                'is_active', 'sort_order',
                ('start_date', 'end_date')
            )
        }),
        ('📊 Statistiques', {
            'fields': ('click_count',),
            'classes': ('collapse',)
        })
    )

# ============= IMAGES PRODUITS =============
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'title', 'is_primary', 'image_type', 'sort_order']
    list_filter = ['is_primary', 'image_type', 'product__category']
    search_fields = ['product__name', 'title', 'alt_text']
    raw_id_fields = ['product']
    list_editable = ['is_primary', 'sort_order']

# ============= AVIS =============
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'customer_name', 'rating_display', 
        'is_verified_purchase', 'is_approved', 'created_at'
    ]
    list_filter = [
        'rating', 'is_verified_purchase', 'is_approved', 'created_at'
    ]
    search_fields = ['product__name', 'customer_name', 'title', 'comment']
    raw_id_fields = ['product', 'user', 'order']
    list_editable = ['is_approved']
    readonly_fields = ['is_verified_purchase', 'helpful_count']

    def rating_display(self, obj):
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        return f"{stars} ({obj.rating}/5)"
    rating_display.short_description = 'Note'

# ============= TRANSACTIONS =============
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'order_link', 'amount_display',
        'status_display', 'payment_method', 'transaction_date'
    ]
    list_filter = ['status', 'payment_method', 'currency', 'transaction_date']
    search_fields = [
        'transaction_id', 'moncash_order_id', 'reference_number',
        'order__order_number'
    ]
    readonly_fields = [
        'transaction_id', 'gateway_response', 'transaction_date',
        'verified_at', 'webhook_received_at'
    ]
    raw_id_fields = ['order']

    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:marketplace_order_change', args=[obj.order.id])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return "Aucune"
    order_link.short_description = 'Commande'

    def amount_display(self, obj):
        return f"{obj.amount} {obj.currency}"
    amount_display.short_description = 'Montant'

    def status_display(self, obj):
        colors = {
            'pending': 'orange',
            'completed': 'green',
            'failed': 'red',
            'cancelled': 'gray',
            'refunded': 'purple'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Statut'

# ============= MODÈLES SIMPLES =============
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price', 'total_price']
    list_filter = ['order__status', 'created_at']
    search_fields = ['product__name', 'order__order_number']
    raw_id_fields = ['order', 'product']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_id', 'items_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'session_id']
    raw_id_fields = ['user']

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Articles'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'price', 'total_price']
    raw_id_fields = ['cart', 'product']

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'old_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['old_status', 'new_status', 'created_at']
    raw_id_fields = ['order', 'changed_by']

@admin.register(MediaContentSection)
class MediaContentSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'layout_type', 'is_active', 'sort_order']
    list_filter = ['layout_type', 'is_active']
    list_editable = ['is_active', 'sort_order']

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'is_featured', 'author']
    list_filter = ['is_active', 'is_featured', 'created_at']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'source', 'subscribed_at']
    search_fields = ['email', 'first_name', 'last_name']

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['setting_key', 'setting_value', 'setting_type', 'group_name']
    list_filter = ['setting_type', 'group_name', 'is_public']
    search_fields = ['setting_key', 'description']