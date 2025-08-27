# marketplace/models/order.py
"""
Order and cart models for Afèpanou marketplace
"""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid

from .managers import CartManager, OrderManager


class Cart(models.Model):
    """Paniers des utilisateurs"""
    
    # User/Session Association
    user = models.ForeignKey(
        'User', 
        models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='carts'
    )
    session_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    objects = CartManager()

    class Meta:
        db_table = 'carts'
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'

    def __str__(self):
        return f"Panier de {self.user.username if self.user else self.session_id}"
    
    def save(self, *args, **kwargs):
        # Set expiration time for session carts (24 hours)
        if not self.user and not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)
    
    @property
    def total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        """Get cart subtotal"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def is_empty(self):
        """Check if cart is empty"""
        return not self.items.exists()
    
    def clear(self):
        """Clear all items from cart"""
        self.items.all().delete()
    
    def get_or_create_item(self, product, quantity=1, **options):
        """Get existing cart item or create new one"""
        item, created = self.items.get_or_create(
            product=product,
            defaults={
                'quantity': quantity,
                'price': product.current_price,
                'options': options or {}
            }
        )
        
        if not created:
            item.quantity += quantity
            item.save()
        
        return item


class CartItem(models.Model):
    """Items dans les paniers"""
    
    # Relationships
    cart = models.ForeignKey(Cart, models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', models.CASCADE)
    
    # Item Details
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    options = models.JSONField(blank=True, null=True)  # Size, color, etc.
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Article Panier'
        verbose_name_plural = 'Articles Panier'
        unique_together = ['cart', 'product']

    def save(self, *args, **kwargs):
        # Always use current product price
        self.price = self.product.current_price
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        """Get total price for this item"""
        return self.quantity * self.price
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


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
    
    # Order Identification
    order_number = models.CharField(unique=True, max_length=50)
    user = models.ForeignKey(
        'User', 
        models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='orders'
    )
    
    # Customer Information
    customer_name = models.CharField(max_length=100)
    customer_email = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    
    # Shipping Address
    shipping_address = models.TextField()
    shipping_city = models.CharField(
        max_length=50, 
        default='Port-au-Prince', 
        blank=True, 
        null=True
    )
    shipping_country = models.CharField(
        max_length=50, 
        default='Haïti', 
        blank=True, 
        null=True
    )
    
    # Billing Address
    billing_address = models.TextField(blank=True, null=True)
    billing_city = models.CharField(max_length=50, blank=True, null=True)
    billing_country = models.CharField(
        max_length=50, 
        default='Haïti', 
        blank=True, 
        null=True
    )
    
    # Order Totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        blank=True, 
        null=True
    )
    tax_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        blank=True, 
        null=True
    )
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        blank=True, 
        null=True
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='HTG', blank=True, null=True)
    
    # Order Status
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending', 
        blank=True, 
        null=True
    )
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending', 
        blank=True, 
        null=True
    )
    
    # Payment and Shipping
    payment_method = models.CharField(
        max_length=50, 
        default='moncash', 
        blank=True, 
        null=True
    )
    shipping_method = models.CharField(
        max_length=50, 
        default='standard', 
        blank=True, 
        null=True
    )
    
    # Tracking and Delivery
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery = models.DateField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    # Additional Information
    notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    source = models.CharField(max_length=50, default='web', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    objects = OrderManager()

    class Meta:
        db_table = 'orders'
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'payment_status']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['order_number']),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"AF{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Commande {self.order_number}"
    
    @property
    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in ['pending', 'confirmed']
    
    @property
    def is_paid(self):
        """Check if order is paid"""
        return self.payment_status == 'paid'
    
    @property
    def is_delivered(self):
        """Check if order is delivered"""
        return self.status == 'delivered'
    
    def get_status_display_class(self):
        """Get CSS class for status display"""
        status_classes = {
            'pending': 'warning',
            'confirmed': 'info',
            'processing': 'info',
            'shipped': 'primary',
            'delivered': 'success',
            'cancelled': 'danger',
            'refunded': 'secondary'
        }
        return status_classes.get(self.status, 'secondary')


class OrderItem(models.Model):
    """Articles dans les commandes"""
    
    # Relationships
    order = models.ForeignKey(Order, models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', models.CASCADE)
    
    # Item Details
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Product Snapshot (for order history)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50, blank=True, null=True)
    product_image = models.CharField(max_length=255, blank=True, null=True)
    product_options = models.JSONField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Article Commande'
        verbose_name_plural = 'Articles Commandes'

    def save(self, *args, **kwargs):
        # Calculate total and save product snapshot
        self.total_price = self.quantity * self.unit_price
        
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.product.sku
        if not self.product_image and self.product.primary_image:
            self.product_image = self.product.primary_image.image_url
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name}"


class OrderStatusHistory(models.Model):
    """Historique des statuts de commandes"""
    
    # Relationships
    order = models.ForeignKey(Order, models.CASCADE, related_name='status_history')
    changed_by = models.ForeignKey('User', models.CASCADE, blank=True, null=True)
    
    # Status Change Details
    old_status = models.CharField(max_length=50, blank=True, null=True)
    new_status = models.CharField(max_length=50)
    comment = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'order_status_history'
        verbose_name = 'Historique Statut'
        verbose_name_plural = 'Historique Statuts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order.order_number}: {self.old_status} → {self.new_status}"