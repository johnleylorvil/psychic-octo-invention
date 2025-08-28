# marketplace/models/vendor.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .user import User
from ..validators import validate_haitian_phone_number

class VendorProfile(models.Model):
    """Enhanced vendor profile for comprehensive seller management"""
    
    BUSINESS_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('sole_proprietorship', 'Sole Proprietorship'),
        ('corporation', 'Corporation'),
        ('cooperative', 'Cooperative'),
        ('ngo', 'NGO/Non-Profit'),
    ]
    
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_review', 'In Review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    # Basic Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=150)
    business_type = models.CharField(
        max_length=50, 
        choices=BUSINESS_TYPE_CHOICES,
        default='individual'
    )
    business_description = models.TextField(blank=True)
    business_registration = models.CharField(max_length=50, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    
    # Contact Information
    business_address = models.TextField()
    business_phone = models.CharField(
        max_length=20, 
        validators=[validate_haitian_phone_number]
    )
    business_email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Financial Information
    bank_account_info = models.JSONField(blank=True, null=True)
    moncash_number = models.CharField(max_length=20, blank=True)
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=15.00,
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    
    # Verification and Status
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending'
    )
    is_verified = models.BooleanField(default=False)
    verification_documents = models.JSONField(blank=True, null=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    verification_notes = models.TextField(blank=True)
    
    # Performance Metrics
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    cancelled_orders = models.PositiveIntegerField(default=0)
    return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Account Settings
    is_featured_seller = models.BooleanField(default=False)
    auto_accept_orders = models.BooleanField(default=True)
    max_processing_days = models.PositiveIntegerField(default=3)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vendor_profiles'
        verbose_name = 'Vendor Profile'
        verbose_name_plural = 'Vendor Profiles'
        
    def __str__(self):
        return f"{self.business_name} ({self.user.username})"
    
    def mark_as_verified(self, notes=""):
        """Mark vendor as verified"""
        self.is_verified = True
        self.verification_status = 'verified'
        self.verified_at = timezone.now()
        self.verification_notes = notes
        self.save(update_fields=[
            'is_verified', 'verification_status', 
            'verified_at', 'verification_notes'
        ])
    
    def suspend_vendor(self, reason=""):
        """Suspend vendor account"""
        self.verification_status = 'suspended'
        self.verification_notes = reason
        self.user.suspend_account(reason)
        self.save(update_fields=['verification_status', 'verification_notes'])
    
    def update_performance_metrics(self):
        """Update performance metrics based on actual data"""
        from django.db.models import Sum, Avg, Count
        from ..models import Order, Review
        
        # Get orders for this vendor's products
        orders = Order.objects.filter(
            items__product__seller=self.user,
            payment_status='paid'
        ).distinct()
        
        completed = orders.filter(status='delivered')
        cancelled = orders.filter(status='cancelled')
        
        # Update order counts
        self.total_orders = orders.count()
        self.completed_orders = completed.count()
        self.cancelled_orders = cancelled.count()
        
        # Update revenue
        revenue_data = completed.aggregate(
            total=Sum('total_amount')
        )
        self.total_revenue = revenue_data['total'] or 0
        
        # Update ratings
        rating_data = Review.objects.filter(
            product__seller=self.user,
            is_approved=True
        ).aggregate(
            avg_rating=Avg('rating'),
            count=Count('id')
        )
        
        self.average_rating = rating_data['avg_rating'] or 0
        
        # Calculate return rate
        if self.completed_orders > 0:
            returns = orders.filter(status='refunded').count()
            self.return_rate = (returns / self.completed_orders) * 100
        
        self.save()
    
    @property
    def completion_rate(self):
        """Calculate order completion rate"""
        if self.total_orders > 0:
            return (self.completed_orders / self.total_orders) * 100
        return 0
    
    @property
    def is_reliable_seller(self):
        """Check if seller meets reliability criteria"""
        return (
            self.is_verified and
            self.average_rating >= 4.0 and
            self.completion_rate >= 90 and
            self.return_rate <= 5
        )
    
    @property
    def pending_verification(self):
        """Check if verification is pending"""
        return self.verification_status in ['pending', 'in_review']
