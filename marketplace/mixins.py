# marketplace/mixins.py
"""
Reusable model mixins for Afèpanou marketplace
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class TimestampMixin(models.Model):
    """Add created_at and updated_at fields to models"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """Add soft delete functionality to models"""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete the object"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=['is_deleted', 'deleted_at'])
    
    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the object"""
        super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """Restore a soft deleted object"""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


class ActiveStatusMixin(models.Model):
    """Add active status functionality to models"""
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
    
    def activate(self):
        """Activate the object"""
        self.is_active = True
        self.save(update_fields=['is_active'])
    
    def deactivate(self):
        """Deactivate the object"""
        self.is_active = False
        self.save(update_fields=['is_active'])


class SEOMixin(models.Model):
    """Add SEO fields to models"""
    meta_title = models.CharField(
        max_length=60, 
        blank=True, 
        help_text="SEO title (max 60 characters)"
    )
    meta_description = models.TextField(
        max_length=160, 
        blank=True, 
        help_text="SEO meta description (max 160 characters)"
    )
    
    class Meta:
        abstract = True


class SlugMixin(models.Model):
    """Add slug field to models"""
    slug = models.SlugField(
        max_length=100, 
        unique=True, 
        help_text="URL-friendly version of the name"
    )
    
    class Meta:
        abstract = True


class PositionMixin(models.Model):
    """Add display order/position functionality"""
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        abstract = True
        ordering = ['display_order']


class AuditMixin(models.Model):
    """Add audit trail fields to models"""
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_%(class)s_set'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_%(class)s_set'
    )
    
    class Meta:
        abstract = True


class ViewCountMixin(models.Model):
    """Add view count functionality to models"""
    view_count = models.PositiveIntegerField(default=0)
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def increment_view_count(self):
        """Increment the view count"""
        self.view_count += 1
        self.last_viewed_at = timezone.now()
        self.save(update_fields=['view_count', 'last_viewed_at'])


class AddressMixin(models.Model):
    """Add address fields to models"""
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=2, default='HT')
    
    class Meta:
        abstract = True
    
    @property
    def full_address(self):
        """Return formatted full address"""
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.postal_code:
            parts.append(self.postal_code)
        return ', '.join(parts)


class ContactMixin(models.Model):
    """Add contact information fields to models"""
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    class Meta:
        abstract = True


class ImageMixin(models.Model):
    """Add image handling to models"""
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    image_alt_text = models.CharField(
        max_length=255, 
        blank=True,
        help_text="Alternative text for accessibility"
    )
    
    class Meta:
        abstract = True
    
    @property
    def has_image(self):
        """Check if model has an image"""
        return bool(self.image)


class PricingMixin(models.Model):
    """Add pricing fields to models"""
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    promotional_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    class Meta:
        abstract = True
    
    @property
    def effective_price(self):
        """Get the effective selling price"""
        if self.promotional_price and self.promotional_price < self.price:
            return self.promotional_price
        return self.price
    
    @property
    def discount_amount(self):
        """Get discount amount if promotional price exists"""
        if self.promotional_price and self.promotional_price < self.price:
            return self.price - self.promotional_price
        return 0
    
    @property
    def discount_percentage(self):
        """Get discount percentage if promotional price exists"""
        discount = self.discount_amount
        if discount > 0:
            return round((discount / self.price) * 100, 2)
        return 0


class RatingMixin(models.Model):
    """Add rating functionality to models"""
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00
    )
    rating_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        abstract = True
    
    @property
    def rating_stars(self):
        """Get rating as number of stars (1-5)"""
        return round(float(self.average_rating))


class PublishableMixin(models.Model):
    """Add publishing functionality to models"""
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def publish(self):
        """Publish the object"""
        self.is_published = True
        self.published_at = timezone.now()
        self.save(update_fields=['is_published', 'published_at'])
    
    def unpublish(self):
        """Unpublish the object"""
        self.is_published = False
        self.save(update_fields=['is_published'])
    
    @property
    def is_live(self):
        """Check if object is published and active"""
        return (
            self.is_published and 
            hasattr(self, 'is_active') and 
            self.is_active
        )