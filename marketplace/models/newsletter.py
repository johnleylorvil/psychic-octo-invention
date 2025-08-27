# marketplace/models/newsletter.py
"""
Newsletter and subscription models for Afèpanou marketplace
"""

from django.db import models
from django.utils import timezone


class NewsletterSubscriber(models.Model):
    """Abonnés à la newsletter"""
    
    SOURCE_CHOICES = [
        ('website', 'Site Web'),
        ('checkout', 'Checkout'),
        ('registration', 'Inscription'),
        ('popup', 'Pop-up'),
        ('footer', 'Footer'),
        ('api', 'API'),
        ('import', 'Import'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('unsubscribed', 'Désabonné'),
        ('bounced', 'Rejeté'),
        ('complained', 'Plainte'),
    ]
    
    # Contact Information
    email = models.CharField(unique=True, max_length=100)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    
    # Preferences
    language = models.CharField(max_length=5, default='fr', blank=True, null=True)
    categories_of_interest = models.JSONField(
        blank=True, 
        null=True,
        help_text="Catégories d'intérêt du subscriber"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True, blank=True, null=True)
    
    # Source Tracking
    source = models.CharField(
        max_length=50, 
        default='website', 
        blank=True, 
        null=True,
        choices=SOURCE_CHOICES
    )
    referrer_url = models.CharField(max_length=500, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Timestamps
    subscribed_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    unsubscribed_at = models.DateTimeField(blank=True, null=True)
    last_email_sent_at = models.DateTimeField(blank=True, null=True)
    
    # Engagement
    total_emails_sent = models.IntegerField(default=0, blank=True, null=True)
    total_emails_opened = models.IntegerField(default=0, blank=True, null=True)
    total_links_clicked = models.IntegerField(default=0, blank=True, null=True)
    
    class Meta:
        db_table = 'newsletter_subscribers'
        verbose_name = 'Abonné Newsletter'
        verbose_name_plural = 'Abonnés Newsletter'
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['subscribed_at']),
        ]

    def __str__(self):
        if self.first_name or self.last_name:
            name = f"{self.first_name or ''} {self.last_name or ''}".strip()
            return f"{name} ({self.email})"
        return self.email
    
    @property
    def full_name(self):
        """Get subscriber's full name"""
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return None
    
    @property
    def is_engaged(self):
        """Check if subscriber is engaged (opened emails recently)"""
        if not self.last_email_sent_at:
            return True  # New subscribers are considered engaged
        
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        return (self.total_emails_opened > 0 and 
                self.last_email_sent_at >= thirty_days_ago)
    
    @property
    def engagement_rate(self):
        """Calculate email engagement rate"""
        if self.total_emails_sent == 0:
            return 0
        return round((self.total_emails_opened / self.total_emails_sent) * 100, 1)
    
    def unsubscribe(self, reason=None):
        """Unsubscribe the user"""
        self.status = 'unsubscribed'
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()
    
    def resubscribe(self):
        """Resubscribe the user"""
        self.status = 'active'
        self.is_active = True
        self.unsubscribed_at = None
        self.save()
    
    def record_email_sent(self):
        """Record that an email was sent"""
        self.total_emails_sent += 1
        self.last_email_sent_at = timezone.now()
        self.save(update_fields=['total_emails_sent', 'last_email_sent_at'])
    
    def record_email_opened(self):
        """Record that an email was opened"""
        self.total_emails_opened += 1
        self.save(update_fields=['total_emails_opened'])
    
    def record_link_clicked(self):
        """Record that a link was clicked"""
        self.total_links_clicked += 1
        self.save(update_fields=['total_links_clicked'])


class NewsletterCampaign(models.Model):
    """Campagnes de newsletter"""
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('scheduled', 'Programmé'),
        ('sending', 'En cours d\'envoi'),
        ('sent', 'Envoyé'),
        ('cancelled', 'Annulé'),
    ]
    
    # Campaign Information
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    preview_text = models.CharField(
        max_length=150, 
        blank=True, 
        null=True,
        help_text="Texte de prévisualisation"
    )
    
    # Content
    content_html = models.TextField()
    content_text = models.TextField(blank=True, null=True)
    
    # Targeting
    target_all_subscribers = models.BooleanField(default=True)
    target_categories = models.JSONField(
        blank=True, 
        null=True,
        help_text="Cibler par catégories d'intérêt"
    )
    
    # Status and Scheduling
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    scheduled_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    # Statistics
    total_recipients = models.IntegerField(default=0, blank=True, null=True)
    total_sent = models.IntegerField(default=0, blank=True, null=True)
    total_delivered = models.IntegerField(default=0, blank=True, null=True)
    total_opened = models.IntegerField(default=0, blank=True, null=True)
    total_clicked = models.IntegerField(default=0, blank=True, null=True)
    total_unsubscribed = models.IntegerField(default=0, blank=True, null=True)
    
    # Creator
    created_by = models.ForeignKey(
        'User',
        models.CASCADE,
        related_name='newsletter_campaigns'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'newsletter_campaigns'
        verbose_name = 'Campagne Newsletter'
        verbose_name_plural = 'Campagnes Newsletter'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def open_rate(self):
        """Calculate email open rate"""
        if self.total_delivered == 0:
            return 0
        return round((self.total_opened / self.total_delivered) * 100, 1)
    
    @property
    def click_rate(self):
        """Calculate click-through rate"""
        if self.total_delivered == 0:
            return 0
        return round((self.total_clicked / self.total_delivered) * 100, 1)
    
    @property
    def unsubscribe_rate(self):
        """Calculate unsubscribe rate"""
        if self.total_delivered == 0:
            return 0
        return round((self.total_unsubscribed / self.total_delivered) * 100, 1)