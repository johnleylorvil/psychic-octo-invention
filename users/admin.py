# ======================================
# apps/users/admin.py
# ======================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Count
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Affichage de la liste
    list_display = ['username', 'email', 'full_name', 'user_type', 'is_active_status', 'created_at_formatted']
    list_filter = ['is_active', 'is_seller', 'is_staff', 'is_superuser', 'email_verified', 'city', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    # Fieldsets pour l'édition d'un utilisateur existant
    fieldsets = (
        ('Informations de connexion', {
            'fields': ('username', 'email', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'phone', 'birth_date', 'gender', 'profile_image')
        }),
        ('Adresse', {
            'fields': ('address', 'city', 'country')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_seller', 'email_verified', 'groups', 'user_permissions')
        }),
        ('Dates importantes', {
            'fields': ('date_joined', 'last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets pour la création d'un nouvel utilisateur
    add_fieldsets = (
        ('Informations de base', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        }),
        ('Permissions initiales', {
            'classes': ('wide',),
            'fields': ('is_staff', 'is_seller')
        }),
    )
    
    # Actions personnalisées
    actions = ['activate_users', 'deactivate_users', 'make_sellers', 'remove_seller_status', 'verify_emails']
    
    def full_name(self, obj):
        """Affiche le nom complet"""
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return "-"
    full_name.short_description = "Nom complet"
    
    def user_type(self, obj):
        """Affiche le type d'utilisateur avec couleur"""
        if obj.is_superuser:
            return format_html('<span style="color: purple; font-weight: bold;">👑 Super Admin</span>')
        elif obj.is_staff:
            return format_html('<span style="color: red; font-weight: bold;">🛡️ Staff</span>')
        elif obj.is_seller:
            return format_html('<span style="color: blue;">🏪 Vendeur</span>')
        else:
            return format_html('<span style="color: green;">👤 Client</span>')
    user_type.short_description = "Type"
    
    def is_active_status(self, obj):
        """Affiche le statut actif avec couleur"""
        if obj.is_active:
            if obj.email_verified:
                return format_html('<span style="color: green;">✅ Actif & Vérifié</span>')
            else:
                return format_html('<span style="color: orange;">⚠️ Actif non vérifié</span>')
        return format_html('<span style="color: red;">❌ Inactif</span>')
    is_active_status.short_description = "Statut"
    
    def created_at_formatted(self, obj):
        """Affiche la date de création formatée"""
        return obj.created_at.strftime('%d/%m/%Y')
    created_at_formatted.short_description = "Inscrit le"
    
    # Actions personnalisées
    def activate_users(self, request, queryset):
        """Activer les utilisateurs"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} utilisateur(s) activé(s).")
    activate_users.short_description = "Activer les utilisateurs sélectionnés"
    
    def deactivate_users(self, request, queryset):
        """Désactiver les utilisateurs"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} utilisateur(s) désactivé(s).")
    deactivate_users.short_description = "Désactiver les utilisateurs sélectionnés"
    
    def make_sellers(self, request, queryset):
        """Promouvoir en vendeurs"""
        updated = queryset.update(is_seller=True)
        self.message_user(request, f"{updated} utilisateur(s) promu(s) vendeur(s).")
    make_sellers.short_description = "Promouvoir en vendeurs"
    
    def remove_seller_status(self, request, queryset):
        """Retirer le statut vendeur"""
        updated = queryset.update(is_seller=False)
        self.message_user(request, f"{updated} vendeur(s) rétrogradé(s) en client(s).")
    remove_seller_status.short_description = "Retirer le statut vendeur"
    
    def verify_emails(self, request, queryset):
        """Vérifier les emails"""
        updated = queryset.update(email_verified=True)
        self.message_user(request, f"{updated} email(s) vérifié(s).")
    verify_emails.short_description = "Vérifier les emails"
    
    def changelist_view(self, request, extra_context=None):
        """Ajoute des statistiques dans la vue liste"""
        extra_context = extra_context or {}
        
        # Statistiques des utilisateurs
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        sellers = User.objects.filter(is_seller=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        verified_emails = User.objects.filter(email_verified=True).count()
        
        # Statistiques par ville
        top_cities = User.objects.values('city').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Utilisateurs récents (dernière semaine)
        from django.utils import timezone
        from datetime import timedelta
        week_ago = timezone.now() - timedelta(days=7)
        recent_users = User.objects.filter(created_at__gte=week_ago).count()
        
        extra_context.update({
            'total_users': total_users,
            'active_users': active_users,
            'sellers': sellers,
            'staff_users': staff_users,
            'verified_emails': verified_emails,
            'top_cities': top_cities,
            'recent_users': recent_users,
        })
        
        return super().changelist_view(request, extra_context=extra_context)
    
    def get_queryset(self, request):
        """Optimise les requêtes pour l'affichage liste"""
        return super().get_queryset(request).select_related()


# Configuration personnalisée de l'interface admin
admin.site.site_header = "Administration Afèpanou"
admin.site.site_title = "Afèpanou Admin"
admin.site.index_title = "Tableau de bord - Marketplace Haïtienne"