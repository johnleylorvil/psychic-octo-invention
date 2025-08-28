# marketplace/models/address.py
"""
Address management models for Afèpanou marketplace
"""

from django.db import models
from django.core.validators import RegexValidator
from .user import User
from ..validators import validate_haitian_phone_number, validate_postal_code_haiti
from ..constants import HAITI_DEPARTMENTS, HAITI_CITIES, COUNTRY_CHOICES


class Address(models.Model):
    """User addresses for shipping and billing"""
    
    ADDRESS_TYPE_CHOICES = [
        ('billing', 'Billing Address'),
        ('shipping', 'Shipping Address'),
        ('both', 'Billing & Shipping'),
    ]
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    
    # Address Type and Status
    address_type = models.CharField(
        max_length=10,
        choices=ADDRESS_TYPE_CHOICES,
        default='shipping'
    )
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Contact Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(
        max_length=20, 
        validators=[validate_haitian_phone_number]
    )
    email = models.EmailField(blank=True)
    
    # Address Details
    company_name = models.CharField(max_length=100, blank=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    department = models.CharField(
        max_length=50,
        blank=True,
        choices=HAITI_DEPARTMENTS
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        validators=[validate_postal_code_haiti]
    )
    country = models.CharField(
        max_length=2,
        choices=COUNTRY_CHOICES,
        default='HT'
    )
    
    # Additional Information
    delivery_instructions = models.TextField(blank=True)
    landmark = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Nearby landmark for easier delivery"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'addresses'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'address_type'],
                condition=models.Q(is_default=True),
                name='unique_default_address_per_type'
            )
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.country}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default address per type per user
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        """Get full name for address"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def full_address(self):
        """Get formatted full address"""
        parts = []
        
        if self.company_name:
            parts.append(self.company_name)
        
        parts.append(f"{self.first_name} {self.last_name}")
        parts.append(self.address_line1)
        
        if self.address_line2:
            parts.append(self.address_line2)
        
        city_part = self.city
        if self.department:
            city_part += f", {self.get_department_display()}"
        
        parts.append(city_part)
        
        if self.postal_code:
            parts.append(self.postal_code)
        
        parts.append(self.get_country_display())
        
        return '\n'.join(parts)
    
    @property
    def single_line_address(self):
        """Get address as single line"""
        parts = [self.address_line1]
        
        if self.address_line2:
            parts.append(self.address_line2)
        
        parts.append(self.city)
        
        if self.department:
            parts.append(self.get_department_display())
        
        if self.postal_code:
            parts.append(self.postal_code)
        
        return ', '.join(parts)
    
    @property
    def is_haiti_address(self):
        """Check if address is in Haiti"""
        return self.country == 'HT'
    
    def set_as_default(self):
        """Set this address as default for its type"""
        # Remove default from other addresses of same type
        Address.objects.filter(
            user=self.user,
            address_type=self.address_type
        ).exclude(pk=self.pk).update(is_default=False)
        
        # Set this as default
        self.is_default = True
        self.save(update_fields=['is_default'])
    
    def deactivate(self):
        """Deactivate this address"""
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    @classmethod
    def get_default_shipping_address(cls, user):
        """Get user's default shipping address"""
        return cls.objects.filter(
            user=user,
            address_type__in=['shipping', 'both'],
            is_default=True,
            is_active=True
        ).first()
    
    @classmethod
    def get_default_billing_address(cls, user):
        """Get user's default billing address"""
        return cls.objects.filter(
            user=user,
            address_type__in=['billing', 'both'],
            is_default=True,
            is_active=True
        ).first()
    
    @classmethod
    def get_user_addresses(cls, user, address_type=None):
        """Get all active addresses for user"""
        queryset = cls.objects.filter(user=user, is_active=True)
        
        if address_type:
            if address_type in ['shipping', 'billing']:
                queryset = queryset.filter(
                    address_type__in=[address_type, 'both']
                )
            else:
                queryset = queryset.filter(address_type=address_type)
        
        return queryset.order_by('-is_default', '-created_at')


class SavedLocation(models.Model):
    """Commonly used locations for faster address entry"""
    
    LOCATION_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_locations')
    
    # Location Details
    name = models.CharField(max_length=100)  # e.g., "Home", "Office", "Mom's House"
    location_type = models.CharField(
        max_length=10,
        choices=LOCATION_TYPE_CHOICES,
        default='other'
    )
    
    # Address Information (simplified)
    address = models.TextField()
    city = models.CharField(max_length=100)
    landmark = models.CharField(max_length=255, blank=True)
    coordinates = models.JSONField(
        blank=True, 
        null=True,
        help_text="GPS coordinates for precise location"
    )
    
    # Usage tracking
    use_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'saved_locations'
        verbose_name = 'Saved Location'
        verbose_name_plural = 'Saved Locations'
        ordering = ['-use_count', '-last_used']
    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    def increment_usage(self):
        """Increment usage count and update last used"""
        from django.utils import timezone
        self.use_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['use_count', 'last_used'])
    
    @property
    def full_address(self):
        """Get full address with landmark"""
        address_parts = [self.address, self.city]
        if self.landmark:
            address_parts.append(f"Near {self.landmark}")
        return ', '.join(address_parts)