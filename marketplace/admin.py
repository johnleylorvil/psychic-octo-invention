# marketplace/admin.py
"""
Enhanced admin interface for Afèpanou marketplace
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from marketplace.models import (
    User, VendorProfile, Category, Product, ProductImage,
    Cart, CartItem, Order, OrderItem, OrderStatusHistory,
    Transaction, Review, Banner, MediaContentSection, 
    Page, NewsletterSubscriber, SiteSetting, Promotion
)


# User Management
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_seller', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_seller', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('email', 'first_name', 'last_name', 'phone')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_seller'),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['last_login', 'date_joined']
    
    actions = ['activate_users', 'deactivate_users', 'make_seller']
    
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} users activated.")
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} users deactivated.")
    deactivate_users.short_description = "Deactivate selected users"
    
    def make_seller(self, request, queryset):
        queryset.update(is_seller=True)
        self.message_user(request, f"{queryset.count()} users made sellers.")
    make_seller.short_description = "Make selected users sellers"


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'business_name', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__email', 'business_name', 'business_description']
    readonly_fields = ['created_at', 'updated_at']


# Product Management
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image', 'alt_text', 'is_primary', 'display_order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'is_featured', 'product_count']
    list_filter = ['is_active', 'is_featured', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.filter(is_active=True).count()
    product_count.short_description = 'Active Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'seller', 'category', 'price', 'promotional_price',
        'stock_quantity', 'is_active', 'is_featured', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_featured', 'is_digital', 'category',
        'created_at', 'seller'
    ]
    search_fields = ['name', 'sku', 'description', 'tags', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'view_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'seller', 'category', 'brand')
        }),
        ('Product Details', {
            'fields': ('description', 'short_description', 'specifications', 'tags')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'promotional_price', 'cost_price', 'sku', 'stock_quantity', 'min_stock_alert', 'is_digital')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_featured', 'weight', 'dimensions')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline]
    
    actions = ['activate_products', 'deactivate_products', 'feature_products']
    
    def activate_products(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} products activated.")
    activate_products.short_description = "Activate selected products"
    
    def deactivate_products(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} products deactivated.")
    deactivate_products.short_description = "Deactivate selected products"
    
    def feature_products(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} products featured.")
    feature_products.short_description = "Feature selected products"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_primary', 'sort_order']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']


# Order Management
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product', 'product_name', 'quantity', 'unit_price', 'total_price']
    extra = 0
    
    def has_add_permission(self, request, obj=None):
        return False


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    readonly_fields = ['old_status', 'new_status', 'changed_by', 'created_at']
    extra = 0
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user_email', 'status', 'payment_status',
        'total_amount', 'created_at'
    ]
    list_filter = [
        'status', 'payment_status', 'payment_method', 'created_at'
    ]
    search_fields = [
        'order_number', 'user__email', 'email', 
        'shipping_first_name', 'shipping_last_name'
    ]
    readonly_fields = [
        'order_number', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'email', 'phone', 'status', 'payment_status', 'payment_method')
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_first_name', 'shipping_last_name',
                'shipping_address_line1', 'shipping_address_line2',
                'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country'
            )
        }),
        ('Billing Address', {
            'fields': (
                'billing_first_name', 'billing_last_name',
                'billing_address_line1', 'billing_address_line2',
                'billing_city', 'billing_state', 'billing_postal_code', 'billing_country'
            ),
            'classes': ('collapse',)
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'total_amount')
        }),
        ('Additional Information', {
            'fields': ('special_instructions', 'tracking_number', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    def user_email(self, obj):
        return obj.user.email if obj.user else obj.email
    user_email.short_description = 'Email'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_id', 'is_active', 'item_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'session_id']
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


# Payment Management
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'amount', 'currency', 'payment_method', 
        'status', 'transaction_id', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['order__order_number', 'transaction_id']
    readonly_fields = [
        'created_at', 'updated_at', 'gateway_response'
    ]
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('order', 'amount', 'currency', 'payment_method', 'status')
        }),
        ('External Reference', {
            'fields': ('transaction_id', 'reference_number')
        }),
        ('Metadata', {
            'fields': ('gateway_response', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


# Review Management
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'user', 'rating', 'is_approved', 
        'is_verified_purchase', 'created_at'
    ]
    list_filter = [
        'rating', 'is_approved', 'is_verified_purchase', 'created_at'
    ]
    search_fields = ['product__name', 'user__email', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} reviews disapproved.")
    disapprove_reviews.short_description = "Disapprove selected reviews"


# Content Management
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'sort_order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'button_text']
    
    fieldsets = (
        ('Banner Content', {
            'fields': ('title', 'subtitle', 'description', 'button_text', 'link_url')
        }),
        ('Media', {
            'fields': ('image_url', 'image_path', 'mobile_image_url')
        }),
        ('Settings', {
            'fields': ('is_active', 'sort_order', 'layout_type')
        }),
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'first_name', 'last_name']
    
    actions = ['activate_subscribers', 'deactivate_subscribers']
    
    def activate_subscribers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} subscribers activated.")
    activate_subscribers.short_description = "Activate selected subscribers"
    
    def deactivate_subscribers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} subscribers deactivated.")
    deactivate_subscribers.short_description = "Deactivate selected subscribers"


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['setting_key', 'setting_value', 'description']
    search_fields = ['setting_key', 'description']
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'discount_type', 'discount_value', 'is_active',
        'start_date', 'end_date'
    ]
    list_filter = ['discount_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['name', 'code']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'discount_type')
        }),
        ('Discount Settings', {
            'fields': ('discount_value', 'minimum_amount')
        }),
        ('Validity', {
            'fields': ('start_date', 'end_date', 'maximum_uses', 'current_uses')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['current_uses']


# Custom admin site configuration
admin.site.site_header = "Afèpanou Admin"
admin.site.site_title = "Afèpanou Admin Portal"
admin.site.index_title = "Welcome to Afèpanou Administration"