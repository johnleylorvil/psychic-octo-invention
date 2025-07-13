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
    list_display = ['username', 'email', 'full_name', 'user_type', 'is_active_status', 'created_at_formatted']
    list_filter = ['is_active', 'is_seller', 'is_admin', 'email_verified', 'city', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    date_hierarchy = 'created_at'
    
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
            'fields': ('is_active', 'is_admin', 'is_seller', 'email_verified')
        }),
        ('Dates importantes', {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Création utilisateur', {
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
        }),
        ('Permissions initiales', {
            'fields': ('is_seller', 'is_admin')
        }),
    )
    
    actions = ['activate_users', 'deactivate_users', 'make_sellers', 'verify_emails']
    
    def full_name(self, obj):
        """Affiche le nom complet"""
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Nom complet"
    
    def user_type(self, obj):
        """Affiche le type d'utilisateur avec couleur"""
        if obj.is_admin:
            return format_html('<span style="color: red; font-weight: bold;">👑 Admin</span>')
        elif obj.is_seller:
            return format_html('<span style="color: blue;">🏪 Vendeur</span>')
        else:
            return format_html('<span style="color: green;">👤 Client</span>')
    user_type.short_description = "Type"
    
    def is_active_status(self, obj):
        """Affiche le statut actif avec couleur"""
        if obj.is_active:
            icon = "✅" if obj.email_verified else "⚠️"
            status = "Vérifié" if obj.email_verified else "Non vérifié"
            return format_html(f'<span style="color: green;">{icon} {status}</span>')
        return format_html('<span style="color: red;">❌ Inactif</span>')
    is_active_status.short_description = "Statut"
    
    def created_at_formatted(self, obj):
        """Affiche la date de création formatée"""
        return obj.created_at.strftime('%d/%m/%Y')
    created_at_formatted.short_description = "Inscrit le"
    
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
    
    def verify_emails(self, request, queryset):
        """Vérifier les emails"""
        updated = queryset.update(email_verified=True)
        self.message_user(request, f"{updated} email(s) vérifié(s).")
    verify_emails.short_description = "Vérifier les emails"
    
    def changelist_view(self, request, extra_context=None):
        """Ajoute des statistiques"""
        extra_context = extra_context or {}
        
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        sellers = User.objects.filter(is_seller=True).count()
        admins = User.objects.filter(is_admin=True).count()
        verified_emails = User.objects.filter(email_verified=True).count()
        
        extra_context.update({
            'total_users': total_users,
            'active_users': active_users,
            'sellers': sellers,
            'admins': admins,
            'verified_emails': verified_emails,
        })
        
        return super().changelist_view(request, extra_context=extra_context)