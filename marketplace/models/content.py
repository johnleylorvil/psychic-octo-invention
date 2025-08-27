# marketplace/models/content.py
"""
Content management models for Afèpanou marketplace
"""

from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Banner(models.Model):
    """Bannières du site"""
    
    LAYOUT_CHOICES = [
        ('hero', 'Hero Banner'),
        ('carousel', 'Carousel'),
        ('sidebar', 'Sidebar'),
        ('footer', 'Footer'),
    ]
    
    # Content
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Media
    image_url = models.CharField(max_length=255)
    image_path = models.CharField(max_length=255)
    mobile_image_url = models.CharField(max_length=255, blank=True, null=True)
    
    # Action
    link_url = models.CharField(max_length=255, blank=True, null=True)
    button_text = models.CharField(
        max_length=50, 
        default='Découvrir', 
        blank=True, 
        null=True
    )
    
    # Styling
    button_color = models.CharField(
        max_length=7, 
        default='#E67E22', 
        blank=True, 
        null=True
    )
    text_color = models.CharField(
        max_length=7, 
        default='#ffffff', 
        blank=True, 
        null=True
    )
    overlay_opacity = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.3, 
        blank=True, 
        null=True
    )
    
    # Organization
    layout_type = models.CharField(
        max_length=20,
        choices=LAYOUT_CHOICES,
        default='hero',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True, blank=True, null=True)
    sort_order = models.IntegerField(default=0, blank=True, null=True)
    
    # Scheduling
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    
    # Analytics
    click_count = models.IntegerField(default=0, blank=True, null=True)
    view_count = models.IntegerField(default=0, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'banners'
        verbose_name = 'Bannière'
        verbose_name_plural = 'Bannières'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title
    
    @property
    def is_scheduled(self):
        """Check if banner has scheduling dates"""
        return self.start_date or self.end_date
    
    @property
    def is_currently_active(self):
        """Check if banner is currently active based on dates"""
        from django.utils import timezone
        now = timezone.now().date()
        
        if not self.is_active:
            return False
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True
    
    def increment_clicks(self):
        """Increment click counter"""
        self.click_count += 1
        self.save(update_fields=['click_count'])
    
    def increment_views(self):
        """Increment view counter"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class MediaContentSection(models.Model):
    """Sections de contenu média du site"""
    
    LAYOUT_CHOICES = [
        ('left', 'Image à Gauche'),
        ('right', 'Image à Droite'),
        ('center', 'Image Centrée'),
        ('background', 'Image en Arrière-plan'),
    ]
    
    # Content
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField()
    detailed_description = models.TextField(blank=True, null=True)
    
    # Media
    image_url = models.CharField(max_length=255, blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    
    # Action
    button_text = models.CharField(
        max_length=50, 
        default='Voir les produits', 
        blank=True, 
        null=True
    )
    button_link = models.CharField(max_length=255, blank=True, null=True)
    
    # Categories and Products
    category_tags = models.TextField(
        blank=True, 
        null=True,
        help_text="Tags de catégories séparés par des virgules"
    )
    product_tags = models.TextField(
        blank=True, 
        null=True,
        help_text="Tags de produits séparés par des virgules"
    )
    
    # Styling
    background_color = models.CharField(max_length=7, blank=True, null=True)
    text_color = models.CharField(max_length=7, blank=True, null=True)
    layout_type = models.CharField(
        max_length=20, 
        default='left', 
        blank=True, 
        null=True, 
        choices=LAYOUT_CHOICES
    )
    
    # Organization
    is_active = models.BooleanField(default=True, blank=True, null=True)
    sort_order = models.IntegerField(default=0, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'media_content_sections'
        verbose_name = 'Section Contenu'
        verbose_name_plural = 'Sections Contenu'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title
    
    @property
    def category_list(self):
        """Get list of category tags"""
        if self.category_tags:
            return [tag.strip() for tag in self.category_tags.split(',')]
        return []
    
    @property
    def product_list(self):
        """Get list of product tags"""
        if self.product_tags:
            return [tag.strip() for tag in self.product_tags.split(',')]
        return []


class Page(models.Model):
    """Pages statiques du site"""
    
    TEMPLATE_CHOICES = [
        ('default', 'Défaut'),
        ('full_width', 'Pleine Largeur'),
        ('sidebar_left', 'Sidebar Gauche'),
        ('sidebar_right', 'Sidebar Droite'),
        ('landing', 'Page d\'Atterrissage'),
    ]
    
    # Content
    title = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=200)
    content = models.TextField(blank=True, null=True)
    excerpt = models.TextField(
        blank=True, 
        null=True,
        help_text="Court résumé de la page"
    )
    
    # Media
    featured_image = models.CharField(max_length=255, blank=True, null=True)
    
    # Template and Layout
    template = models.CharField(
        max_length=50, 
        default='default', 
        blank=True, 
        null=True,
        choices=TEMPLATE_CHOICES
    )
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.CharField(max_length=500, blank=True, null=True)
    
    # Status and Organization
    is_active = models.BooleanField(default=True, blank=True, null=True)
    is_featured = models.BooleanField(default=False, blank=True, null=True)
    sort_order = models.IntegerField(default=0, blank=True, null=True)
    
    # Author
    author = models.ForeignKey(
        'User', 
        models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='authored_pages'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'pages'
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        ordering = ['sort_order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Get page URL"""
        return reverse('page_detail', kwargs={'slug': self.slug})
    
    @property
    def word_count(self):
        """Get approximate word count"""
        if self.content:
            return len(self.content.split())
        return 0
    
    @property
    def reading_time(self):
        """Estimate reading time in minutes (assuming 200 words per minute)"""
        words = self.word_count
        if words == 0:
            return 0
        return max(1, round(words / 200))