# marketplace/models/user.py
"""
User management models for Afèpanou marketplace
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Modèle utilisateur étendu pour le marketplace"""
    
    # Personal Information
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True, default='Port-au-Prince')
    country = models.CharField(max_length=50, blank=True, null=True, default='Haïti')
    profile_image = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    
    # User Type and Status
    is_seller = models.BooleanField(default=False)
    is_premium_seller = models.BooleanField(default=False)
    seller_since = models.DateTimeField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Account Status
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    # Additional Information
    gender = models.CharField(
        max_length=10, 
        blank=True, 
        null=True, 
        choices=[
            ('M', 'Masculin'),
            ('F', 'Féminin'),
            ('O', 'Autre')
        ]
    )
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    # CORRECTION CRITIQUE : Éviter les conflits de reverse accessors
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='marketplace_users',
        related_query_name='marketplace_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='marketplace_users',
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
        """Return user's full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property 
    def has_complete_profile(self):
        """Check if user has complete profile information"""
        required_fields = [
            self.first_name,
            self.last_name,
            self.email,
            self.phone,
            self.address,
            self.city
        ]
        return all(field for field in required_fields)
    
    def get_display_name(self):
        """Return the best display name for the user"""
        if self.first_name and self.last_name:
            return self.full_name
        elif self.first_name:
            return self.first_name
        else:
            return self.username
    
    def activate_seller_account(self):
        """Activate seller account"""
        from django.utils import timezone
        if not self.is_seller:
            self.is_seller = True
            self.seller_since = timezone.now()
            self.save(update_fields=['is_seller', 'seller_since'])
    
    def deactivate_seller_account(self):
        """Deactivate seller account"""
        self.is_seller = False
        self.is_premium_seller = False
        self.save(update_fields=['is_seller', 'is_premium_seller'])
    
    def suspend_account(self, reason=""):
        """Suspend user account"""
        self.is_suspended = True
        self.suspension_reason = reason
        self.is_active = False
        self.save(update_fields=['is_suspended', 'suspension_reason', 'is_active'])
    
    def unsuspend_account(self):
        """Unsuspend user account"""
        self.is_suspended = False
        self.suspension_reason = ""
        self.is_active = True
        self.save(update_fields=['is_suspended', 'suspension_reason', 'is_active'])
    
    @property
    def is_verified_seller(self):
        """Check if seller has all verifications"""
        return (self.is_seller and 
                self.email_verified and 
                self.phone_verified and
                hasattr(self, 'vendor_profile') and 
                self.vendor_profile.is_verified)
    
    @property
    def seller_rating(self):
        """Get seller's average rating from all their products"""
        if not self.is_seller:
            return None
        
        from django.db.models import Avg
        reviews = self.products.filter(
            reviews__is_approved=True
        ).aggregate(avg_rating=Avg('reviews__rating'))
        
        return round(reviews['avg_rating'] or 0, 2)
    
    @property
    def total_products(self):
        """Get total number of products for seller"""
        if not self.is_seller:
            return 0
        return self.products.filter(is_active=True).count()
    
    @property
    def account_age_days(self):
        """Get account age in days"""
        from django.utils import timezone
        return (timezone.now() - self.date_joined).days