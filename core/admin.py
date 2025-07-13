from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import SiteSetting, NewsletterSubscriber


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['setting_key', 'setting_value_truncated', 'setting_type', 'group_name', 'is_public', 'updated_at']
    list_filter = ['setting_type', 'group_name', 'is_public', 'created_at']
    search_fields = ['setting_key', 'setting_value', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Configuration', {
            'fields': ('setting_key', 'setting_value', 'setting_type')
        }),
        ('Métadonnées', {
            'fields': ('description', 'group_name', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def setting_value_truncated(self, obj):
        """Affiche une version tronquée de la valeur"""
        if obj.setting_value:
            if len(obj.setting_value) > 50:
                return f"{obj.setting_value[:50]}..."
            return obj.setting_value
        return "-"
    setting_value_truncated.short_description = "Valeur"
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request)
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'is_active_status', 'source', 'subscribed_at_formatted']
    list_filter = ['is_active', 'source', 'subscribed_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['subscribed_at', 'unsubscribed_at']
    date_hierarchy = 'subscribed_at'
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('email', 'first_name', 'last_name')
        }),
        ('Statut', {
            'fields': ('is_active', 'source')
        }),
        ('Dates', {
            'fields': ('subscribed_at', 'unsubscribed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_subscribers', 'deactivate_subscribers', 'export_emails']
    
    def full_name(self, obj):
        """Affiche le nom complet"""
        if obj.first_name or obj.last_name:
            return f"{obj.first_name or ''} {obj.last_name or ''}".strip()
        return "-"
    full_name.short_description = "Nom complet"
    
    def is_active_status(self, obj):
        """Affiche le statut avec couleur"""
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Actif</span>')
        return format_html('<span style="color: red;">✗ Inactif</span>')
    is_active_status.short_description = "Statut"
    
    def subscribed_at_formatted(self, obj):
        """Affiche la date d'inscription formatée"""
        if obj.subscribed_at:
            return obj.subscribed_at.strftime('%d/%m/%Y %H:%M')
        return "-"
    subscribed_at_formatted.short_description = "Date d'inscription"
    
    def activate_subscribers(self, request, queryset):
        """Action pour activer les abonnés"""
        updated = queryset.update(is_active=True, unsubscribed_at=None)
        self.message_user(request, f"{updated} abonné(s) activé(s).")
    activate_subscribers.short_description = "Activer les abonnés sélectionnés"
    
    def deactivate_subscribers(self, request, queryset):
        """Action pour désactiver les abonnés"""
        from django.utils import timezone
        updated = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, f"{updated} abonné(s) désactivé(s).")
    deactivate_subscribers.short_description = "Désactiver les abonnés sélectionnés"
    
    def export_emails(self, request, queryset):
        """Action pour exporter les emails"""
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="newsletter_subscribers.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'Prénom', 'Nom', 'Actif', 'Source', 'Date inscription'])
        
        for subscriber in queryset:
            writer.writerow([
                subscriber.email,
                subscriber.first_name or '',
                subscriber.last_name or '',
                'Oui' if subscriber.is_active else 'Non',
                subscriber.source,
                subscriber.subscribed_at.strftime('%d/%m/%Y') if subscriber.subscribed_at else ''
            ])
        
        return response
    export_emails.short_description = "Exporter les emails en CSV"
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request)
    
    def changelist_view(self, request, extra_context=None):
        """Ajoute des statistiques dans la vue liste"""
        extra_context = extra_context or {}
        
        # Statistiques des abonnés
        total_subscribers = NewsletterSubscriber.objects.count()
        active_subscribers = NewsletterSubscriber.objects.filter(is_active=True).count()
        inactive_subscribers = total_subscribers - active_subscribers
        
        # Statistiques par source
        sources_stats = NewsletterSubscriber.objects.values('source').annotate(
            count=Count('id')
        ).order_by('-count')
        
        extra_context.update({
            'total_subscribers': total_subscribers,
            'active_subscribers': active_subscribers,
            'inactive_subscribers': inactive_subscribers,
            'sources_stats': sources_stats,
        })
        
        return super().changelist_view(request, extra_context=extra_context)


# Configuration de l'admin pour personnaliser le titre
admin.site.site_header = "Administration Afèpanou"
admin.site.site_title = "Afèpanou Admin"
admin.site.index_title = "Tableau de bord"