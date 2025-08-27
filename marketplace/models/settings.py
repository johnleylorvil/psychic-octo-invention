# marketplace/models/settings.py
"""
Site settings and configuration models for Afèpanou marketplace
"""

from django.db import models
from django.core.cache import cache
import json


class SiteSettingManager(models.Manager):
    """Custom manager for SiteSetting model"""
    
    def get_value(self, key, default=None):
        """Get setting value with caching"""
        cache_key = f"site_setting_{key}"
        value = cache.get(cache_key)
        
        if value is None:
            try:
                setting = self.get(setting_key=key)
                value = setting.get_typed_value()
                # Cache for 1 hour
                cache.set(cache_key, value, 3600)
            except self.model.DoesNotExist:
                value = default
        
        return value
    
    def set_value(self, key, value, setting_type='text', description=None):
        """Set setting value and update cache"""
        setting, created = self.get_or_create(
            setting_key=key,
            defaults={
                'setting_value': str(value),
                'setting_type': setting_type,
                'description': description
            }
        )
        
        if not created:
            setting.setting_value = str(value)
            setting.setting_type = setting_type
            if description:
                setting.description = description
            setting.save()
        
        # Update cache
        cache_key = f"site_setting_{key}"
        cache.set(cache_key, setting.get_typed_value(), 3600)
        
        return setting
    
    def by_group(self, group_name):
        """Get settings by group"""
        return self.filter(group_name=group_name)
    
    def public_settings(self):
        """Get public settings (safe to expose to frontend)"""
        return self.filter(is_public=True)


class SiteSetting(models.Model):
    """Paramètres du site"""
    
    SETTING_TYPE_CHOICES = [
        ('text', 'Texte'),
        ('number', 'Nombre'),
        ('boolean', 'Booléen'),
        ('json', 'JSON'),
        ('email', 'Email'),
        ('url', 'URL'),
        ('color', 'Couleur'),
        ('image', 'Image'),
    ]
    
    GROUP_CHOICES = [
        ('general', 'Général'),
        ('appearance', 'Apparence'),
        ('commerce', 'Commerce'),
        ('payments', 'Paiements'),
        ('shipping', 'Livraison'),
        ('email', 'Email'),
        ('social', 'Réseaux Sociaux'),
        ('seo', 'SEO'),
        ('analytics', 'Analytiques'),
        ('security', 'Sécurité'),
    ]
    
    # Setting Information
    setting_key = models.CharField(unique=True, max_length=100)
    setting_value = models.TextField(blank=True, null=True)
    setting_type = models.CharField(
        max_length=20, 
        default='text', 
        blank=True, 
        null=True, 
        choices=SETTING_TYPE_CHOICES
    )
    
    # Metadata
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Description de ce paramètre"
    )
    group_name = models.CharField(
        max_length=50, 
        default='general', 
        blank=True, 
        null=True,
        choices=GROUP_CHOICES
    )
    
    # Visibility
    is_public = models.BooleanField(
        default=False, 
        blank=True, 
        null=True,
        help_text="Peut être exposé au frontend"
    )
    is_required = models.BooleanField(default=False, blank=True, null=True)
    
    # Validation
    validation_rules = models.JSONField(
        blank=True,
        null=True,
        help_text="Règles de validation JSON"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    objects = SiteSettingManager()

    class Meta:
        db_table = 'site_settings'
        verbose_name = 'Paramètre Site'
        verbose_name_plural = 'Paramètres Site'
        ordering = ['group_name', 'setting_key']

    def __str__(self):
        return f"{self.setting_key}: {self.setting_value}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Clear cache when setting is updated
        cache_key = f"site_setting_{self.setting_key}"
        cache.delete(cache_key)
    
    def get_typed_value(self):
        """Get setting value converted to appropriate type"""
        if not self.setting_value:
            return None
        
        try:
            if self.setting_type == 'boolean':
                return self.setting_value.lower() in ('true', '1', 'yes', 'on')
            elif self.setting_type == 'number':
                if '.' in self.setting_value:
                    return float(self.setting_value)
                return int(self.setting_value)
            elif self.setting_type == 'json':
                return json.loads(self.setting_value)
            else:
                return self.setting_value
        except (ValueError, json.JSONDecodeError):
            return self.setting_value
    
    def set_typed_value(self, value):
        """Set setting value from typed value"""
        if self.setting_type == 'json':
            self.setting_value = json.dumps(value)
        elif self.setting_type == 'boolean':
            self.setting_value = 'true' if value else 'false'
        else:
            self.setting_value = str(value)
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Convenience method to get a setting value"""
        return cls.objects.get_value(key, default)
    
    @classmethod
    def set_setting(cls, key, value, setting_type='text', description=None):
        """Convenience method to set a setting value"""
        return cls.objects.set_value(key, value, setting_type, description)


# Common site settings initialization
def initialize_default_settings():
    """Initialize default site settings"""
    default_settings = {
        # General Settings
        ('site_name', 'Afèpanou', 'text', 'general', 'Nom du site', True),
        ('site_description', 'Marketplace Haïtien pour la Croissance Économique Locale', 'text', 'general', 'Description du site', True),
        ('site_keywords', 'Haiti, marketplace, e-commerce, MonCash', 'text', 'seo', 'Mots-clés du site', True),
        ('site_logo', '', 'image', 'appearance', 'Logo du site', True),
        ('favicon', '', 'image', 'appearance', 'Favicon du site', True),
        
        # Commerce Settings
        ('default_currency', 'HTG', 'text', 'commerce', 'Devise par défaut', True),
        ('tax_rate', '0.00', 'number', 'commerce', 'Taux de taxe par défaut', False),
        ('shipping_cost', '50.00', 'number', 'commerce', 'Coût de livraison par défaut', False),
        ('free_shipping_threshold', '1000.00', 'number', 'commerce', 'Seuil de livraison gratuite', False),
        
        # Payment Settings
        ('moncash_enabled', 'true', 'boolean', 'payments', 'MonCash activé', False),
        ('cod_enabled', 'true', 'boolean', 'payments', 'Paiement à la livraison activé', False),
        
        # Email Settings
        ('admin_email', '', 'email', 'email', 'Email administrateur', False),
        ('from_email', '', 'email', 'email', 'Email expéditeur', False),
        ('smtp_enabled', 'false', 'boolean', 'email', 'SMTP activé', False),
        
        # Social Media
        ('facebook_url', '', 'url', 'social', 'URL Facebook', True),
        ('instagram_url', '', 'url', 'social', 'URL Instagram', True),
        ('twitter_url', '', 'url', 'social', 'URL Twitter', True),
        
        # Features
        ('reviews_enabled', 'true', 'boolean', 'general', 'Avis activés', True),
        ('newsletter_enabled', 'true', 'boolean', 'general', 'Newsletter activée', True),
        ('wishlist_enabled', 'true', 'boolean', 'general', 'Liste de souhaits activée', True),
        
        # Appearance
        ('primary_color', '#E67E22', 'color', 'appearance', 'Couleur primaire', True),
        ('secondary_color', '#D35400', 'color', 'appearance', 'Couleur secondaire', True),
        
        # Business Information
        ('business_name', 'Afèpanou', 'text', 'general', 'Nom de l\'entreprise', True),
        ('business_address', 'Port-au-Prince, Haïti', 'text', 'general', 'Adresse de l\'entreprise', True),
        ('business_phone', '', 'text', 'general', 'Téléphone de l\'entreprise', True),
        ('business_email', '', 'email', 'general', 'Email de l\'entreprise', True),
    }
    
    for key, value, setting_type, group, description, is_public in default_settings:
        SiteSetting.objects.get_or_create(
            setting_key=key,
            defaults={
                'setting_value': value,
                'setting_type': setting_type,
                'group_name': group,
                'description': description,
                'is_public': is_public,
            }
        )