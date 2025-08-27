# marketplace/admin/product_admin.py
"""
Product administration interface
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.utils import timezone

from ..models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    """Inline for product images"""
    model = ProductImage
    extra = 1
    fields = ('image_url', 'image_path', 'alt_text', 'is_primary', 'sort_order', 'image_type')
    readonly_fields = ('created_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Enhanced Category admin"""
    
    list_display = [
        'name', 
        'parent', 
        'product_count', 
        'is_featured', 
        'is_active', 
        'sort_order',
        'created_at'
    ]
    list_filter = ['is_featured', 'is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_featured', 'is_active', 'sort_order']
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        ('Informations de Base', {
            'fields': ('name', 'slug', 'description', 'detailed_description', 'parent')
        }),
        ('Médias', {
            'fields': ('banner_image', 'banner_image_path', 'icon', 'folder_path'),
            'classes': ['collapse']
        }),
        ('Paramètres', {
            'fields': ('is_featured', 'is_active', 'sort_order')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    def product_count(self, obj):
        """Display number of products in category"""
        count = obj.products.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:marketplace_product_changelist') + f'?category__id={obj.id}'
            return format_html(
                '<a href="{}">{} produit{}</a>',
                url,
                count,
                's' if count != 1 else ''
            )
        return '0 produit'
    product_count.short_description = 'Produits'
    product_count.admin_order_field = 'products__count'
    
    def get_queryset(self, request):
        """Optimize queryset with annotations"""
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        ).select_related('parent')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Enhanced Product admin"""
    
    list_display = [
        'name',
        'category',
        'seller_name',
        'current_price_display',
        'stock_display',
        'rating_display',
        'is_featured',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'category',
        'seller',
        'is_featured',
        'is_active',
        'is_digital',
        'condition_type',
        'created_at'
    ]
    search_fields = ['name', 'description', 'sku', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = [
        'sku', 
        'created_at', 
        'updated_at', 
        'average_rating_display',
        'review_count_display'
    ]
    list_editable = ['is_featured', 'is_active']
    ordering = ['-created_at']
    inlines = [ProductImageInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations de Base', {
            'fields': (
                'name', 'slug', 'short_description', 'description', 
                'detailed_description', 'specifications'
            )
        }),
        ('Catégorie et Vendeur', {
            'fields': ('category', 'seller')
        }),
        ('Prix et Inventaire', {
            'fields': (
                ('price', 'promotional_price', 'cost_price'),
                ('stock_quantity', 'min_stock_alert'),
                ('sku', 'barcode')
            )
        }),
        ('Détails du Produit', {
            'fields': (
                ('brand', 'model', 'color'),
                ('material', 'origin_country', 'condition_type'),
                ('weight', 'dimensions'),
                ('warranty_period', 'video_url')
            ),
            'classes': ['collapse']
        }),
        ('Paramètres', {
            'fields': (
                ('is_featured', 'is_active'),
                ('is_digital', 'requires_shipping'),
                'tags'
            )
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ['collapse']
        }),
        ('Statistiques', {
            'fields': ('average_rating_display', 'review_count_display'),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    def seller_name(self, obj):
        """Display seller name with link"""
        url = reverse('admin:marketplace_user_change', args=[obj.seller.id])
        return format_html('<a href="{}">{}</a>', url, obj.seller.get_display_name())
    seller_name.short_description = 'Vendeur'
    seller_name.admin_order_field = 'seller__username'
    
    def current_price_display(self, obj):
        """Display current price with promotional price if applicable"""
        if obj.promotional_price:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">{} HTG</span><br>'
                '<strong style="color: #e74c3c;">{} HTG</strong>',
                obj.price,
                obj.promotional_price
            )
        return format_html('<strong>{} HTG</strong>', obj.price)
    current_price_display.short_description = 'Prix Actuel'
    current_price_display.admin_order_field = 'price'
    
    def stock_display(self, obj):
        """Display stock with color coding"""
        if obj.is_digital:
            return mark_safe('<span style="color: #28a745;">Numérique</span>')
        
        stock = obj.stock_quantity or 0
        if stock == 0:
            color = '#dc3545'  # Red
            status = 'Rupture'
        elif stock <= obj.min_stock_alert:
            color = '#ffc107'  # Yellow
            status = 'Stock Faible'
        else:
            color = '#28a745'  # Green
            status = 'En Stock'
        
        return format_html(
            '<span style="color: {};">{} ({})</span>',
            color,
            stock,
            status
        )
    stock_display.short_description = 'Stock'
    stock_display.admin_order_field = 'stock_quantity'
    
    def rating_display(self, obj):
        """Display product rating"""
        if hasattr(obj, 'average_rating') and obj.average_rating:
            rating = obj.average_rating
            stars = '★' * int(rating) + '☆' * (5 - int(rating))
            return format_html(
                '{} ({:.1f}/5)',
                stars,
                rating
            )
        return 'Pas d\'avis'
    rating_display.short_description = 'Évaluation'
    
    def average_rating_display(self, obj):
        """Display average rating for detail view"""
        from ..services import ProductService
        rating_stats = ProductService.calculate_product_rating(obj)
        if rating_stats['total_count'] > 0:
            return f"{rating_stats['average']}/5 ({rating_stats['total_count']} avis)"
        return "Aucun avis"
    average_rating_display.short_description = 'Évaluation Moyenne'
    
    def review_count_display(self, obj):
        """Display review count with link"""
        count = obj.reviews.filter(is_approved=True).count()
        if count > 0:
            url = reverse('admin:marketplace_review_changelist') + f'?product__id={obj.id}'
            return format_html('<a href="{}">{} avis</a>', url, count)
        return '0 avis'
    review_count_display.short_description = 'Nombre d\'Avis'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related(
            'category', 'seller'
        ).prefetch_related('images', 'reviews')
    
    actions = ['make_featured', 'make_unfeatured', 'activate_products', 'deactivate_products']
    
    def make_featured(self, request, queryset):
        """Mark products as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} produits marqués comme vedettes.')
    make_featured.short_description = 'Marquer comme vedette'
    
    def make_unfeatured(self, request, queryset):
        """Remove featured status"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} produits retirés des vedettes.')
    make_unfeatured.short_description = 'Retirer des vedettes'
    
    def activate_products(self, request, queryset):
        """Activate products"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} produits activés.')
    activate_products.short_description = 'Activer les produits'
    
    def deactivate_products(self, request, queryset):
        """Deactivate products"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} produits désactivés.')
    deactivate_products.short_description = 'Désactiver les produits'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Product Image admin"""
    
    list_display = ['product', 'image_type', 'is_primary', 'sort_order', 'created_at']
    list_filter = ['image_type', 'is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text', 'title']
    readonly_fields = ['created_at']
    ordering = ['product', 'sort_order']
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('product')