# ======================================
# apps/products/admin.py
# ======================================

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Count
from django.urls import reverse
from .models import Category, Product, ProductImage, Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['created_at']
    fields = ['image_url', 'alt_text', 'is_primary', 'sort_order', 'image_type']


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = ['customer_name', 'rating', 'title', 'is_approved', 'created_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_link', 'products_count', 'is_featured_status', 'is_active_status', 'sort_order']
    list_filter = ['is_featured', 'is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'slug', 'parent', 'description', 'detailed_description')
        }),
        ('Images et médias', {
            'fields': ('banner_image', 'banner_image_path', 'icon', 'folder_path')
        }),
        ('Configuration', {
            'fields': ('is_featured', 'is_active', 'sort_order')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_featured', 'make_active', 'make_inactive']
    
    def parent_link(self, obj):
        if obj.parent:
            url = reverse("admin:products_category_change", args=[obj.parent.pk])
            return format_html('<a href="{}">{}</a>', url, obj.parent.name)
        return "Racine"
    parent_link.short_description = "Catégorie parent"
    
    def products_count(self, obj):
        count = obj.product_set.count()
        return format_html('<strong>{}</strong>', count)
    products_count.short_description = "Produits"
    
    def is_featured_status(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: gold;">★ Vedette</span>')
        return format_html('<span style="color: gray;">-</span>')
    is_featured_status.short_description = "Vedette"
    
    def is_active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Actif</span>')
        return format_html('<span style="color: red;">✗ Inactif</span>')
    is_active_status.short_description = "Statut"
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} catégorie(s) marquée(s) comme vedette.")
    make_featured.short_description = "Marquer comme vedette"
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} catégorie(s) activée(s).")
    make_active.short_description = "Activer"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} catégorie(s) désactivée(s).")
    make_inactive.short_description = "Désactiver"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_link', 'seller_link', 'price_display', 'stock_status', 'rating_display', 'is_featured_status', 'is_active_status']
    list_filter = ['is_featured', 'is_active', 'category', 'seller', 'is_digital', 'created_at']
    search_fields = ['name', 'sku', 'description', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ReviewInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'slug', 'category', 'seller', 'short_description', 'description', 'detailed_description')
        }),
        ('Prix et stock', {
            'fields': ('price', 'promotional_price', 'cost_price', 'stock_quantity', 'min_stock_alert')
        }),
        ('Identifiants', {
            'fields': ('sku', 'barcode'),
            'classes': ('collapse',)
        }),
        ('Spécifications', {
            'fields': ('specifications', 'brand', 'model', 'color', 'material', 'weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('is_featured', 'is_active', 'is_digital', 'requires_shipping', 'origin_country', 'condition_type')
        }),
        ('Médias', {
            'fields': ('video_url', 'tags'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['make_featured', 'make_active', 'duplicate_products', 'check_stock']
    
    def category_link(self, obj):
        url = reverse("admin:products_category_change", args=[obj.category.pk])
        return format_html('<a href="{}">{}</a>', url, obj.category.name)
    category_link.short_description = "Catégorie"
    
    def seller_link(self, obj):
        url = reverse("admin:users_user_change", args=[obj.seller.pk])
        return format_html('<a href="{}">{}</a>', url, obj.seller.username)
    seller_link.short_description = "Vendeur"
    
    def price_display(self, obj):
        if obj.promotional_price:
            return format_html(
                '<span style="text-decoration: line-through; color: gray;">{} HTG</span><br>'
                '<strong style="color: red;">{} HTG</strong>',
                obj.price, obj.promotional_price
            )
        return f"{obj.price} HTG"
    price_display.short_description = "Prix"
    
    def stock_status(self, obj):
        if obj.stock_quantity <= 0:
            return format_html('<span style="color: red; font-weight: bold;">📦 Rupture</span>')
        elif obj.stock_quantity <= obj.min_stock_alert:
            return format_html('<span style="color: orange; font-weight: bold;">⚠️ Faible ({} restants)</span>', obj.stock_quantity)
        else:
            return format_html('<span style="color: green;">✓ En stock ({})</span>', obj.stock_quantity)
    stock_status.short_description = "Stock"
    
    def rating_display(self, obj):
        reviews = obj.review_set.filter(is_approved=True)
        if reviews.exists():
            avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
            count = reviews.count()
            stars = '★' * int(avg_rating) + '☆' * (5 - int(avg_rating))
            return format_html('{} ({:.1f}/5 - {} avis)', stars, avg_rating, count)
        return "Pas d'avis"
    rating_display.short_description = "Note"
    
    def is_featured_status(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: gold;">★ Vedette</span>')
        return "-"
    is_featured_status.short_description = "Vedette"
    
    def is_active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Actif</span>')
        return format_html('<span style="color: red;">✗ Inactif</span>')
    is_active_status.short_description = "Statut"
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} produit(s) marqué(s) comme vedette.")
    make_featured.short_description = "Marquer comme vedette"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        featured_products = Product.objects.filter(is_featured=True).count()
        low_stock = Product.objects.filter(stock_quantity__lte=5).count()
        
        extra_context.update({
            'total_products': total_products,
            'active_products': active_products,
            'featured_products': featured_products,
            'low_stock': low_stock,
        })
        
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_link', 'image_preview', 'is_primary', 'image_type', 'sort_order']
    list_filter = ['is_primary', 'image_type', 'created_at']
    search_fields = ['title', 'alt_text', 'product__name']
    readonly_fields = ['created_at']
    
    def product_link(self, obj):
        url = reverse("admin:products_product_change", args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = "Produit"
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image_url)
        return "Pas d'image"
    image_preview.short_description = "Aperçu"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'product_link', 'customer_name', 'rating_stars', 'is_verified_status', 'is_approved_status', 'created_at_formatted']
    list_filter = ['rating', 'is_verified_purchase', 'is_approved', 'created_at']
    search_fields = ['title', 'customer_name', 'customer_email', 'comment', 'product__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Avis', {
            'fields': ('product', 'user', 'order', 'customer_name', 'customer_email')
        }),
        ('Contenu', {
            'fields': ('rating', 'title', 'comment', 'pros', 'cons')
        }),
        ('Modération', {
            'fields': ('is_verified_purchase', 'is_approved', 'helpful_count')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'reject_reviews']
    
    def product_link(self, obj):
        url = reverse("admin:products_product_change", args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = "Produit"
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: gold;">{}</span> ({})', stars, obj.rating)
    rating_stars.short_description = "Note"
    
    def is_verified_status(self, obj):
        if obj.is_verified_purchase:
            return format_html('<span style="color: green;">✓ Vérifié</span>')
        return format_html('<span style="color: gray;">Non vérifié</span>')
    is_verified_status.short_description = "Achat vérifié"
    
    def is_approved_status(self, obj):
        if obj.is_approved:
            return format_html('<span style="color: green;">✓ Approuvé</span>')
        return format_html('<span style="color: orange;">⏳ En attente</span>')
    is_approved_status.short_description = "Statut"
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = "Date"
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} avis approuvé(s).")
    approve_reviews.short_description = "Approuver les avis"
    
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} avis rejeté(s).")
    reject_reviews.short_description = "Rejeter les avis"