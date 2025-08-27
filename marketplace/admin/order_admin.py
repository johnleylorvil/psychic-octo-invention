# marketplace/admin/order_admin.py
"""
Order administration interface
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum
from django.utils import timezone

from ..models import Cart, CartItem, Order, OrderItem, OrderStatusHistory


class CartItemInline(admin.TabularInline):
    """Inline for cart items"""
    model = CartItem
    extra = 0
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    fields = ['product', 'quantity', 'price', 'total_price', 'options']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Cart admin"""
    
    list_display = [
        'cart_identifier',
        'user_or_session',
        'items_count',
        'total_value',
        'is_active',
        'created_at',
        'expires_at'
    ]
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'session_id']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'subtotal']
    inlines = [CartItemInline]
    date_hierarchy = 'created_at'
    
    def cart_identifier(self, obj):
        """Display cart identifier"""
        return f"Cart #{obj.id}"
    cart_identifier.short_description = 'Panier'
    
    def user_or_session(self, obj):
        """Display user or session ID"""
        if obj.user:
            url = reverse('admin:marketplace_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.get_display_name())
        return f"Session: {obj.session_id[:20]}..."
    user_or_session.short_description = 'Utilisateur/Session'
    
    def items_count(self, obj):
        """Display number of items"""
        return obj.total_items
    items_count.short_description = 'Articles'
    
    def total_value(self, obj):
        """Display cart total value"""
        return format_html('<strong>{} HTG</strong>', obj.subtotal)
    total_value.short_description = 'Valeur Totale'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user').prefetch_related('items')


class OrderItemInline(admin.TabularInline):
    """Inline for order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price', 'product_name', 'product_sku', 'created_at']
    fields = [
        'product', 'product_name', 'quantity', 'unit_price', 
        'total_price', 'product_sku', 'product_options'
    ]


class OrderStatusHistoryInline(admin.TabularInline):
    """Inline for order status history"""
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['created_at']
    fields = ['old_status', 'new_status', 'changed_by', 'comment', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Enhanced Order admin"""
    
    list_display = [
        'order_number',
        'customer_display',
        'status_display',
        'payment_status_display',
        'total_display',
        'items_count',
        'created_at'
    ]
    list_filter = [
        'status',
        'payment_status',
        'payment_method',
        'shipping_city',
        'created_at'
    ]
    search_fields = [
        'order_number',
        'customer_name',
        'customer_email',
        'customer_phone',
        'user__username',
        'user__email'
    ]
    readonly_fields = [
        'order_number',
        'created_at',
        'updated_at',
        'total_items_display',
        'order_summary_display'
    ]
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations de Commande', {
            'fields': (
                'order_number', 'user', 'status', 'payment_status',
                'payment_method', 'source'
            )
        }),
        ('Informations Client', {
            'fields': (
                'customer_name', 'customer_email', 'customer_phone'
            )
        }),
        ('Adresse de Livraison', {
            'fields': (
                'shipping_address', 'shipping_city', 'shipping_country',
                'shipping_method', 'tracking_number', 'estimated_delivery'
            )
        }),
        ('Adresse de Facturation', {
            'fields': ('billing_address', 'billing_city', 'billing_country'),
            'classes': ['collapse']
        }),
        ('Totaux', {
            'fields': (
                ('subtotal', 'shipping_cost'),
                ('tax_amount', 'discount_amount'),
                'total_amount', 'currency'
            )
        }),
        ('Notes et Informations', {
            'fields': ('notes', 'admin_notes', 'coupon_code'),
            'classes': ['collapse']
        }),
        ('Résumé', {
            'fields': ('total_items_display', 'order_summary_display'),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivered_at'),
            'classes': ['collapse']
        })
    )
    
    def customer_display(self, obj):
        """Display customer information"""
        if obj.user:
            url = reverse('admin:marketplace_user_change', args=[obj.user.id])
            return format_html(
                '<a href="{}">{}</a><br><small>{}</small>',
                url,
                obj.customer_name,
                obj.customer_email
            )
        return format_html('{}<br><small>{}</small>', obj.customer_name, obj.customer_email)
    customer_display.short_description = 'Client'
    
    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': '#ffc107',
            'confirmed': '#17a2b8',
            'processing': '#007bff',
            'shipped': '#6f42c1',
            'delivered': '#28a745',
            'cancelled': '#dc3545',
            'refunded': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Statut'
    status_display.admin_order_field = 'status'
    
    def payment_status_display(self, obj):
        """Display payment status with color coding"""
        colors = {
            'pending': '#ffc107',
            'paid': '#28a745',
            'failed': '#dc3545',
            'refunded': '#6c757d'
        }
        color = colors.get(obj.payment_status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_display.short_description = 'Paiement'
    payment_status_display.admin_order_field = 'payment_status'
    
    def total_display(self, obj):
        """Display total amount"""
        return format_html('<strong>{} HTG</strong>', obj.total_amount)
    total_display.short_description = 'Total'
    total_display.admin_order_field = 'total_amount'
    
    def items_count(self, obj):
        """Display number of items"""
        count = obj.items.count()
        url = f"/admin/marketplace/orderitem/?order__id={obj.id}"
        return format_html('<a href="{}">{} article{}</a>', url, count, 's' if count != 1 else '')
    items_count.short_description = 'Articles'
    
    def total_items_display(self, obj):
        """Display total items count for detail view"""
        return sum(item.quantity for item in obj.items.all())
    total_items_display.short_description = 'Total Articles'
    
    def order_summary_display(self, obj):
        """Display order summary"""
        items_html = []
        for item in obj.items.all():
            items_html.append(
                f'<tr>'
                f'<td>{item.product_name}</td>'
                f'<td>{item.quantity}</td>'
                f'<td>{item.unit_price} HTG</td>'
                f'<td><strong>{item.total_price} HTG</strong></td>'
                f'</tr>'
            )
        
        return format_html(
            '<table style="width: 100%; border-collapse: collapse;">'
            '<thead>'
            '<tr style="background: #f8f9fa;">'
            '<th style="padding: 8px; border: 1px solid #dee2e6;">Produit</th>'
            '<th style="padding: 8px; border: 1px solid #dee2e6;">Qté</th>'
            '<th style="padding: 8px; border: 1px solid #dee2e6;">Prix Unit.</th>'
            '<th style="padding: 8px; border: 1px solid #dee2e6;">Total</th>'
            '</tr>'
            '</thead>'
            '<tbody>{}</tbody>'
            '</table>',
            ''.join(items_html)
        )
    order_summary_display.short_description = 'Résumé de Commande'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('user').prefetch_related('items')
    
    actions = [
        'mark_as_confirmed',
        'mark_as_processing', 
        'mark_as_shipped',
        'mark_as_delivered'
    ]
    
    def mark_as_confirmed(self, request, queryset):
        """Mark orders as confirmed"""
        from ..services import OrderService
        updated = 0
        for order in queryset.filter(status='pending'):
            if OrderService.update_order_status(order, 'confirmed', request.user):
                updated += 1
        self.message_user(request, f'{updated} commandes confirmées.')
    mark_as_confirmed.short_description = 'Marquer comme confirmé'
    
    def mark_as_processing(self, request, queryset):
        """Mark orders as processing"""
        from ..services import OrderService
        updated = 0
        for order in queryset.filter(status__in=['pending', 'confirmed']):
            if OrderService.update_order_status(order, 'processing', request.user):
                updated += 1
        self.message_user(request, f'{updated} commandes en traitement.')
    mark_as_processing.short_description = 'Marquer en traitement'
    
    def mark_as_shipped(self, request, queryset):
        """Mark orders as shipped"""
        from ..services import OrderService
        updated = 0
        for order in queryset.filter(status__in=['confirmed', 'processing']):
            if OrderService.update_order_status(order, 'shipped', request.user):
                updated += 1
        self.message_user(request, f'{updated} commandes expédiées.')
    mark_as_shipped.short_description = 'Marquer comme expédié'
    
    def mark_as_delivered(self, request, queryset):
        """Mark orders as delivered"""
        from ..services import OrderService
        updated = 0
        for order in queryset.filter(status='shipped'):
            if OrderService.update_order_status(order, 'delivered', request.user):
                updated += 1
        self.message_user(request, f'{updated} commandes livrées.')
    mark_as_delivered.short_description = 'Marquer comme livré'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Order Item admin"""
    
    list_display = [
        'order_link',
        'product_name',
        'quantity',
        'unit_price',
        'total_price',
        'order_status'
    ]
    list_filter = ['order__status', 'order__created_at']
    search_fields = [
        'product_name',
        'order__order_number',
        'product__name',
        'product_sku'
    ]
    readonly_fields = ['total_price', 'created_at']
    
    def order_link(self, obj):
        """Link to order"""
        url = reverse('admin:marketplace_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = 'Commande'
    
    def order_status(self, obj):
        """Display order status"""
        return obj.order.get_status_display()
    order_status.short_description = 'Statut Commande'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        return super().get_queryset(request).select_related('order', 'product')