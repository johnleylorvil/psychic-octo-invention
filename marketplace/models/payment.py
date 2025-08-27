# marketplace/models/payment.py
"""
Payment and transaction models for Afèpanou marketplace
"""

from django.db import models
from django.utils import timezone
import uuid

from .managers import TransactionManager


class Transaction(models.Model):
    """Transactions de paiement"""
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complétée'),
        ('failed', 'Échec'),
        ('cancelled', 'Annulée'),
        ('refunded', 'Remboursée'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('moncash', 'MonCash'),
        ('bank_transfer', 'Virement Bancaire'),
        ('cash_on_delivery', 'Paiement à la Livraison'),
    ]

    # Relationships
    order = models.ForeignKey(
        'Order', 
        models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='transactions'
    )
    
    # Transaction Identification
    transaction_id = models.CharField(unique=True, max_length=100, blank=True, null=True)
    moncash_order_id = models.CharField(max_length=100, blank=True, null=True)
    payment_token = models.CharField(max_length=255, blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Transaction Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='HTG', blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending', 
        blank=True, 
        null=True
    )
    payment_method = models.CharField(
        max_length=50, 
        choices=PAYMENT_METHOD_CHOICES,
        default='moncash', 
        blank=True, 
        null=True
    )
    
    # Gateway Information
    gateway_response = models.JSONField(blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)
    
    # URLs and Callbacks
    callback_url = models.CharField(max_length=255, blank=True, null=True)
    return_url = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamps
    transaction_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    webhook_received_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    
    # Additional Information
    notes = models.TextField(blank=True, null=True)
    
    objects = TransactionManager()

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'payment_method']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['moncash_order_id']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transaction {self.transaction_id}"
    
    @property
    def is_successful(self):
        """Check if transaction was successful"""
        return self.status == 'completed'
    
    @property
    def is_pending(self):
        """Check if transaction is pending"""
        return self.status == 'pending'
    
    @property
    def can_be_refunded(self):
        """Check if transaction can be refunded"""
        return self.status == 'completed' and self.payment_method == 'moncash'
    
    def mark_as_completed(self, gateway_response=None):
        """Mark transaction as completed"""
        self.status = 'completed'
        self.verified_at = timezone.now()
        if gateway_response:
            self.gateway_response = gateway_response
        self.save()
    
    def mark_as_failed(self, reason=None):
        """Mark transaction as failed"""
        self.status = 'failed'
        if reason:
            self.failure_reason = reason
        self.save()
    
    def get_status_display_class(self):
        """Get CSS class for status display"""
        status_classes = {
            'pending': 'warning',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary',
            'refunded': 'info'
        }
        return status_classes.get(self.status, 'secondary')