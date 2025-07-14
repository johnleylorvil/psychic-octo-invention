# ======================================
# apps/content/serializers.py
# ======================================

from rest_framework import serializers
from .models import Banner, Page, MediaContentSection


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'subtitle', 'description', 'image_url', 'mobile_image_url',
            'link_url', 'button_text', 'button_color', 'text_color', 'overlay_opacity',
            'sort_order', 'start_date', 'end_date'
        ]


class PageSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Page
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'featured_image',
            'template', 'meta_title', 'meta_description', 'author_name',
            'is_featured', 'created_at', 'updated_at'
        ]


class MediaContentSectionSerializer(serializers.ModelSerializer):
    related_categories = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaContentSection
        fields = [
            'id', 'title', 'subtitle', 'description', 'detailed_description',
            'image_url', 'button_text', 'button_link', 'background_color',
            'text_color', 'layout_type', 'sort_order', 'related_categories'
        ]
    
    def get_related_categories(self, obj):
        """Récupère les catégories liées basées sur category_tags"""
        if obj.category_tags:
            from products.models import Category
            try:
                category_ids = [int(id.strip()) for id in obj.category_tags.split(',') if id.strip().isdigit()]
                categories = Category.objects.filter(id__in=category_ids, is_active=True)
                return [{'id': cat.id, 'name': cat.name, 'slug': cat.slug} for cat in categories]
            except:
                pass
        return []
