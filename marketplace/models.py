# marketplace/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

# ============= USER MODEL CUSTOM =============
class User(AbstractUser):
    """Modèle utilisateur étendu pour le marketplace"""
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True, default='Port-au-Prince')
    country = models.CharField(max_length=50, blank=True, null=True, default='Haïti')
    is_seller = models.BooleanField(default=False)
    profile_image = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True, choices=[
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre')
    ])
    email_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    # CORRECTION CRITIQUE : Éviter les conflits de reverse accessors
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='marketplace_users',  # 🎯 AJOUT CRITIQUE
        related_query_name='marketplace_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='marketplace_users',  # 🎯 AJOUT CRITIQUE
        related_query_name='marketplace_user',
    )

    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

# ============= CATÉGORIES =============
class Category(models.Model):
    """Catégories de produits"""
    name = models.CharField(max_length=100)
    slug = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    detailed_description = models.TextField(blank=True, null=True)
    folder_path = models.CharField(max_length=255, blank=True, null=True)
    banner_image = models.CharField(max_length=255, blank=True, null=True)
    banner_image_path = models.CharField(max_length=255, blank=True, null=True)
    icon = models.CharField(max_length=255, blank=True, null=True)
    is_featured = models.BooleanField(default=False, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    sort_order = models.IntegerField(default=0, blank=True, null=True)
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.CharField(max_length=500, blank=True, null=True)
    parent = models.ForeignKey('self', models.CASCADE, blank=True, null=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

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

# ============= PRODUITS =============
class Product(models.Model):
    """Produits du marketplace"""
    name = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=200)
    short_description = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    detailed_description = models.TextField(blank=True, null=True)
    specifications = models.JSONField(blank=True, null=True)
    category = models.ForeignKey(Category, models.CASCADE, related_name='products')
    seller = models.ForeignKey(User, models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    stock_quantity = models.IntegerField(default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    min_stock_alert = models.IntegerField(default=5, blank=True, null=True, validators=[MinValueValidator(0)])
    sku = models.CharField(unique=True, max_length=50, blank=True, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    is_featured = models.BooleanField(default=False, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    is_digital = models.BooleanField(default=False, blank=True, null=True)
    requires_shipping = models.BooleanField(default=True, blank=True, null=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    video_url = models.CharField(max_length=255, blank=True, null=True)
    warranty_period = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    brand = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    origin_country = models.CharField(max_length=50, default='Haïti', blank=True, null=True)
    condition_type = models.CharField(max_length=20, default='new', blank=True, null=True, choices=[
        ('new', 'Neuf'),
        ('used', 'Utilisé'),
        ('refurbished', 'Reconditionné')
    ])
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"AF{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        """Retourne le prix promotionnel s'il existe, sinon le prix normal"""
        return self.promotional_price if self.promotional_price else self.price

    @property
    def in_stock(self):
        """Vérifie si le produit est en stock"""
        return self.stock_quantity and self.stock_quantity > 0

# ============= IMAGES PRODUITS =============
class ProductImage(models.Model):
    """Images des produits"""
    product = models.ForeignKey(Product, models.CASCADE, related_name='images')
    image_url = models.CharField(max_length=255)
    image_path = models.CharField(max_length=255)
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    is_primary = models.BooleanField(default=False, blank=True, null=True)
    sort_order = models.IntegerField(default=0, blank=True, null=True)
    image_type = models.CharField(max_length=20, default='gallery', blank=True, null=True, choices=[
        ('main', 'Principale'),
        ('gallery', 'Galerie'),
        ('thumbnail', 'Miniature')
    ])
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'product_images'
        verbose_name = 'Image Produit'
        verbose_name_plural = 'Images Produits'
        ordering = ['sort_order']

    def __str__(self):
        return f"Image de {self.product.name}"

# ============= PANIERS =============
class Cart(models.Model):
    """Paniers des utilisateurs"""
    user = models.ForeignKey(User, models.CASCADE, blank=True, null=True, related_name='carts')
    session_id = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'carts'
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'

    def __str__(self):
        return f"Panier de {self.user.username if self.user else self.session_id}"

class CartItem(models.Model):
    """Items dans les paniers"""
    cart = models.ForeignKey(Cart, models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    options = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Article Panier'
        verbose_name_plural = 'Articles Panier'
        unique_together = ['cart', 'product']

    def save(self, *args, **kwargs):
        self.price = self.product.current_price
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.quantity * self.price

# ============= COMMANDES =============
class Order(models.Model):
    """Commandes"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('processing', 'En traitement'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
        ('refunded', 'Remboursée'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'Payée'),
        ('failed', 'Échec'),
        ('refunded', 'Remboursée'),
    ]

    order_number = models.CharField(unique=True, max_length=50)
    user = models.ForeignKey(User, models.CASCADE, blank=True, null=True, related_name='orders')
    customer_name = models.CharField(max_length=100)
    customer_email = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=50, default='Port-au-Prince', blank=True, null=True)
    shipping_country = models.CharField(max_length=50, default='Haïti', blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)
    billing_city = models.CharField(max_length=50, blank=True, null=True)
    billing_country = models.CharField(max_length=50, default='Haïti', blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='HTG', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='moncash', blank=True, null=True)
    shipping_method = models.CharField(max_length=50, default='standard', blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery = models.DateField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    source = models.CharField(max_length=50, default='web', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"AF{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commande {self.order_number}"

class OrderItem(models.Model):
    """Articles dans les commandes"""
    order = models.ForeignKey(Order, models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50, blank=True, null=True)
    product_image = models.CharField(max_length=255, blank=True, null=True)
    product_options = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Article Commande'
        verbose_name_plural = 'Articles Commandes'

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.product.sku
        super().save(*args, **kwargs)

class OrderStatusHistory(models.Model):
    """Historique des statuts de commandes"""
    order = models.ForeignKey(Order, models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=50, blank=True, null=True)
    new_status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(User, models.CASCADE, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'order_status_history'
        verbose_name = 'Historique Statut'
        verbose_name_plural = 'Historique Statuts'

# ============= AVIS ET ÉVALUATIONS =============
class Review(models.Model):
    """Avis clients sur les produits"""
    product = models.ForeignKey(Product, models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, models.CASCADE, blank=True, null=True, related_name='reviews')
    order = models.ForeignKey(Order, models.CASCADE, blank=True, null=True)
    customer_name = models.CharField(max_length=100)
    customer_email = models.CharField(max_length=100, blank=True, null=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    pros = models.TextField(blank=True, null=True)
    cons = models.TextField(blank=True, null=True)
    is_verified_purchase = models.BooleanField(default=False, blank=True, null=True)
    is_approved = models.BooleanField(default=False, blank=True, null=True)
    helpful_count = models.IntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-created_at']

    def __str__(self):
        return f"Avis de {self.customer_name} sur {self.product.name}"

# ============= PAIEMENTS =============
class Transaction(models.Model):
    """Transactions de paiement"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complétée'),
        ('failed', 'Échec'),
        ('cancelled', 'Annulée'),
        ('refunded', 'Remboursée'),
    ]

    order = models.ForeignKey(Order, models.CASCADE, blank=True, null=True, related_name='transactions')
    transaction_id = models.CharField(unique=True, max_length=100, blank=True, null=True)
    moncash_order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_token = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='HTG', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='moncash', blank=True, null=True)
    gateway_response = models.JSONField(blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    callback_url = models.CharField(max_length=255, blank=True, null=True)
    return_url = models.CharField(max_length=255, blank=True, null=True)
    webhook_received_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transaction {self.transaction_id}"

# ============= CMS ET CONTENU =============
class Banner(models.Model):
    """Bannières du site"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=255)
    image_path = models.CharField(max_length=255)
    mobile_image_url = models.CharField(max_length=255, blank=True, null=True)
    link_url = models.CharField(max_length=255, blank=True, null=True)
    button_text = models.CharField(max_length=50, default='Découvrir', blank=True, null=True)
    button_color = models.CharField(max_length=7, default='#007bff', blank=True, null=True)
    text_color = models.CharField(max_length=7, default='#ffffff', blank=True, null=True)
    overlay_opacity = models.DecimalField(max_digits=3, decimal_places=2, default=0.3, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    sort_order = models.IntegerField(default=0, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    click_count = models.IntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'banners'
        verbose_name = 'Bannière'
        verbose_name_plural = 'Bannières'
        ordering = ['sort_order']

    def __str__(self):
        return self.title

class MediaContentSection(models.Model):
    """Sections de contenu média du site"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField()
    detailed_description = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    button_text = models.CharField(max_length=50, default='Voir les produits', blank=True, null=True)
    button_link = models.CharField(max_length=255, blank=True, null=True)
    category_tags = models.TextField(blank=True, null=True)
    product_tags = models.TextField(blank=True, null=True)
    background_color = models.CharField(max_length=7, blank=True, null=True)
    text_color = models.CharField(max_length=7, blank=True, null=True)
    layout_type = models.CharField(max_length=10, default='left', blank=True, null=True, choices=[
        ('left', 'Gauche'),
        ('right', 'Droite'),
        ('center', 'Centre')
    ])
    is_active = models.BooleanField(default=True, blank=True, null=True)
    sort_order = models.IntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'media_content_sections'
        verbose_name = 'Section Contenu'
        verbose_name_plural = 'Sections Contenu'
        ordering = ['sort_order']

    def __str__(self):
        return self.title

# ============= PAGES STATIQUES =============
class Page(models.Model):
    """Pages statiques du site"""
    title = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=200)
    content = models.TextField(blank=True, null=True)
    excerpt = models.TextField(blank=True, null=True)
    featured_image = models.CharField(max_length=255, blank=True, null=True)
    template = models.CharField(max_length=50, default='default', blank=True, null=True)
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    is_featured = models.BooleanField(default=False, blank=True, null=True)
    sort_order = models.IntegerField(default=0, blank=True, null=True)
    author = models.ForeignKey(User, models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'pages'
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# ============= NEWSLETTER =============
class NewsletterSubscriber(models.Model):
    """Abonnés à la newsletter"""
    email = models.CharField(unique=True, max_length=100)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)
    subscribed_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    unsubscribed_at = models.DateTimeField(blank=True, null=True)
    source = models.CharField(max_length=50, default='website', blank=True, null=True)

    class Meta:
        db_table = 'newsletter_subscribers'
        verbose_name = 'Abonné Newsletter'
        verbose_name_plural = 'Abonnés Newsletter'

    def __str__(self):
        return self.email

# ============= PARAMÈTRES SITE =============
class SiteSetting(models.Model):
    """Paramètres du site"""
    setting_key = models.CharField(unique=True, max_length=100)
    setting_value = models.TextField(blank=True, null=True)
    setting_type = models.CharField(max_length=10, default='text', blank=True, null=True, choices=[
        ('text', 'Texte'),
        ('number', 'Nombre'),
        ('boolean', 'Booléen'),
        ('json', 'JSON')
    ])
    description = models.TextField(blank=True, null=True)
    group_name = models.CharField(max_length=50, default='general', blank=True, null=True)
    is_public = models.BooleanField(default=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'site_settings'
        verbose_name = 'Paramètre Site'
        verbose_name_plural = 'Paramètres Site'

    def __str__(self):
        return f"{self.setting_key}: {self.setting_value}"