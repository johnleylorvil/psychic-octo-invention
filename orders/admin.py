# ======================================
# apps/orders/admin.py
# ======================================

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse
from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    fields = ['product', 'quantity', 'price', 'created_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'session_id', 'items_count', 'total_value', 'is_active', 'created_at_formatted']
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'session_id']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    
    def user_link(self, obj):
        if obj.user:
            url = reverse("admin:users_user_change", args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "Invité"
    user_link.short_description = "Utilisateur"
    
    def items_count(self, obj):
        return obj.cartitem_set.count()
    items_count.short_description = "Articles"
    
    def total_value(self, obj):
        total = obj.cartitem_set.aggregate(
            total=Sum('price')
        )['total'] or 0
        return f"{total} HTG"
    total_value.short_description = "Valeur totale"
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = "Créé le"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['created_at', 'total_price']
    fields = ['product', 'product_name', 'quantity', 'unit_price', 'total_price']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['created_at']
    fields = ['old_status', 'new_status', 'changed_by', 'comment', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_name', 'total_amount_formatted', 'status_colored', 'payment_status_colored', 'created_at_formatted']
    list_filter = ['status', 'payment_status', 'payment_method', 'shipping_city', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'customer_phone']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Informations commande', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'payment_method')
        }),
        ('Client', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Livraison', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_country', 'shipping_method', 'tracking_number')
        }),
        ('Facturation', {
            'fields': ('billing_address', 'billing_city', 'billing_country'),
            'classes': ('collapse',)
        }),
        ('Montants', {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'discount_amount', 'total_amount', 'currency')
        }),
        ('Livraison', {
            'fields': ('estimated_delivery', 'delivered_at')
        }),
        ('Notes', {
            'fields': ('notes', 'admin_notes', 'coupon_code'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered', 'export_orders']
    
    def status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'confirmed': 'blue',
            'processing': 'purple',
            'shipped': 'green',
            'delivered': 'darkgreen',
            'cancelled': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status.upper()
        )
    status_colored.short_description = "Statut"
    
    def payment_status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'paid': 'green',
            'failed': 'red',
            'refunded': 'blue',
        }
        color = colors.get(obj.payment_status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.payment_status.upper()
        )
    payment_status_colored.short_description = "Paiement"
    
    def total_amount_formatted(self, obj):
        return f"{obj.total_amount} {obj.currency}"
    total_amount_formatted.short_description = "Total"
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = "Date"
    
    def mark_as_confirmed(self, request, queryset):
        for order in queryset:
            old_status = order.status
            order.status = 'confirmed'
            order.save()
            
            # Ajouter à l'historique
            OrderStatusHistory.objects.create(
                order=order,
                old_status=old_status,
                new_status='confirmed',
                changed_by=request.user,
                comment=f"Confirmé par {request.user.username}"
            )
        
        self.message_user(request, f"{queryset.count()} commande(s) confirmée(s).")
    mark_as_confirmed.short_description = "Marquer comme confirmé"
    
    def mark_as_shipped(self, request, queryset):
        for order in queryset:
            old_status = order.status
            order.status = 'shipped'
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                old_status=old_status,
                new_status='shipped',
                changed_by=request.user,
                comment=f"Expédié par {request.user.username}"
            )
        
        self.message_user(request, f"{queryset.count()} commande(s) expédiée(s).")
    mark_as_shipped.short_description = "Marquer comme expédié"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Statistiques des commandes
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        total_revenue = Order.objects.filter(payment_status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        extra_context.update({
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_revenue': total_revenue,
        })
        
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'old_status', 'new_status', 'changed_by', 'created_at_formatted']
    list_filter = ['new_status', 'created_at']
    search_fields = ['order__order_number', 'comment']
    readonly_fields = ['created_at']
    
    def order_link(self, obj):
        url = reverse("admin:orders_order_change", args=[obj.order.pk])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = "Commande"
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = "Date"