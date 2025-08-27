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
    email_verified = models.BooleanField(default=False)
    
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