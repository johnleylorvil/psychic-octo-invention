# marketplace/models/product.py
"""
Product catalog models for Afèpanou marketplace
"""

from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
import uuid

from .managers import CategoryManager, ProductManager


class Category(models.Model):
    """Catégories de produits"""
    
    # Basic Information
    name = models.CharField(max_length=100)
    slug = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    detailed_description = models.TextField(blank=True, null=True)
    
    # Imagery and Branding
    folder_path = models.CharField(max_length=255, blank=True, null=True)
    banner_image = models.CharField(max_length=255, blank=True, null=True)
    banner_image_path = models.CharField(max_length=255, blank=True, null=True)
    icon = models.CharField(max_length=255, blank=True, null=True)
    
    # Status and Ordering
    is_featured = models.BooleanField(default=False, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    sort_order = models.IntegerField(default=0, blank=True, null=True)
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.CharField(max_length=500, blank=True, null=True)
    
    # Hierarchy
    parent = models.ForeignKey(
        'self', 
        models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='children'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    objects = CategoryManager()

    class Meta:
        db_table = 'categories'
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['sort_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    @property
    def product_count(self):
        """Get total number of active products in this category"""
        return self.products.filter(is_active=True).count()
    
    @property
    def subcategory_count(self):
        """Get number of subcategories"""
        return self.children.filter(is_active=True).count()
    
    def get_absolute_url(self):
        """Get category detail URL"""
        return reverse('category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    """Produits du marketplace"""
    
    CONDITION_CHOICES = [
        ('new', 'Neuf'),
        ('used', 'Utilisé'),
        ('refurbished', 'Reconditionné')
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=200)
    short_description = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    detailed_description = models.TextField(blank=True, null=True)
    specifications = models.JSONField(blank=True, null=True)
    
    # Relationships
    category = models.ForeignKey(Category, models.CASCADE, related_name='products')
    seller = models.ForeignKey('User', models.CASCADE, related_name='products')
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    promotional_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        validators=[MinValueValidator(0)]
    )
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        validators=[MinValueValidator(0)]
    )
    
    # Inventory Management
    stock_quantity = models.IntegerField(
        default=0, 
        blank=True, 
        null=True, 
        validators=[MinValueValidator(0)]
    )
    min_stock_alert = models.IntegerField(
        default=5, 
        blank=True, 
        null=True, 
        validators=[MinValueValidator(0)]
    )
    sku = models.CharField(unique=True, max_length=50, blank=True, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    
    # Status and Features
    is_featured = models.BooleanField(default=False, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    is_digital = models.BooleanField(default=False, blank=True, null=True)
    requires_shipping = models.BooleanField(default=True, blank=True, null=True)
    
    # Physical Properties
    weight = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        validators=[MinValueValidator(0)]
    )
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional Information
    tags = models.TextField(blank=True, null=True)
    video_url = models.CharField(max_length=255, blank=True, null=True)
    warranty_period = models.IntegerField(
        blank=True, 
        null=True, 
        validators=[MinValueValidator(0)]
    )
    
    # Product Details
    brand = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    origin_country = models.CharField(max_length=50, default='Haïti', blank=True, null=True)
    condition_type = models.CharField(
        max_length=20, 
        default='new', 
        blank=True, 
        null=True, 
        choices=CONDITION_CHOICES
    )
    
    # SEO
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.CharField(max_length=500, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    objects = ProductManager()

    class Meta:
        db_table = 'products'
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['seller', 'is_active']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"AF{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Retourne l'URL pour la page de détail de ce produit"""
        return reverse('product_detail', kwargs={'slug': self.slug})

    @property
    def primary_image(self):
        """Retourne l'objet ProductImage marqué comme principal, ou le premier de la liste"""
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        return self.images.first()

    @property
    def current_price(self):
        """Retourne le prix promotionnel s'il existe, sinon le prix normal"""
        return self.promotional_price if self.promotional_price is not None else self.price

    @property
    def in_stock(self):
        """Vérifie si le produit est en stock"""
        return self.stock_quantity and self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        """Check if product is low on stock"""
        return (self.stock_quantity is not None and 
                self.min_stock_alert is not None and 
                self.stock_quantity <= self.min_stock_alert)
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if promotional price exists"""
        if self.promotional_price and self.promotional_price < self.price:
            discount = ((self.price - self.promotional_price) / self.price) * 100
            return round(discount, 1)
        return 0
    
    @property
    def average_rating(self):
        """Get average rating from reviews"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating']
        return 0
    
    @property
    def review_count(self):
        """Get total number of approved reviews"""
        return self.reviews.filter(is_approved=True).count()


class ProductImage(models.Model):
    """Images des produits"""
    
    IMAGE_TYPE_CHOICES = [
        ('main', 'Principale'),
        ('gallery', 'Galerie'),
        ('thumbnail', 'Miniature')
    ]
    
    # Relationships
    product = models.ForeignKey(Product, models.CASCADE, related_name='images')
    
    # Image Information
    image_url = models.CharField(max_length=255)
    image_path = models.CharField(max_length=255)
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    
    # Organization
    is_primary = models.BooleanField(default=False, blank=True, null=True)
    sort_order = models.IntegerField(default=0, blank=True, null=True)
    image_type = models.CharField(
        max_length=20, 
        default='gallery', 
        blank=True, 
        null=True, 
        choices=IMAGE_TYPE_CHOICES
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'product_images'
        verbose_name = 'Image Produit'
        verbose_name_plural = 'Images Produits'
        ordering = ['sort_order']

    def __str__(self):
        return f"Image de {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, 
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)