# marketplace/models/review.py
"""
Review and rating models for Afèpanou marketplace
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from .managers import ReviewManager


class Review(models.Model):
    """Avis clients sur les produits"""
    
    RATING_CHOICES = [
        (1, '1 étoile'),
        (2, '2 étoiles'),
        (3, '3 étoiles'),
        (4, '4 étoiles'),
        (5, '5 étoiles'),
    ]
    
    # Relationships
    product = models.ForeignKey('Product', models.CASCADE, related_name='reviews')
    user = models.ForeignKey(
        'User', 
        models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='reviews'
    )
    order = models.ForeignKey('Order', models.CASCADE, blank=True, null=True)
    
    # Customer Information
    customer_name = models.CharField(max_length=100)
    customer_email = models.CharField(max_length=100, blank=True, null=True)
    
    # Review Content
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    pros = models.TextField(blank=True, null=True, help_text="Points positifs")
    cons = models.TextField(blank=True, null=True, help_text="Points négatifs")
    
    # Review Status
    is_verified_purchase = models.BooleanField(default=False, blank=True, null=True)
    is_approved = models.BooleanField(default=False, blank=True, null=True)
    helpful_count = models.IntegerField(default=0, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    
    objects = ReviewManager()

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-created_at']
        unique_together = ['product', 'user', 'order']
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"Avis de {self.customer_name} sur {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Auto-approve verified purchases with high ratings
        if (self.is_verified_purchase and 
            self.rating >= 4 and 
            not self.is_approved):
            self.is_approved = True
            self.approved_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def rating_stars(self):
        """Get star rating display"""
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    @property
    def is_recent(self):
        """Check if review is recent (within last 30 days)"""
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        return self.created_at >= thirty_days_ago
    
    def approve(self):
        """Approve this review"""
        self.is_approved = True
        self.approved_at = timezone.now()
        self.save()
    
    def mark_helpful(self):
        """Mark review as helpful"""
        self.helpful_count += 1
        self.save()


class ReviewHelpful(models.Model):
    """Track users who found reviews helpful"""
    
    # Relationships
    review = models.ForeignKey(Review, models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey('User', models.CASCADE)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'review_helpful'
        verbose_name = 'Avis Utile'
        verbose_name_plural = 'Avis Utiles'
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f"{self.user.username} trouve l'avis de {self.review.customer_name} utile"