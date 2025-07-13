# ======================================
# apps/payments/admin.py
# ======================================

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order_link', 'amount_display', 'status_colored', 'payment_method', 'created_at_formatted']
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['transaction_id', 'moncash_order_id', 'reference_number', 'order__order_number']
    readonly_fields = ['transaction_id', 'moncash_order_id', 'payment_token', 'gateway_response', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informations transaction', {
            'fields': ('transaction_id', 'moncash_order_id', 'order', 'payment_token')
        }),
        ('Montant', {
            'fields': ('amount', 'currency', 'payment_method')
        }),
        ('Statut', {
            'fields': ('status', 'failure_reason', 'reference_number')
        }),
        ('Dates', {
            'fields': ('transaction_date', 'verified_at', 'webhook_received_at')
        }),
        ('URLs', {
            'fields': ('callback_url', 'return_url'),
            'classes': ('collapse',)
        }),
        ('Réponse Gateway', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_paid', 'mark_as_failed', 'verify_payments']
    
    def order_link(self, obj):
        if obj.order:
            url = reverse("admin:orders_order_change", args=[obj.order.pk])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return "Pas de commande"
    order_link.short_description = "Commande"
    
    def amount_display(self, obj):
        return f"{obj.amount} {obj.currency}"
    amount_display.short_description = "Montant"
    
    def status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'paid': 'green',
            'failed': 'red',
            'cancelled': 'gray',
            'refunded': 'blue',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status.upper()
        )
    status_colored.short_description = "Statut"
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = "Date"
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid')
        self.message_user(request, f"{updated} transaction(s) marquée(s) comme payée(s).")
    mark_as_paid.short_description = "Marquer comme payé"
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f"{updated} transaction(s) marquée(s) comme échouée(s).")
    mark_as_failed.short_description = "Marquer comme échoué"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Statistiques des transactions
        total_transactions = Transaction.objects.count()
        paid_transactions = Transaction.objects.filter(status='paid').count()
        total_revenue = Transaction.objects.filter(status='paid').aggregate(
            total=Sum('amount')
        )['total'] or 0
        pending_transactions = Transaction.objects.filter(status='pending').count()
        
        extra_context.update({
            'total_transactions': total_transactions,
            'paid_transactions': paid_transactions,
            'total_revenue': total_revenue,
            'pending_transactions': pending_transactions,
        })
        
        return super().changelist_view(request, extra_context=extra_context)
