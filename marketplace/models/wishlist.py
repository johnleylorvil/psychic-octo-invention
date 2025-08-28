# marketplace/models/wishlist.py
"""
Wishlist and user favorites models for Afèpanou marketplace
"""

from django.db import models
from django.core.exceptions import ValidationError
from .user import User
from .product import Product


class Wishlist(models.Model):
    """User wishlist for saving favorite products"""
    
    # Relationships
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    
    # Settings
    is_public = models.BooleanField(
        default=False, 
        help_text="Allow others to view this wishlist"
    )
    name = models.CharField(
        max_length=100, 
        default="My Wishlist",
        help_text="Custom name for this wishlist"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this wishlist"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wishlists'
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'
    
    def __str__(self):
        return f"{self.user.username}'s {self.name}"
    
    @property
    def item_count(self):
        """Get total number of items in wishlist"""
        return self.items.filter(is_active=True).count()
    
    @property
    def total_value(self):
        """Calculate total value of all wishlist items"""
        total = 0
        for item in self.items.filter(is_active=True):
            if item.product.is_active:
                total += item.product.current_price
        return total
    
    def add_product(self, product, notes=""):
        """Add product to wishlist"""
        item, created = WishlistItem.objects.get_or_create(
            wishlist=self,
            product=product,
            defaults={'notes': notes}
        )
        
        if not created and not item.is_active:
            # Reactivate if previously removed
            item.is_active = True
            item.notes = notes
            item.save()
        
        return item
    
    def remove_product(self, product):
        """Remove product from wishlist"""
        try:
            item = self.items.get(product=product)
            item.is_active = False
            item.save()
            return True
        except WishlistItem.DoesNotExist:
            return False
    
    def has_product(self, product):
        """Check if product is in wishlist"""
        return self.items.filter(product=product, is_active=True).exists()
    
    def clear_unavailable_items(self):
        """Remove items for products that are no longer available"""
        unavailable_items = self.items.filter(
            is_active=True,
            product__is_active=False
        )
        count = unavailable_items.count()
        unavailable_items.update(is_active=False)
        return count
    
    def get_available_items(self):
        """Get all active wishlist items with available products"""
        return self.items.filter(
            is_active=True,
            product__is_active=True
        ).select_related('product')


class WishlistItem(models.Model):
    """Individual items in a wishlist"""
    
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Urgent'),
    ]
    
    # Relationships
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    
    # Item Details
    notes = models.TextField(
        blank=True,
        help_text="Personal notes about this item"
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=2,
        help_text="Purchase priority level"
    )
    target_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Desired price to purchase at"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_purchased = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wishlist_items'
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        ordering = ['-priority', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['wishlist', 'product'],
                condition=models.Q(is_active=True),
                name='unique_active_wishlist_item'
            )
        ]
    
    def __str__(self):
        return f"{self.product.name} in {self.wishlist.name}"
    
    def clean(self):
        """Validate wishlist item"""
        if self.target_price and self.target_price <= 0:
            raise ValidationError("Target price must be greater than zero")
    
    def mark_as_purchased(self):
        """Mark item as purchased"""
        from django.utils import timezone
        self.is_purchased = True
        self.purchased_at = timezone.now()
        self.save(update_fields=['is_purchased', 'purchased_at'])
    
    @property
    def is_price_target_met(self):
        """Check if current price meets target price"""
        if not self.target_price:
            return False
        return self.product.current_price <= self.target_price
    
    @property
    def price_difference(self):
        """Calculate difference between current price and target price"""
        if not self.target_price:
            return None
        return self.product.current_price - self.target_price
    
    @property
    def savings_potential(self):
        """Calculate potential savings if bought at target price"""
        if not self.target_price:
            return 0
        return max(0, self.product.current_price - self.target_price)


class WishlistCollection(models.Model):
    """Named collections within a user's wishlist"""
    
    # Relationships
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='collections')
    
    # Collection Details
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7,
        default="#007bff",
        help_text="Hex color code for collection theme"
    )
    
    # Products in this collection
    products = models.ManyToManyField(
        Product,
        through='WishlistCollectionItem',
        related_name='wishlist_collections'
    )
    
    # Settings
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wishlist_collections'
        verbose_name = 'Wishlist Collection'
        verbose_name_plural = 'Wishlist Collections'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.wishlist.user.username})"
    
    @property
    def item_count(self):
        """Get number of items in collection"""
        return self.collection_items.filter(is_active=True).count()
    
    @property
    def total_value(self):
        """Calculate total value of collection"""
        total = 0
        for item in self.collection_items.filter(is_active=True):
            total += item.product.current_price
        return total


class WishlistCollectionItem(models.Model):
    """Items within a wishlist collection"""
    
    # Relationships
    collection = models.ForeignKey(
        WishlistCollection, 
        on_delete=models.CASCADE, 
        related_name='collection_items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'wishlist_collection_items'
        verbose_name = 'Collection Item'
        verbose_name_plural = 'Collection Items'
        constraints = [
            models.UniqueConstraint(
                fields=['collection', 'product'],
                condition=models.Q(is_active=True),
                name='unique_active_collection_item'
            )
        ]
    
    def __str__(self):
        return f"{self.product.name} in {self.collection.name}"


class ProductAlert(models.Model):
    """Price and availability alerts for products"""
    
    ALERT_TYPE_CHOICES = [
        ('price_drop', 'Price Drop'),
        ('back_in_stock', 'Back in Stock'),
        ('low_stock', 'Low Stock Warning'),
        ('price_target', 'Target Price Reached'),
    ]
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_alerts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alerts')
    
    # Alert Configuration
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    target_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(blank=True, null=True)
    
    # Notification preferences
    notify_email = models.BooleanField(default=True)
    notify_sms = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_alerts'
        verbose_name = 'Product Alert'
        verbose_name_plural = 'Product Alerts'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product', 'alert_type'],
                condition=models.Q(is_active=True),
                name='unique_active_product_alert'
            )
        ]
    
    def __str__(self):
        return f"{self.get_alert_type_display()} for {self.product.name}"
    
    def trigger_alert(self):
        """Mark alert as triggered"""
        from django.utils import timezone
        self.is_triggered = True
        self.triggered_at = timezone.now()
        self.save(update_fields=['is_triggered', 'triggered_at'])
    
    def should_trigger(self):
        """Check if alert conditions are met"""
        if self.is_triggered or not self.is_active:
            return False
        
        if self.alert_type == 'price_drop' and self.target_price:
            return self.product.current_price <= self.target_price
        elif self.alert_type == 'back_in_stock':
            return self.product.in_stock
        elif self.alert_type == 'low_stock':
            return self.product.is_low_stock
        elif self.alert_type == 'price_target' and self.target_price:
            return self.product.current_price <= self.target_price
        
        return False