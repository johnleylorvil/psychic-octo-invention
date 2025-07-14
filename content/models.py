# ======================================
# apps/content/models.py
# ======================================

from django.db import models
from django.conf import settings


class Banner(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(null=True, blank=True)
    image_url = models.CharField(max_length=255)
    image_path = models.CharField(max_length=255)
    mobile_image_url = models.CharField(max_length=255, blank=True)
    link_url = models.CharField(max_length=255, blank=True)
    button_text = models.CharField(max_length=50, blank=True, default='Découvrir')
    button_color = models.CharField(max_length=7, blank=True, default='#007bff')
    text_color = models.CharField(max_length=7, blank=True, default='#ffffff')
    overlay_opacity = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, default=0.3)
    is_active = models.BooleanField(null=True, blank=True, default=True)
    sort_order = models.IntegerField(null=True, blank=True, default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    click_count = models.IntegerField(null=True, blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'banners'

    def __str__(self):
        return self.title


class Page(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField(null=True, blank=True)
    excerpt = models.TextField(null=True, blank=True)
    featured_image = models.CharField(max_length=255, blank=True)
    template = models.CharField(max_length=50, blank=True, default='default')
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(null=True, blank=True, default=True)
    is_featured = models.BooleanField(null=True, blank=True, default=False)
    sort_order = models.IntegerField(null=True, blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'pages'

    def __str__(self):
        return self.title


class MediaContentSection(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    detailed_description = models.TextField(null=True, blank=True)
    image_url = models.CharField(max_length=255, blank=True)
    image_path = models.CharField(max_length=255, blank=True)
    button_text = models.CharField(max_length=50, blank=True, default='Voir les produits')
    button_link = models.CharField(max_length=255, blank=True)
    category_tags = models.TextField(null=True, blank=True)
    product_tags = models.TextField(null=True, blank=True)
    background_color = models.CharField(max_length=7, blank=True)
    text_color = models.CharField(max_length=7, blank=True)
    layout_type = models.CharField(max_length=10, blank=True, default='left')
    is_active = models.BooleanField(null=True, blank=True, default=True)
    sort_order = models.IntegerField(null=True, blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'media_content_sections'

    def __str__(self):
        return self.title
