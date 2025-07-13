# ======================================
# apps/content/admin.py
# ======================================

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from .models import Banner, Page, MediaContentSection


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'is_active_status', 'sort_order', 'click_count', 'date_range', 'created_at_formatted']
    list_filter = ['is_active', 'created_at', 'start_date', 'end_date']
    search_fields = ['title', 'subtitle', 'description']
    readonly_fields = ['click_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'subtitle', 'description')
        }),
        ('Images', {
            'fields': ('image_url', 'image_path', 'mobile_image_url')
        }),
        ('Action', {
            'fields': ('link_url', 'button_text', 'button_color')
        }),
        ('Style', {
            'fields': ('text_color', 'overlay_opacity')
        }),
        ('Configuration', {
            'fields': ('is_active', 'sort_order')
        }),
        ('Planification', {
            'fields': ('start_date', 'end_date')
        }),
        ('Statistiques', {
            'fields': ('click_count',),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_banners', 'deactivate_banners', 'reset_click_count']
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" width="60" height="40" style="object-fit: cover; border-radius: 4px;" />',
                obj.image_url
            )
        return "Pas d'image"
    image_preview.short_description = "Aperçu"
    
    def is_active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Actif</span>')
        return format_html('<span style="color: red;">✗ Inactif</span>')
    is_active_status.short_description = "Statut"
    
    def date_range(self, obj):
        if obj.start_date and obj.end_date:
            return f"{obj.start_date.strftime('%d/%m/%Y')} - {obj.end_date.strftime('%d/%m/%Y')}"
        elif obj.start_date:
            return f"À partir du {obj.start_date.strftime('%d/%m/%Y')}"
        elif obj.end_date:
            return f"Jusqu'au {obj.end_date.strftime('%d/%m/%Y')}"
        return "Permanent"
    date_range.short_description = "Période"
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = "Créé le"
    
    def activate_banners(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} bannière(s) activée(s).")
    activate_banners.short_description = "Activer les bannières"
    
    def deactivate_banners(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} bannière(s) désactivée(s).")
    deactivate_banners.short_description = "Désactiver les bannières"
    
    def reset_click_count(self, request, queryset):
        updated = queryset.update(click_count=0)
        self.message_user(request, f"Compteurs remis à zéro pour {updated} bannière(s).")
    reset_click_count.short_description = "Remettre compteurs à zéro"


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author_link', 'is_active_status', 'is_featured_status', 'template', 'created_at_formatted']
    list_filter = ['is_active', 'is_featured', 'template', 'author', 'created_at']
    search_fields = ['title', 'slug', 'content', 'excerpt']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'slug', 'author', 'excerpt', 'content')
        }),
        ('Média', {
            'fields': ('featured_image',)
        }),
        ('Configuration', {
            'fields': ('template', 'is_active', 'is_featured', 'sort_order')
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
    
    actions = ['make_featured', 'remove_featured', 'activate_pages']
    
    def author_link(self, obj):
        if obj.author:
            url = reverse("admin:users_user_change", args=[obj.author.pk])
            return format_html('<a href="{}">{}</a>', url, obj.author.username)
        return "Aucun auteur"
    author_link.short_description = "Auteur"
    
    def is_active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Actif</span>')
        return format_html('<span style="color: red;">✗ Inactif</span>')
    is_active_status.short_description = "Statut"
    
    def is_featured_status(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: gold;">★ Vedette</span>')
        return "-"
    is_featured_status.short_description = "Vedette"
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = "Créé le"
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} page(s) marquée(s) comme vedette.")
    make_featured.short_description = "Marquer comme vedette"
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f"{updated} page(s) retirée(s) des vedettes.")
    remove_featured.short_description = "Retirer des vedettes"


@admin.register(MediaContentSection)
class MediaContentSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'layout_type', 'is_active_status', 'sort_order', 'created_at_formatted']
    list_filter = ['is_active', 'layout_type', 'created_at']
    search_fields = ['title', 'subtitle', 'description', 'category_tags', 'product_tags']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contenu', {
            'fields': ('title', 'subtitle', 'description', 'detailed_description')
        }),
        ('Média', {
            'fields': ('image_url', 'image_path')
        }),
        ('Action', {
            'fields': ('button_text', 'button_link')
        }),
        ('Tags et filtres', {
            'fields': ('category_tags', 'product_tags')
        }),
        ('Style', {
            'fields': ('background_color', 'text_color', 'layout_type')
        }),
        ('Configuration', {
            'fields': ('is_active', 'sort_order')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_sections', 'deactivate_sections']
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" width="60" height="40" style="object-fit: cover; border-radius: 4px;" />',
                obj.image_url
            )
        return "Pas d'image"
    image_preview.short_description = "Aperçu"
    
    def is_active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Actif</span>')
        return format_html('<span style="color: red;">✗ Inactif</span>')
    is_active_status.short_description = "Statut"
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    created_at_formatted.short_description = "Créé le"
    
    def activate_sections(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} section(s) activée(s).")
    activate_sections.short_description = "Activer les sections"
    
    def deactivate_sections(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} section(s) désactivée(s).")
    deactivate_sections.short_description = "Désactiver les sections"