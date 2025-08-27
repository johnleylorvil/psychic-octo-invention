# marketplace/models/vendor.py
from django.db import models
from .user import User

class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    business_name = models.CharField(max_length=100)
    business_registration = models.CharField(max_length=50, blank=True)
    business_address = models.TextField()
    business_phone = models.CharField(max_length=20)
    bank_account_info = models.JSONField(blank=True, null=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)

    # Verification status
    is_verified = models.BooleanField(default=False)
    verification_documents = models.JSONField(blank=True, null=True)

    # Performance metrics
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
