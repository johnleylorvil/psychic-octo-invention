## Phase 4: Model Analysis & Enhancement

### Task 4: Analyze and Enhance Models for Complete Marketplace Functionality
**Priority**: Medium | 

#### Objective
Thoroughly analyze existing models, identify gaps, and enhance them to support full marketplace functionality including vendor management, inventory tracking, and payment processing.

#### Deliverables
- [ ] Model relationship diagram
- [ ] Enhanced model classes with proper validation
- [ ] Missing model implementations
- [ ] Database migration scripts
- [ ] Model documentation


#### Implementation Steps

1. **Model Analysis & Documentation**
   ```python
   # Create detailed model analysis document
   # marketplace/docs/models_analysis.md
   """
   Model Relationship Analysis:
   
   User (1) -> (M) Product [seller relationship]
   Product (M) -> (1) Category [categorization]
   Product (1) -> (M) ProductImage [gallery]
   Product (M) -> (M) Cart [through CartItem]
   Order (1) -> (M) OrderItem [line items]
   Order (1) -> (1) Transaction [payment]
   User (1) -> (M) Review [for products purchased]
   """
   ```

2. **Enhance Existing Models**
   ```python
   # marketplace/models/product.py
   class Product(models.Model):
       # Add missing fields
       sku = models.CharField(max_length=50, unique=True, blank=True)
       weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
       dimensions = models.JSONField(blank=True, null=True)  # length, width, height
       
       # SEO enhancements
       meta_title = models.CharField(max_length=60, blank=True)
       meta_description = models.CharField(max_length=160, blank=True)
       
       # Inventory tracking
       reserved_quantity = models.PositiveIntegerField(default=0)
       
       @property
       def available_quantity(self):
           return self.stock_quantity - self.reserved_quantity
           
       def reserve_quantity(self, quantity):
           """Reserve quantity for pending orders"""
           if self.available_quantity >= quantity:
               self.reserved_quantity += quantity
               self.save()
               return True
           return False
   ```

3. **Add Missing Models**
   ```python
   # marketplace/models/vendor.py
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
   
   # marketplace/models/promotion.py
   class Promotion(models.Model):
       DISCOUNT_TYPES = [
           ('percentage', 'Percentage'),
           ('fixed_amount', 'Fixed Amount'),
           ('buy_x_get_y', 'Buy X Get Y'),
       ]
       
       name = models.CharField(max_length=100)
       code = models.CharField(max_length=20, unique=True)
       discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
       discount_value = models.DecimalField(max_digits=10, decimal_places=2)
       
       # Conditions
       minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
       maximum_uses = models.PositiveIntegerField(null=True, blank=True)
       current_uses = models.PositiveIntegerField(default=0)
       
       # Validity
       start_date = models.DateTimeField()
       end_date = models.DateTimeField()
       is_active = models.BooleanField(default=True)
   ```

4. **Add Model Validation**
   ```python
   # marketplace/models/product.py (enhancement)
   class Product(models.Model):
       def clean(self):
           """Custom model validation"""
           if self.promotional_price and self.promotional_price >= self.price:
               raise ValidationError('Promotional price must be less than regular price')
               
           if self.stock_quantity < 0:
               raise ValidationError('Stock quantity cannot be negative')
               
           if self.low_stock_threshold > self.stock_quantity:
               raise ValidationError('Low stock threshold cannot exceed current stock')
   
       def save(self, *args, **kwargs):
           if not self.sku:
               self.sku = self.generate_sku()
           self.full_clean()
           super().save(*args, **kwargs)
   
       def generate_sku(self):
           """Generate unique SKU for product"""
           import uuid
           return f"AFE-{str(uuid.uuid4())[:8].upper()}"
   ```

#### Acceptance Criteria
- [ ] All model relationships properly defined and documented
- [ ] Missing models implemented (VendorProfile, Promotion, etc.)
- [ ] Model validation implemented and tested
- [ ] Database migrations created and tested
- [ ] Model methods provide useful business logic
- [ ] Foreign key relationships optimized with proper related_name

---