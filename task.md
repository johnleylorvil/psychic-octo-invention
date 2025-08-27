# Afèpanou Development Task List

## Project Development Roadmap

This document outlines the systematic approach to building the Afèpanou marketplace platform. Each task builds upon the previous ones to ensure a solid, well-tested foundation.

---

## Phase 1: Project Foundation & Documentation

### Task 1: Create Changelog System
**Priority**: High | **Estimated Time**: 4 hours

#### Objective
Establish a comprehensive changelog system to track project evolution, context, and decision-making process.

#### Deliverables
- [ ] Create `CHANGELOG.md` in project root
- [ ] Set up changelog structure with semantic versioning
- [ ] Document current project state and existing codebase
- [ ] Establish changelog update workflow for team

#### Implementation Steps
1. **Create CHANGELOG.md Structure**
   ```markdown
   # Changelog
   All notable changes to Afèpanou marketplace will be documented in this file.
   
   ## [Unreleased]
   ### Added
   ### Changed  
   ### Deprecated
   ### Removed
   ### Fixed
   ### Security
   
   ## [1.0.0] - 2025-08-26
   ### Added
   - Initial marketplace structure with Django backend
   - MonCash payment integration foundation
   - Basic product catalog models
   - User authentication system
   ```

2. **Context Documentation**
   ```markdown
   ## Development Context Log
   
   ### 2025-08-26: Project Analysis
   **Existing Codebase Status:**
   - Django backend with marketplace app structure ✅
   - Models defined for User, Product, Order, Transaction ✅  
   - MonCash integration partially implemented ✅
   - Celery configuration with specialized queues ✅
   - Railway deployment configuration ✅
   - Templates and static files structure basic ❌
   - API serializers not implemented ❌
   - Business logic services empty ❌
   - Comprehensive tests missing ❌
   
   **Technical Decisions Made:**
   - PostgreSQL database hosted on Railway
   - Backblaze B2 for media storage  
   - Redis for caching and Celery broker
   - MonCash as primary payment processor
   - French localization for Haitian market
   ```

3. **Set Up Version Control Hooks**
   - Create `.gitmessage` template for consistent commit messages
   - Add changelog update reminders in PR templates

#### Acceptance Criteria
- [ ] CHANGELOG.md exists with proper semantic versioning structure
- [ ] Current project state thoroughly documented
- [ ] Team workflow established for changelog maintenance
- [ ] Git hooks configured to prompt changelog updates

---

## Phase 2: Template Structure & Frontend Foundation

### Task 2: Structure Templates According to Design Guidelines
**Priority**: High | **Estimated Time**: 12 hours

#### Objective
Create a comprehensive, maintainable template structure that aligns with the Afèpanou design system and supports the full marketplace functionality.

#### Deliverables
- [ ] Base template system with consistent layout
- [ ] Component-based template architecture
- [ ] Responsive design implementation
- [ ] Haitian localization integration

#### Implementation Steps

1. **Create Base Template System**
   ```
   templates/
   ├── base/
   │   ├── base.html              # Master template
   │   ├── header.html            # Global navigation
   │   ├── footer.html            # Global footer
   │   ├── messages.html          # Flash messages
   │   └── meta.html              # SEO meta tags
   ├── components/                 # Reusable components
   │   ├── product_card.html      # Product display card
   │   ├── category_nav.html      # Category navigation
   │   ├── search_bar.html        # Search functionality
   │   ├── cart_summary.html      # Cart widget
   │   ├── pagination.html        # Pagination component
   │   └── rating_stars.html      # Rating display
   ├── pages/                     # Full page templates
   │   ├── home.html             # Homepage
   │   ├── category_list.html    # Category listing
   │   ├── product_detail.html   # Product page
   │   ├── search_results.html   # Search results
   │   ├── cart.html            # Shopping cart
   │   └── checkout.html        # Checkout process
   ├── account/                   # User account templates
   │   ├── login.html
   │   ├── register.html
   │   ├── profile.html
   │   └── order_history.html
   ├── seller/                    # Seller dashboard
   │   ├── dashboard.html
   │   ├── products.html
   │   ├── orders.html
   │   └── analytics.html
   └── emails/                    # Email templates
       ├── order_confirmation.html
       ├── shipping_notification.html
       └── welcome.html
   ```

2. **Implement Design System CSS**
   ```css
   /* static/css/main.css */
   :root {
     /* Brand colors from design system */
     --primary-orange: #E67E22;
     --primary-orange-dark: #D35400;
     --primary-orange-light: #F39C12;
     /* ... rest of design system variables */
   }
   
   /* Component styles */
   @import 'components/buttons.css';
   @import 'components/cards.css';
   @import 'components/forms.css';
   @import 'components/navigation.css';
   ```

3. **JavaScript Component Architecture**
   ```javascript
   // static/js/components/
   ├── cart.js              # Shopping cart functionality
   ├── search.js            # Product search
   ├── product-gallery.js   # Image gallery
   ├── filters.js           # Category filters
   └── checkout.js          # Checkout process
   ```

#### Key Templates to Implement

1. **Base Template (base.html)**
   ```html
   <!DOCTYPE html>
   <html lang="fr-HT">
   <head>
       {% include 'base/meta.html' %}
       <title>{% block title %}Afèpanou - Croissance Économique Locale{% endblock %}</title>
       {% load static %}
       <link rel="stylesheet" href="{% static 'css/main.css' %}">
   </head>
   <body>
       {% include 'base/header.html' %}
       
       <main id="main-content">
           {% include 'base/messages.html' %}
           {% block content %}{% endblock %}
       </main>
       
       {% include 'base/footer.html' %}
       
       <script src="{% static 'js/main.js' %}"></script>
       {% block extra_js %}{% endblock %}
   </body>
   </html>
   ```

2. **Homepage Template (pages/home.html)**
   - Hero carousel with Haitian economic growth messaging
   - Featured product categories
   - Popular products section
   - Seller spotlight section

3. **Product Detail Template (pages/product_detail.html)**
   - Product image gallery with zoom
   - Detailed product information
   - Add to cart functionality
   - Reviews and ratings section
   - Seller information

#### Acceptance Criteria
- [ ] All templates render correctly across devices (mobile, tablet, desktop)
- [ ] Design system consistently applied throughout
- [ ] French localization properly integrated
- [ ] Template inheritance working correctly
- [ ] Component reusability demonstrated
- [ ] Accessibility standards met (ARIA labels, proper heading hierarchy)

---

## Phase 3: Application Structure Optimization

### Task 3: Structure Marketplace App According to Django Best Practices
**Priority**: High | **Estimated Time**: 8 hours

#### Objective
Reorganize the marketplace Django app to follow domain-driven design principles and Django best practices for maintainability and scalability.

#### Deliverables
- [ ] Properly organized app structure
- [ ] Clear separation of concerns
- [ ] Domain-based model organization
- [ ] Service layer implementation
- [ ] Admin interface enhancement

#### Implementation Steps

1. **Reorganize Models by Domain**
   ```python
   # marketplace/models/__init__.py
   from .user import User, UserProfile, SellerProfile
   from .product import Category, Product, ProductImage, ProductVariant
   from .order import Cart, CartItem, Order, OrderItem, Transaction
   from .content import Banner, MediaContentSection, Page
   from .review import Review, Rating
   
   __all__ = [
       'User', 'UserProfile', 'SellerProfile',
       'Category', 'Product', 'ProductImage', 'ProductVariant',
       'Cart', 'CartItem', 'Order', 'OrderItem', 'Transaction',
       'Banner', 'MediaContentSection', 'Page',
       'Review', 'Rating',
   ]
   ```

2. **Create Service Layer Architecture**
   ```python
   # marketplace/services/__init__.py
   from .product_service import ProductService
   from .cart_service import CartService  
   from .order_service import OrderService
   from .payment_service import PaymentService
   from .email_service import EmailService
   
   # marketplace/services/product_service.py
   class ProductService:
       @staticmethod
       def get_featured_products(limit=8):
           """Get featured products for homepage"""
           
       @staticmethod
       def search_products(query, category=None, filters=None):
           """Advanced product search with filters"""
           
       @staticmethod
       def get_related_products(product, limit=4):
           """Get products related to given product"""
   ```

3. **Implement Manager Classes**
   ```python
   # marketplace/managers.py
   class ProductManager(models.Manager):
       def available(self):
           return self.filter(is_active=True, stock_quantity__gt=0)
           
       def featured(self):
           return self.available().filter(is_featured=True)
           
       def by_category(self, category):
           return self.available().filter(category=category)
   
   class OrderManager(models.Manager):
       def for_user(self, user):
           return self.filter(user=user).order_by('-created_at')
           
       def pending_payment(self):
           return self.filter(status='pending')
   ```

4. **Enhanced Admin Interface**
   ```python
   # marketplace/admin.py
   @admin.register(Product)
   class ProductAdmin(admin.ModelAdmin):
       list_display = ['name', 'category', 'price', 'stock_quantity', 'is_active']
       list_filter = ['category', 'is_active', 'is_featured']
       search_fields = ['name', 'description']
       prepopulated_fields = {'slug': ('name',)}
       readonly_fields = ['created_at', 'updated_at']
       
       fieldsets = (
           ('Basic Information', {
               'fields': ('name', 'slug', 'description', 'category')
           }),
           ('Pricing', {
               'fields': ('price', 'promotional_price', 'cost_price')
           }),
           ('Inventory', {
               'fields': ('stock_quantity', 'low_stock_threshold')
           }),
           ('Settings', {
               'fields': ('is_active', 'is_featured', 'is_digital')
           })
       )
   ```

#### Acceptance Criteria
- [ ] Models properly organized by domain
- [ ] Service layer provides clear business logic abstraction
- [ ] Manager classes enhance query capabilities
- [ ] Admin interface provides comprehensive product management
- [ ] Code follows Django naming conventions
- [ ] Proper imports and dependencies

---

## Phase 4: Model Analysis & Enhancement

### Task 4: Analyze and Enhance Models for Complete Marketplace Functionality
**Priority**: Medium | **Estimated Time**: 10 hours

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

## Phase 5: Views & Forms Implementation

### Task 5: Create Comprehensive Views and Forms
**Priority**: High | **Estimated Time**: 16 hours

#### Objective
Implement all necessary views and forms to support the complete marketplace functionality, including product browsing, cart management, checkout process, and user account management.

#### Deliverables
- [ ] Template-based views for all pages
- [ ] API views for AJAX functionality
- [ ] Form classes with validation
- [ ] Authentication and permission handling
- [ ] Error handling and user feedback

#### Implementation Steps

1. **Create Form Classes**
   ```python
   # marketplace/forms/__init__.py
   from .product_forms import ProductSearchForm, ProductReviewForm
   from .user_forms import UserRegistrationForm, UserProfileForm, SellerApplicationForm
   from .checkout_forms import ShippingAddressForm, PaymentForm
   
   # marketplace/forms/product_forms.py
   class ProductSearchForm(forms.Form):
       query = forms.CharField(
           max_length=100,
           required=False,
           widget=forms.TextInput(attrs={
               'placeholder': 'Rechercher produits et services...',
               'class': 'form-control search-input'
           })
       )
       category = forms.ModelChoiceField(
           queryset=Category.objects.filter(parent__isnull=True),
           required=False,
           empty_label="Toutes les catégories"
       )
       min_price = forms.DecimalField(required=False, min_value=0)
       max_price = forms.DecimalField(required=False, min_value=0)
       in_stock = forms.BooleanField(required=False)
       
       def clean(self):
           cleaned_data = super().clean()
           min_price = cleaned_data.get('min_price')
           max_price = cleaned_data.get('max_price')
           
           if min_price and max_price and min_price > max_price:
               raise forms.ValidationError("Le prix minimum ne peut pas être supérieur au prix maximum")
   
   class ProductReviewForm(forms.ModelForm):
       class Meta:
           model = Review
           fields = ['rating', 'title', 'comment']
           widgets = {
               'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
               'comment': forms.Textarea(attrs={'rows': 4})
           }
   ```

2. **Implement Template Views**
   ```python
   # marketplace/views/pages.py
   class HomePageView(TemplateView):
       template_name = 'pages/home.html'
       
       def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)
           context.update({
               'featured_products': Product.objects.featured()[:8],
               'categories': Category.objects.filter(parent__isnull=True),
               'banners': Banner.objects.filter(is_active=True),
               'recent_reviews': Review.objects.select_related('product', 'user').order_by('-created_at')[:6]
           })
           return context
   
   class ProductDetailView(DetailView):
       model = Product
       template_name = 'pages/product_detail.html'
       context_object_name = 'product'
       
       def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)
           product = self.object
           
           context.update({
               'related_products': ProductService.get_related_products(product),
               'reviews': product.reviews.select_related('user').order_by('-created_at'),
               'review_form': ProductReviewForm(),
               'can_review': self.can_user_review(product)
           })
           return context
           
       def can_user_review(self, product):
           if not self.request.user.is_authenticated:
               return False
           # Check if user has purchased this product
           return OrderItem.objects.filter(
               order__user=self.request.user,
               product=product,
               order__status='delivered'
           ).exists()
   
   class CategoryListView(ListView):
       model = Product
       template_name = 'pages/category_list.html'
       context_object_name = 'products'
       paginate_by = 24
       
       def get_queryset(self):
           category_slug = self.kwargs.get('slug')
           self.category = get_object_or_404(Category, slug=category_slug)
           
           queryset = Product.objects.filter(category=self.category).available()
           
           # Apply filters from form
           form = ProductSearchForm(self.request.GET)
           if form.is_valid():
               if form.cleaned_data['query']:
                   queryset = queryset.filter(
                       Q(name__icontains=form.cleaned_data['query']) |
                       Q(description__icontains=form.cleaned_data['query'])
                   )
               if form.cleaned_data['min_price']:
                   queryset = queryset.filter(price__gte=form.cleaned_data['min_price'])
               if form.cleaned_data['max_price']:
                   queryset = queryset.filter(price__lte=form.cleaned_data['max_price'])
           
           # Apply sorting
           sort_by = self.request.GET.get('sort', 'popularity')
           if sort_by == 'price_asc':
               queryset = queryset.order_by('price')
           elif sort_by == 'price_desc':
               queryset = queryset.order_by('-price')
           elif sort_by == 'newest':
               queryset = queryset.order_by('-created_at')
           elif sort_by == 'rating':
               queryset = queryset.order_by('-average_rating')
           else:  # popularity
               queryset = queryset.order_by('-view_count', '-created_at')
               
           return queryset
       
       def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)
           context.update({
               'category': self.category,
               'search_form': ProductSearchForm(self.request.GET),
               'current_filters': self.request.GET,
               'sellers': User.objects.filter(
                   products__category=self.category
               ).annotate(
                   products_count=Count('products')
               ).distinct()
           })
           return context
   ```

3. **Implement AJAX Views**
   ```python
   # marketplace/views/ajax.py
   class AddToCartView(LoginRequiredMixin, View):
       def post(self, request):
           try:
               product_id = request.POST.get('product_id')
               quantity = int(request.POST.get('quantity', 1))
               
               product = get_object_or_404(Product, id=product_id)
               
               if quantity > product.available_quantity:
                   return JsonResponse({
                       'success': False,
                       'message': 'Quantité demandée non disponible'
                   })
               
               cart, created = Cart.objects.get_or_create(user=request.user)
               cart_item, item_created = CartItem.objects.get_or_create(
                   cart=cart,
                   product=product,
                   defaults={'quantity': quantity}
               )
               
               if not item_created:
                   cart_item.quantity += quantity
                   cart_item.save()
               
               return JsonResponse({
                   'success': True,
                   'message': 'Produit ajouté au panier',
                   'cart_count': cart.items.count(),
                   'cart_total': str(cart.total_price)
               })
               
           except Exception as e:
               return JsonResponse({
                   'success': False,
                   'message': 'Erreur lors de l\'ajout au panier'
               })
   
   class ProductQuickViewView(DetailView):
       model = Product
       template_name = 'components/product_quick_view.html'
       
       def get_context_data(self, **kwargs):
           context = super().get_context_data(**kwargs)
           context['is_quick_view'] = True
           return context
   ```

4. **Implement User Account Views**
   ```python
   # marketplace/views/account.py
   class UserRegistrationView(CreateView):
       form_class = UserRegistrationForm
       template_name = 'account/register.html'
       success_url = reverse_lazy('account:profile')
       
       def form_valid(self, form):
           user = form.save()
           login(self.request, user)
           messages.success(self.request, 'Compte créé avec succès!')
           return super().form_valid(form)
   
   class UserProfileView(LoginRequiredMixin, UpdateView):
       model = User
       form_class = UserProfileForm
       template_name = 'account/profile.html'
       success_url = reverse_lazy('account:profile')
       
       def get_object(self):
           return self.request.user
       
       def form_valid(self, form):
           messages.success(self.request, 'Profil mis à jour avec succès!')
           return super().form_valid(form)
   
   class SellerApplicationView(LoginRequiredMixin, CreateView):
       form_class = SellerApplicationForm
       template_name = 'account/become_seller.html'
       success_url = reverse_lazy('account:profile')
       
       def form_valid(self, form):
           vendor_profile = form.save(commit=False)
           vendor_profile.user = self.request.user
           vendor_profile.save()
           
           # Send notification to admin
           send_seller_application_notification.delay(vendor_profile.id)
           
           messages.success(
               self.request, 
               'Votre demande de devenir vendeur a été soumise. Nous vous contacterons bientôt.'
           )
           return super().form_valid(form)
   ```

#### Acceptance Criteria
- [ ] All major pages have functional views
- [ ] Forms include proper validation and error handling
- [ ] AJAX views provide smooth user experience
- [ ] Authentication and permissions properly enforced
- [ ] User feedback through messages system
- [ ] Mobile-responsive templates implemented

---

## Phase 6: Testing Implementation

### Task 6: Create Comprehensive Test Suite
**Priority**: High | **Estimated Time**: 14 hours

#### Objective
Develop a comprehensive testing strategy covering unit tests, integration tests, and functional tests to ensure reliability and maintainability of the marketplace platform.

#### Deliverables
- [ ] Unit tests for models, views, and forms
- [ ] Integration tests for API endpoints
- [ ] Functional tests for user workflows
- [ ] Test fixtures and factories
- [ ] Test configuration and CI setup

#### Implementation Steps

1. **Set Up Testing Framework**
   ```python
   # requirements/testing.txt
   pytest==7.4.2
   pytest-django==4.5.2
   pytest-cov==4.0.0
   factory-boy==3.3.0
   faker==19.6.2
   
   # conftest.py (project root)
   import pytest
   from django.test import Client
   from django.contrib.auth import get_user_model
   from marketplace.models import Category, Product
   from tests.factories import UserFactory, ProductFactory, CategoryFactory
   
   User = get_user_model()
   
   @pytest.fixture
   def client():
       return Client()
   
   @pytest.fixture
   def user():
       return UserFactory()
   
   @pytest.fixture
   def seller():
       return UserFactory(is_seller=True)
   
   @pytest.fixture
   def category():
       return CategoryFactory()
   
   @pytest.fixture
   def product(seller, category):
       return ProductFactory(user=seller, category=category)
   ```

2. **Create Test Factories**
   ```python
   # tests/factories.py
   import factory
   from django.contrib.auth import get_user_model
   from marketplace.models import Category, Product, Order, Review
   
   User = get_user_model()
   
   class UserFactory(factory.django.DjangoModelFactory):
       class Meta:
           model = User
           
       username = factory.Sequence(lambda n: f"user{n}")
       email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
       first_name = factory.Faker('first_name')
       last_name = factory.Faker('last_name')
       phone = factory.Faker('phone_number')
       city = 'Port-au-Prince'
       country = 'Haïti'
       is_seller = False
   
   class CategoryFactory(factory.django.DjangoModelFactory):
       class Meta:
           model = Category
           
       name = factory.Faker('word')
       slug = factory.LazyAttribute(lambda obj: obj.name.lower())
       description = factory.Faker('text')
       is_active = True
   
   class ProductFactory(factory.django.DjangoModelFactory):
       class Meta:
           model = Product
           
       name = factory.Faker('commerce_product_name')
       description = factory.Faker('text')
       price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
       stock_quantity = factory.Faker('random_int', min=0, max=100)
       category = factory.SubFactory(CategoryFactory)
       user = factory.SubFactory(UserFactory, is_seller=True)
       is_active = True
       is_featured = False
   ```

3. **Model Tests**
   ```python
   # tests/test_models.py
   import pytest
   from decimal import Decimal
   from django.core.exceptions import ValidationError
   from marketplace.models import Product, Cart, CartItem
   from tests.factories import ProductFactory, UserFactory, CategoryFactory
   
   @pytest.mark.django_db
   class TestProductModel:
       def test_product_creation(self):
           """Test product can be created with required fields"""
           product = ProductFactory()
           assert product.name
           assert product.price > 0
           assert product.category
           assert product.user.is_seller
   
       def test_product_slug_generation(self):
           """Test automatic slug generation"""
           product = ProductFactory(name="Test Product Name")
           assert product.slug == "test-product-name"
   
       def test_promotional_price_validation(self):
           """Test promotional price must be less than regular price"""
           product = ProductFactory(price=Decimal('100.00'))
           product.promotional_price = Decimal('150.00')
           
           with pytest.raises(ValidationError):
               product.full_clean()
   
       def test_available_quantity_calculation(self):
           """Test available quantity considers reserved stock"""
           product = ProductFactory(stock_quantity=10)
           product.reserved_quantity = 3
           assert product.available_quantity == 7
   
       def test_reserve_quantity_success(self):
           """Test successful quantity reservation"""
           product = ProductFactory(stock_quantity=10, reserved_quantity=0)
           result = product.reserve_quantity(5)
           
           assert result is True
           assert product.reserved_quantity == 5
   
       def test_reserve_quantity_insufficient_stock(self):
           """Test quantity reservation fails with insufficient stock"""
           product = ProductFactory(stock_quantity=3, reserved_quantity=0)
           result = product.reserve_quantity(5)
           
           assert result is False
           assert product.reserved_quantity == 0
   
   @pytest.mark.django_db  
   class TestCartModel:
       def test_cart_creation(self):
           """Test cart creation for user"""
           user = UserFactory()
           cart = Cart.objects.create(user=user)
           assert cart.user == user
           assert cart.total_price == Decimal('0.00')
   
       def test_cart_total_calculation(self):
           """Test cart total price calculation"""
           user = UserFactory()
           cart = Cart.objects.create(user=user)
           product1 = ProductFactory(price=Decimal('25.00'))
           product2 = ProductFactory(price=Decimal('15.00'))
           
           CartItem.objects.create(cart=cart, product=product1, quantity=2)
           CartItem.objects.create(cart=cart, product=product2, quantity=1)
           
           # Refresh cart from database
           cart.refresh_from_db()
           assert cart.total_price == Decimal('65.00')  # (25*2) + (15*1)
   ```

4. **View Tests**
   ```python
   # tests/test_views.py
   import pytest
   from django.urls import reverse
   from django.contrib.auth import get_user_model
   from marketplace.models import Product, Cart, CartItem
   from tests.factories import ProductFactory, UserFactory, CategoryFactory
   
   User = get_user_model()
   
   @pytest.mark.django_db
   class TestHomePageView:
       def test_homepage_loads_successfully(self, client):
           """Test homepage loads without errors"""
           url = reverse('marketplace:home')
           response = client.get(url)
           assert response.status_code == 200
   
       def test_homepage_shows_featured_products(self, client):
           """Test homepage displays featured products"""
           ProductFactory.create_batch(3, is_featured=True)
           ProductFactory.create_batch(2, is_featured=False)
           
           url = reverse('marketplace:home')
           response = client.get(url)
           
           assert len(response.context['featured_products']) == 3
   
   @pytest.mark.django_db
   class TestProductDetailView:
       def test_product_detail_loads(self, client):
           """Test product detail page loads"""
           product = ProductFactory()
           url = reverse('marketplace:product_detail', kwargs={'slug': product.slug})
           response = client.get(url)
           
           assert response.status_code == 200
           assert response.context['product'] == product
   
       def test_product_detail_404_for_inactive_product(self, client):
           """Test 404 for inactive products"""
           product = ProductFactory(is_active=False)
           url = reverse('marketplace:product_detail', kwargs={'slug': product.slug})
           response = client.get(url)
           
           assert response.status_code == 404
   
   @pytest.mark.django_db
   class TestAddToCartView:
       def test_add_to_cart_requires_login(self, client):
           """Test add to cart requires authentication"""
           product = ProductFactory()
           url = reverse('marketplace:add_to_cart')
           
           response = client.post(url, {'product_id': product.id, 'quantity': 1})
           assert response.status_code == 302  # Redirect to login
   
       def test_add_to_cart_success(self, client):
           """Test successful product addition to cart"""
           user = UserFactory()
           product = ProductFactory(stock_quantity=10)
           client.force_login(user)
           
           url = reverse('marketplace:add_to_cart')
           response = client.post(url, {'product_id': product.id, 'quantity': 2})
           
           assert response.status_code == 200
           data = response.json()
           assert data['success'] is True
           
           # Verify cart item was created
           cart = Cart.objects.get(user=user)
           cart_item = CartItem.objects.get(cart=cart, product=product)
           assert cart_item.quantity == 2
   
       def test_add_to_cart_insufficient_stock(self, client):
           """Test add to cart with insufficient stock"""
           user = UserFactory()
           product = ProductFactory(stock_quantity=1)
           client.force_login(user)
           
           url = reverse('marketplace:add_to_cart')
           response = client.post(url, {'product_id': product.id, 'quantity': 5})
           
           data = response.json()
           assert data['success'] is False
           assert 'non disponible' in data['message'].lower()
   ```

5. **Form Tests**
   ```python
   # tests/test_forms.py
   import pytest
   from marketplace.forms import ProductSearchForm, ProductReviewForm
   from tests.factories import CategoryFactory
   
   @pytest.mark.django_db
   class TestProductSearchForm:
       def test_valid_search_form(self):
           """Test valid search form data"""
           category = CategoryFactory()
           form_data = {
               'query': 'test product',
               'category': category.id,
               'min_price': '10.00',
               'max_price': '100.00',
               'in_stock': True
           }
           
           form = ProductSearchForm(data=form_data)
           assert form.is_valid()
   
       def test_invalid_price_range(self):
           """Test form validation for invalid price range"""
           form_data = {
               'min_price': '100.00',
               'max_price': '50.00'
           }
           
           form = ProductSearchForm(data=form_data)
           assert not form.is_valid()
           assert 'Le prix minimum ne peut pas être supérieur au prix maximum' in str(form.errors)
   
   class TestProductReviewForm:
       def test_valid_review_form(self):
           """Test valid review form submission"""
           form_data = {
               'rating': 5,
               'title': 'Excellent product',
               'comment': 'This product exceeded my expectations.'
           }
           
           form = ProductReviewForm(data=form_data)
           assert form.is_valid()
   
       def test_review_form_missing_required_fields(self):
           """Test form validation with missing required fields"""
           form_data = {
               'comment': 'Good product'
               # Missing rating which is required
           }
           
           form = ProductReviewForm(data=form_data)
           assert not form.is_valid()
           assert 'rating' in form.errors
   ```

#### Acceptance Criteria
- [ ] Test coverage above 80%
- [ ] All critical user flows tested
- [ ] Tests run successfully in CI/CD pipeline
- [ ] Test fixtures provide realistic data scenarios
- [ ] Performance tests identify potential bottlenecks

---

## Phase 7: URL Configuration

### Task 7: Implement Complete URL Routing System
**Priority**: Medium | **Estimated Time**: 6 hours

#### Objective
Create a comprehensive, SEO-friendly URL structure that supports the full marketplace functionality with proper namespacing and error handling.

#### Deliverables
- [ ] Main URL configuration
- [ ] App-specific URL patterns
- [ ] SEO-friendly URL structures
- [ ] API endpoint organization
- [ ] Error page routing

#### Implementation Steps

1. **Main URL Configuration**
   ```python
   # config/urls.py
   from django.contrib import admin
   from django.urls import path, include
   from django.conf import settings
   from django.conf.urls.static import static
   from django.views.generic import TemplateView
   
   urlpatterns = [
       # Admin
       path('admin/', admin.site.urls),
       
       # Authentication
       path('auth/', include('django.contrib.auth.urls')),
       
       # Main marketplace
       path('', include('marketplace.urls', namespace='marketplace')),
       
       # API endpoints
       path('api/v1/', include('marketplace.api.urls', namespace='api')),
       
       # Static pages
       path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about'),
       path('contact/', TemplateView.as_view(template_name='pages/contact.html'), name='contact'),
       path('terms/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
       path('privacy/', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
   ]
   
   # Development media serving
   if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   
   # Custom error handlers
   handler404 = 'marketplace.views.errors.handler404'
   handler500 = 'marketplace.views.errors.handler500'
   ```

2. **Marketplace URL Patterns**
   ```python
   # marketplace/urls.py
   from django.urls import path, include
   from . import views
   
   app_name = 'marketplace'
   
   urlpatterns = [
       # Homepage
       path('', views.HomePageView.as_view(), name='home'),
       
       # Product URLs
       path('produit/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
       path('produits/', views.ProductListView.as_view(), name='product_list'),
       path('recherche/', views.ProductSearchView.as_view(), name='product_search'),
       
       # Category URLs
       path('categorie/<slug:slug>/', views.CategoryListView.as_view(), name='category_list'),
       path('categories/', views.CategoryIndexView.as_view(), name='category_index'),
       
       # Specific category pages (SEO-friendly)
       path('agricole/', views.AgricultureCategoryView.as_view(), name='agriculture'),
       path('patriotiques/', views.PatrioticCategoryView.as_view(), name='patriotic'),
       path('petite-industrie/', views.SmallIndustryCategoryView.as_view(), name='small_industry'),
       path('services/', views.ServicesView.as_view(), name='services'),
       path('premiere-necessite/', views.EssentialsCategoryView.as_view(), name='essentials'),
       
       # Cart & Checkout
       path('panier/', views.CartView.as_view(), name='cart'),
       path('panier/ajouter/', views.AddToCartView.as_view(), name='add_to_cart'),
       path('panier/supprimer/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
       path('panier/vider/', views.ClearCartView.as_view(), name='clear_cart'),
       path('commande/', views.CheckoutView.as_view(), name='checkout'),
       path('commande/confirmation/<int:order_id>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
       
       # User Account
       path('compte/', include([
           path('', views.UserProfileView.as_view(), name='profile'),
           path('inscription/', views.UserRegistrationView.as_view(), name='register'),
           path('connexion/', views.UserLoginView.as_view(), name='login'),
           path('deconnexion/', views.UserLogoutView.as_view(), name='logout'),
           path('commandes/', views.OrderHistoryView.as_view(), name='order_history'),
           path('commandes/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
           path('favoris/', views.WishlistView.as_view(), name='wishlist'),
           path('devenir-vendeur/', views.SellerApplicationView.as_view(), name='become_seller'),
       ])),
       
       # Seller Dashboard
       path('vendeur/', include([
           path('', views.SellerDashboardView.as_view(), name='seller_dashboard'),
           path('produits/', views.SellerProductListView.as_view(), name='seller_products'),
           path('produits/ajouter/', views.SellerProductCreateView.as_view(), name='seller_product_create'),
           path('produits/<int:pk>/modifier/', views.SellerProductUpdateView.as_view(), name='seller_product_update'),
           path('commandes/', views.SellerOrderListView.as_view(), name='seller_orders'),
           path('commandes/<int:pk>/', views.SellerOrderDetailView.as_view(), name='seller_order_detail'),
           path('statistiques/', views.SellerAnalyticsView.as_view(), name='seller_analytics'),
       ])),
       
       # Payment Processing
       path('paiement/', include([
           path('moncash/redirect/', views.MonCashRedirectView.as_view(), name='moncash_redirect'),
           path('moncash/callback/', views.MonCashCallbackView.as_view(), name='moncash_callback'),
           path('moncash/webhook/', views.MonCashWebhookView.as_view(), name='moncash_webhook'),
       ])),
       
       # AJAX Endpoints
       path('ajax/', include([
           path('produit/<int:pk>/apercu/', views.ProductQuickViewView.as_view(), name='product_quick_view'),
           path('avis/ajouter/', views.AddReviewView.as_view(), name='add_review'),
           path('favoris/toggle/', views.ToggleWishlistView.as_view(), name='toggle_wishlist'),
           path('panier/count/', views.CartCountView.as_view(), name='cart_count'),
       ])),
   ]
   ```

3. **API URL Configuration**
   ```python
   # marketplace/api/urls.py
   from django.urls import path, include
   from rest_framework.routers import DefaultRouter
   from . import views
   
   app_name = 'api'
   
   router = DefaultRouter()
   router.register(r'products', views.ProductViewSet)
   router.register(r'categories', views.CategoryViewSet)
   router.register(r'orders', views.OrderViewSet)
   router.register(r'reviews', views.ReviewViewSet)
   
   urlpatterns = [
       # DRF Router URLs
       path('', include(router.urls)),
       
       # Authentication
       path('auth/', include([
           path('login/', views.LoginAPIView.as_view(), name='login'),
           path('register/', views.RegisterAPIView.as_view(), name='register'),
           path('refresh/', views.RefreshTokenAPIView.as_view(), name='refresh_token'),
           path('logout/', views.LogoutAPIView.as_view(), name='logout'),
       ])),
       
       # Cart Management
       path('cart/', include([
           path('', views.CartAPIView.as_view(), name='cart'),
           path('add/', views.AddToCartAPIView.as_view(), name='add_to_cart'),
           path('remove/', views.RemoveFromCartAPIView.as_view(), name='remove_from_cart'),
           path('clear/', views.ClearCartAPIView.as_view(), name='clear_cart'),
       ])),
       
       # Search & Filtering
       path('search/', views.ProductSearchAPIView.as_view(), name='search'),
       path('autocomplete/', views.SearchAutocompleteAPIView.as_view(), name='autocomplete'),
       
       # MonCash Integration
       path('payments/', include([
           path('create/', views.CreatePaymentAPIView.as_view(), name='create_payment'),
           path('verify/', views.VerifyPaymentAPIView.as_view(), name='verify_payment'),
           path('webhook/', views.PaymentWebhookAPIView.as_view(), name='payment_webhook'),
       ])),
       
       # Analytics & Reporting
       path('analytics/', include([
           path('popular-products/', views.PopularProductsAPIView.as_view(), name='popular_products'),
           path('sales-stats/', views.SalesStatsAPIView.as_view(), name='sales_stats'),
       ])),
   ]
   ```

4. **SEO-Optimized URL Patterns**
   ```python
   # marketplace/seo_urls.py
   """
   Additional SEO-friendly URL patterns for better search engine optimization
   """
   from django.urls import path
   from . import views
   
   seo_urlpatterns = [
       # Location-specific URLs
       path('port-au-prince/', views.LocationView.as_view(), {'location': 'port-au-prince'}, name='port_au_prince'),
       path('cap-haitien/', views.LocationView.as_view(), {'location': 'cap-haitien'}, name='cap_haitien'),
       
       # Seasonal/promotional URLs
       path('nouveautes/', views.NewProductsView.as_view(), name='new_products'),
       path('promotions/', views.PromotionsView.as_view(), name='promotions'),
       path('meilleures-ventes/', views.BestSellersView.as_view(), name='best_sellers'),
       
       # Content marketing URLs
       path('blog/', views.BlogIndexView.as_view(), name='blog_index'),
       path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
       path('guides/', views.GuideIndexView.as_view(), name='guide_index'),
       path('guides/<slug:slug>/', views.GuideDetailView.as_view(), name='guide_detail'),
       
       # Seller profiles (public)
       path('boutique/<slug:seller_slug>/', views.SellerPublicProfileView.as_view(), name='seller_profile'),
       path('boutiques/', views.SellerDirectoryView.as_view(), name='seller_directory'),
   ]
   ```

5. **Error Handler Views**
   ```python
   # marketplace/views/errors.py
   from django.shortcuts import render
   from django.http import HttpResponseNotFound, HttpResponseServerError
   
   def handler404(request, exception):
       """Custom 404 error handler"""
       context = {
           'error_code': '404',
           'error_message': 'Page non trouvée',
           'error_description': 'La page que vous recherchez n\'existe pas ou a été déplacée.',
           'suggested_actions': [
               'Retourner à l\'accueil',
               'Rechercher des produits',
               'Parcourir les catégories',
           ]
       }
       return render(request, 'errors/404.html', context, status=404)
   
   def handler500(request):
       """Custom 500 error handler"""
       context = {
           'error_code': '500',
           'error_message': 'Erreur du serveur',
           'error_description': 'Une erreur inattendue s\'est produite. Notre équipe technique a été notifiée.',
           'suggested_actions': [
               'Actualiser la page',
               'Réessayer plus tard',
               'Contacter le support',
           ]
       }
       return render(request, 'errors/500.html', context, status=500)
   ```

#### Acceptance Criteria
- [ ] All URLs follow SEO-friendly patterns
- [ ] Proper namespacing implemented
- [ ] API endpoints organized logically
- [ ] Error handling provides helpful user experience
- [ ] URL patterns support internationalization
- [ ] No broken or conflicting URL patterns

---

## Phase 8: End-to-End Testing

### Task 8: Implement End-to-End Testing Suite
**Priority**: High | **Estimated Time**: 12 hours

#### Objective
Create comprehensive end-to-end tests that validate complete user workflows, ensuring the entire marketplace functions correctly from a user's perspective.

#### Deliverables
- [ ] User journey tests for major workflows
- [ ] Browser automation tests
- [ ] Performance testing setup
- [ ] Cross-browser compatibility tests
- [ ] Mobile responsiveness validation

#### Implementation Steps

1. **Set Up E2E Testing Framework**
   ```python
   # requirements/testing.txt (additions)
   selenium==4.15.0
   pytest-selenium==4.1.0
   pytest-html==4.0.0
   pytest-xdist==3.3.1
   locust==2.16.1  # For performance testing
   
   # conftest.py (additions for E2E)
   import pytest
   from selenium import webdriver
   from selenium.webdriver.chrome.options import Options
   from django.contrib.staticfiles.testing import StaticLiveServerTestCase
   from django.test import override_settings
   
   @pytest.fixture
   def browser():
       """Set up Chrome browser for testing"""
       chrome_options = Options()
       chrome_options.add_argument("--headless")  # Run in headless mode
       chrome_options.add_argument("--no-sandbox")
       chrome_options.add_argument("--disable-dev-shm-usage")
       
       driver = webdriver.Chrome(options=chrome_options)
       driver.implicitly_wait(10)
       yield driver
       driver.quit()
   
   @pytest.fixture
   def live_server():
       """Django live server for E2E testing"""
       from django.test import LiveServerTestCase
       server = LiveServerTestCase()
       server._pre_setup()
       yield server
       server._post_teardown()
   ```

2. **User Registration & Authentication Flow**
   ```python
   # tests/e2e/test_user_authentication.py
   import pytest
   from selenium.webdriver.common.by import By
   from selenium.webdriver.support.ui import WebDriverWait
   from selenium.webdriver.support import expected_conditions as EC
   from tests.factories import UserFactory
   
   @pytest.mark.e2e
   class TestUserAuthentication:
       def test_user_registration_complete_flow(self, browser, live_server):
           """Test complete user registration workflow"""
           # Navigate to registration page
           browser.get(f"{live_server.url}/compte/inscription/")
           
           # Fill registration form
           browser.find_element(By.NAME, "first_name").send_keys("Jean")
           browser.find_element(By.NAME, "last_name").send_keys("Dupont")
           browser.find_element(By.NAME, "email").send_keys("jean@example.com")
           browser.find_element(By.NAME, "phone").send_keys("+509 1234-5678")
           browser.find_element(By.NAME, "username").send_keys("jeandupont")
           browser.find_element(By.NAME, "password1").send_keys("SecurePass123!")
           browser.find_element(By.NAME, "password2").send_keys("SecurePass123!")
           
           # Submit form
           browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
           
           # Wait for redirect to profile page
           WebDriverWait(browser, 10).until(
               EC.url_contains("/compte/")
           )
           
           # Verify successful registration
           assert "Profil" in browser.title
           welcome_message = browser.find_element(By.CSS_SELECTOR, ".alert-success")
           assert "Compte créé avec succès" in welcome_message.text
       
       def test_user_login_logout_flow(self, browser, live_server):
           """Test user login and logout workflow"""
           # Create test user
           user = UserFactory(username="testuser", email="test@example.com")
           user.set_password("TestPass123!")
           user.save()
           
           # Navigate to login page
           browser.get(f"{live_server.url}/compte/connexion/")
           
           # Fill login form
           browser.find_element(By.NAME, "username").send_keys("testuser")
           browser.find_element(By.NAME, "password").send_keys("TestPass123!")
           browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
           
           # Wait for redirect after login
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".user-menu"))
           )
           
           # Verify login success
           user_menu = browser.find_element(By.CSS_SELECTOR, ".user-menu")
           assert user.get_full_name() in user_menu.text
           
           # Test logout
           browser.find_element(By.CSS_SELECTOR, ".logout-btn").click()
           
           # Verify logout
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".login-btn"))
           )
           assert browser.find_element(By.CSS_SELECTOR, ".login-btn")
   ```

3. **Product Browsing & Search Flow**
   ```python
   # tests/e2e/test_product_browsing.py
   import pytest
   from selenium.webdriver.common.by import By
   from selenium.webdriver.common.keys import Keys
   from selenium.webdriver.support.ui import WebDriverWait, Select
   from selenium.webdriver.support import expected_conditions as EC
   from tests.factories import ProductFactory, CategoryFactory
   
   @pytest.mark.e2e
   class TestProductBrowsing:
       def test_homepage_to_product_detail_flow(self, browser, live_server):
           """Test navigation from homepage to product detail"""
           # Create test products
           category = CategoryFactory(name="Agricole", slug="agricole")
           product = ProductFactory(
               name="Café des Montagnes Bleues",
               category=category,
               is_featured=True
           )
           
           # Navigate to homepage
           browser.get(live_server.url)
           
           # Verify featured products section exists
           featured_section = browser.find_element(By.CSS_SELECTOR, ".featured-products")
           assert featured_section.is_displayed()
           
           # Click on featured product
           product_card = browser.find_element(
               By.CSS_SELECTOR, 
               f"[data-product-id='{product.id}']"
           )
           product_link = product_card.find_element(By.TAG_NAME, "a")
           product_link.click()
           
           # Wait for product detail page
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".product-detail"))
           )
           
           # Verify product details
           assert product.name in browser.title
           product_name = browser.find_element(By.CSS_SELECTOR, "h1")
           assert product.name in product_name.text
       
       def test_category_browsing_with_filters(self, browser, live_server):
           """Test category browsing with price filters"""
           category = CategoryFactory(name="Services", slug="services")
           ProductFactory.create_batch(
               5, 
               category=category,
               price__range=(50, 200)
           )
           
           # Navigate to category page
           browser.get(f"{live_server.url}/categorie/services/")
           
           # Apply price filter
           min_price = browser.find_element(By.NAME, "min_price")
           min_price.clear()
           min_price.send_keys("100")
           
           max_price = browser.find_element(By.NAME, "max_price")
           max_price.clear()
           max_price.send_keys("150")
           
           # Apply filter
           filter_btn = browser.find_element(By.CSS_SELECTOR, ".apply-filters")
           filter_btn.click()
           
           # Wait for filtered results
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".product-grid"))
           )
           
           # Verify filtered results
           product_cards = browser.find_elements(By.CSS_SELECTOR, ".product-card")
           for card in product_cards:
               price_element = card.find_element(By.CSS_SELECTOR, ".current-price")
               price_text = price_element.text.replace("HTG", "").strip()
               price_value = float(price_text)
               assert 100 <= price_value <= 150
       
       def test_product_search_functionality(self, browser, live_server):
           """Test product search with results"""
           # Create searchable products
           ProductFactory(name="Café Haïtien Premium", description="Excellent café local")
           ProductFactory(name="Artisanat Traditionnel", description="Art haïtien authentique")
           
           # Navigate to homepage
           browser.get(live_server.url)
           
           # Use search functionality
           search_input = browser.find_element(By.CSS_SELECTOR, "input[name='query']")
           search_input.send_keys("café")
           search_input.send_keys(Keys.RETURN)
           
           # Wait for search results
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results"))
           )
           
           # Verify search results
           results = browser.find_elements(By.CSS_SELECTOR, ".product-card")
           assert len(results) >= 1
           
           # Check that results contain search term
           for result in results:
               product_name = result.find_element(By.CSS_SELECTOR, "h3").text
               assert "café" in product_name.lower()
   ```

4. **Shopping Cart & Checkout Flow**
   ```python
   # tests/e2e/test_shopping_cart.py
   import pytest
   from decimal import Decimal
   from selenium.webdriver.common.by import By
   from selenium.webdriver.support.ui import WebDriverWait
   from selenium.webdriver.support import expected_conditions as EC
   from tests.factories import ProductFactory, UserFactory
   
   @pytest.mark.e2e
   class TestShoppingCart:
       def test_complete_purchase_flow(self, browser, live_server):
           """Test complete purchase workflow from product to checkout"""
           # Create test data
           user = UserFactory()
           user.set_password("TestPass123!")
           user.save()
           
           product = ProductFactory(
               name="Test Product",
               price=Decimal('25.00'),
               stock_quantity=10
           )
           
           # Login first
           browser.get(f"{live_server.url}/compte/connexion/")
           browser.find_element(By.NAME, "username").send_keys(user.username)
           browser.find_element(By.NAME, "password").send_keys("TestPass123!")
           browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
           
           # Navigate to product detail
           browser.get(f"{live_server.url}/produit/{product.slug}/")
           
           # Add to cart
           qty_input = browser.find_element(By.NAME, "quantity")
           qty_input.clear()
           qty_input.send_keys("2")
           
           add_to_cart_btn = browser.find_element(By.CSS_SELECTOR, ".btn-add-cart")
           add_to_cart_btn.click()
           
           # Wait for cart update confirmation
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
           )
           
           # Navigate to cart
           browser.find_element(By.CSS_SELECTOR, ".cart-btn").click()
           
           # Verify cart contents
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".cart-items"))
           )
           
           cart_item = browser.find_element(By.CSS_SELECTOR, ".cart-item")
           assert product.name in cart_item.text
           
           # Proceed to checkout
           checkout_btn = browser.find_element(By.CSS_SELECTOR, ".btn-checkout")
           checkout_btn.click()
           
           # Fill shipping information
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".checkout-form"))
           )
           
           browser.find_element(By.NAME, "shipping_address").send_keys("123 Rue Test, Port-au-Prince")
           browser.find_element(By.NAME, "shipping_city").send_keys("Port-au-Prince")
           browser.find_element(By.NAME, "shipping_phone").send_keys("+509 1234-5678")
           
           # Continue to payment (mock MonCash for E2E)
           payment_btn = browser.find_element(By.CSS_SELECTOR, ".btn-payment")
           payment_btn.click()
           
           # Verify order creation
           WebDriverWait(browser, 15).until(
               EC.url_contains("/commande/confirmation/")
           )
           
           # Verify order confirmation page
           confirmation_msg = browser.find_element(By.CSS_SELECTOR, ".order-confirmation")
           assert "Commande confirmée" in confirmation_msg.text
       
       def test_cart_quantity_updates(self, browser, live_server):
           """Test cart quantity update functionality"""
           # Setup test data
           user = UserFactory()
           user.set_password("TestPass123!")
           user.save()
           
           product = ProductFactory(stock_quantity=20)
           
           # Login and add product to cart
           self._login_user(browser, live_server, user)
           self._add_product_to_cart(browser, live_server, product, quantity=3)
           
           # Navigate to cart
           browser.get(f"{live_server.url}/panier/")
           
           # Update quantity
           qty_input = browser.find_element(By.CSS_SELECTOR, ".quantity-input input")
           qty_input.clear()
           qty_input.send_keys("5")
           
           update_btn = browser.find_element(By.CSS_SELECTOR, ".update-quantity")
           update_btn.click()
           
           # Wait for quantity update
           WebDriverWait(browser, 10).until(
               EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".quantity-input input"), "5")
           )
           
           # Verify total price updated
           total_element = browser.find_element(By.CSS_SELECTOR, ".cart-total")
           expected_total = float(product.price) * 5
           assert f"{expected_total:.2f}" in total_element.text
       
       def _login_user(self, browser, live_server, user):
           """Helper method to login user"""
           browser.get(f"{live_server.url}/compte/connexion/")
           browser.find_element(By.NAME, "username").send_keys(user.username)
           browser.find_element(By.NAME, "password").send_keys("TestPass123!")
           browser.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
       
       def _add_product_to_cart(self, browser, live_server, product, quantity=1):
           """Helper method to add product to cart"""
           browser.get(f"{live_server.url}/produit/{product.slug}/")
           
           qty_input = browser.find_element(By.NAME, "quantity")
           qty_input.clear()
           qty_input.send_keys(str(quantity))
           
           browser.find_element(By.CSS_SELECTOR, ".btn-add-cart").click()
           
           WebDriverWait(browser, 10).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
           )
   ```

5. **Performance Testing Setup**
   ```python
   # tests/performance/locustfile.py
   from locust import HttpUser, task, between
   import random
   
   class MarketplaceUser(HttpUser):
       wait_time = between(1, 3)
       
       def on_start(self):
           """Setup for each simulated user"""
           # Login user for authenticated requests
           self.login()
       
       def login(self):
           """Login user session"""
           response = self.client.get("/compte/connexion/")
           csrf_token = self.extract_csrf_token(response.text)
           
           self.client.post("/compte/connexion/", {
               "username": "testuser",
               "password": "testpass",
               "csrfmiddlewaretoken": csrf_token
           })
       
       @task(3)
       def browse_homepage(self):
           """Browse homepage - most common action"""
           self.client.get("/")
       
       @task(2)
       def browse_categories(self):
           """Browse different categories"""
           categories = ["agricole", "patriotiques", "services", "premiere-necessite"]
           category = random.choice(categories)
           self.client.get(f"/categorie/{category}/")
       
       @task(2)
       def view_products(self):
           """View individual product pages"""
           # This would need actual product slugs from database
           response = self.client.get("/produits/")
           if response.status_code == 200:
               # Extract product URLs from response and visit random ones
               pass
       
       @task(1)
       def search_products(self):
           """Perform product searches"""
           search_terms = ["café", "artisanat", "service", "agriculture"]
           term = random.choice(search_terms)
           self.client.get(f"/recherche/?query={term}")
       
       @task(1)
       def add_to_cart(self):
           """Add items to shopping cart"""
           # This would simulate adding products to cart
           pass
       
       def extract_csrf_token(self, html):
           """Extract CSRF token from HTML"""
           # Simple extraction - in real scenario use proper parsing
           import re
           match = re.search(r'csrf_token.*?value="([^"]*)"', html)
           return match.group(1) if match else ""
   ```

6. **Cross-Browser Testing Configuration**
   ```python
   # tests/e2e/conftest.py (browser fixtures)
   import pytest
   from selenium import webdriver
   from selenium.webdriver.chrome.options import Options as ChromeOptions
   from selenium.webdriver.firefox.options import Options as FirefoxOptions
   
   @pytest.fixture(params=["chrome", "firefox"])
   def multi_browser(request):
       """Test across multiple browsers"""
       if request.param == "chrome":
           chrome_options = ChromeOptions()
           chrome_options.add_argument("--headless")
           driver = webdriver.Chrome(options=chrome_options)
       elif request.param == "firefox":
           firefox_options = FirefoxOptions()
           firefox_options.add_argument("--headless")
           driver = webdriver.Firefox(options=firefox_options)
       
       driver.implicitly_wait(10)
       yield driver
       driver.quit()
   
   @pytest.fixture(params=["desktop", "tablet", "mobile"])
   def responsive_browser(request):
       """Test responsive design across device sizes"""
       chrome_options = ChromeOptions()
       chrome_options.add_argument("--headless")
       
       if request.param == "desktop":
           chrome_options.add_argument("--window-size=1920,1080")
       elif request.param == "tablet":
           chrome_options.add_argument("--window-size=768,1024")
       elif request.param == "mobile":
           chrome_options.add_argument("--window-size=375,667")
       
       driver = webdriver.Chrome(options=chrome_options)
       driver.implicitly_wait(10)
       yield driver
       driver.quit()
   ```

#### Acceptance Criteria
- [ ] All critical user journeys tested end-to-end
- [ ] Tests run successfully across different browsers
- [ ] Mobile responsiveness validated
- [ ] Performance benchmarks established
- [ ] Automated test execution in CI/CD pipeline

---

## Phase 9: Frontend Enhancement & Finalization

### Task 9: Complete Frontend Implementation
**Priority**: High | **Estimated Time**: 20 hours

#### Objective
Implement a modern, responsive, and interactive frontend that provides an excellent user experience while maintaining the Haitian cultural identity and supporting the marketplace's business objectives.

#### Deliverables
- [ ] Complete CSS framework implementation
- [ ] Interactive JavaScript components
- [ ] Mobile-optimized responsive design
- [ ] Accessibility compliance
- [ ] Performance optimization

#### Implementation Steps

1. **Advanced CSS Architecture**
   ```scss
   // static/scss/main.scss
   @import 'abstracts/variables';
   @import 'abstracts/functions';
   @import 'abstracts/mixins';
   
   @import 'base/reset';
   @import 'base/typography';
   @import 'base/utilities';
   
   @import 'layout/header';
   @import 'layout/footer';
   @import 'layout/grid';
   
   @import 'components/buttons';
   @import 'components/cards';
   @import 'components/forms';
   @import 'components/modals';
   @import 'components/carousel';
   @import 'components/product-gallery';
   
   @import 'pages/home';
   @import 'pages/product-detail';
   @import 'pages/category';
   @import 'pages/checkout';
   
   // static/scss/abstracts/_variables.scss
   :root {
     // Brand Colors
     --primary-orange: #E67E22;
     --primary-orange-dark: #D35400;
     --primary-orange-light: #F39C12;
     --primary-orange-pale: #FDF2E9;
     
     // Semantic Colors
     --success: #27AE60;
     --warning: #F39C12;
     --danger: #E74C3C;
     --info: #3498DB;
     
     // Neutral Colors
     --white: #FFFFFF;
     --gray-50: #F8F9FA;
     --gray-100: #E9ECEF;
     --gray-200: #DEE2E6;
     --gray-300: #CED4DA;
     --gray-400: #ADB5BD;
     --gray-500: #6C757D;
     --gray-600: #495057;
     --gray-700: #343A40;
     --gray-800: #212529;
     --black: #000000;
     
     // Typography
     --font-family-base: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
     --font-family-heading: 'Inter', serif;
     
     // Font Sizes (fluid typography)
     --font-size-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
     --font-size-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);
     --font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
     --font-size-lg: clamp(1.125rem, 1rem + 0.625vw, 1.25rem);
     --font-size-xl: clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem);
     --font-size-2xl: clamp(1.5rem, 1.3rem + 1vw, 2rem);
     --font-size-3xl: clamp(1.875rem, 1.6rem + 1.375vw, 2.5rem);
     --font-size-4xl: clamp(2.25rem, 1.9rem + 1.75vw, 3rem);
     
     // Spacing Scale
     --space-xs: 0.25rem;   // 4px
     --space-sm: 0.5rem;    // 8px
     --space-md: 1rem;      // 16px
     --space-lg: 1.5rem;    // 24px
     --space-xl: 2rem;      // 32px
     --space-2xl: 3rem;     // 48px
     --space-3xl: 4rem;     // 64px
     --space-4xl: 6rem;     // 96px
     
     // Border Radius
     --radius-sm: 0.375rem;  // 6px
     --radius-md: 0.5rem;    // 8px
     --radius-lg: 0.75rem;   // 12px
     --radius-xl: 1rem;      // 16px
     --radius-full: 9999px;
     
     // Shadows
     --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
     --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
     --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
     --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
     --shadow-orange: 0 4px 20px rgba(230, 126, 34, 0.15);
     
     // Transitions
     --transition-fast: 150ms ease-in-out;
     --transition-base: 200ms ease-in-out;
     --transition-slow: 300ms ease-in-out;
     
     // Z-Index Scale
     --z-dropdown: 1000;
     --z-sticky: 1020;
     --z-fixed: 1030;
     --z-modal-backdrop: 1040;
     --z-modal: 1050;
     --z-popover: 1060;
     --z-tooltip: 1070;
   }
   ```

2. **Interactive JavaScript Components**
   ```javascript
   // static/js/components/carousel.js
   class HeroCarousel {
     constructor(element) {
       this.carousel = element;
       this.slides = element.querySelectorAll('.carousel-slide');
       this.dots = element.querySelectorAll('.dot');
       this.prevBtn = element.querySelector('.carousel-nav.prev');
       this.nextBtn = element.querySelector('.carousel-nav.next');
       this.currentSlide = 0;
       this.autoplayInterval = null;
       
       this.init();
     }
     
     init() {
       this.bindEvents();
       this.startAutoplay();
       this.updateDots();
     }
     
     bindEvents() {
       this.prevBtn?.addEventListener('click', () => this.prevSlide());
       this.nextBtn?.addEventListener('click', () => this.nextSlide());
       
       this.dots.forEach((dot, index) => {
         dot.addEventListener('click', () => this.goToSlide(index));
       });
       
       // Pause autoplay on hover
       this.carousel.addEventListener('mouseenter', () => this.stopAutoplay());
       this.carousel.addEventListener('mouseleave', () => this.startAutoplay());
       
       // Handle swipe gestures on mobile
       this.bindSwipeEvents();
     }
     
     bindSwipeEvents() {
       let startX = 0;
       let endX = 0;
       
       this.carousel.addEventListener('touchstart', (e) => {
         startX = e.touches[0].clientX;
       });
       
       this.carousel.addEventListener('touchend', (e) => {
         endX = e.changedTouches[0].clientX;
         const diffX = startX - endX;
         
         if (Math.abs(diffX) > 50) { // Minimum swipe distance
           if (diffX > 0) {
             this.nextSlide();
           } else {
             this.prevSlide();
           }
         }
       });
     }
     
     goToSlide(index) {
       this.slides[this.currentSlide].classList.remove('active');
       this.dots[this.currentSlide].classList.remove('active');
       
       this.currentSlide = index;
       
       this.slides[this.currentSlide].classList.add('active');
       this.dots[this.currentSlide].classList.add('active');
     }
     
     nextSlide() {
       const nextIndex = (this.currentSlide + 1) % this.slides.length;
       this.goToSlide(nextIndex);
     }
     
     prevSlide() {
       const prevIndex = (this.currentSlide - 1 + this.slides.length) % this.slides.length;
       this.goToSlide(prevIndex);
     }
     
     startAutoplay() {
       this.stopAutoplay();
       this.autoplayInterval = setInterval(() => {
         this.nextSlide();
       }, 5000); // 5 seconds
     }
     
     stopAutoplay() {
       if (this.autoplayInterval) {
         clearInterval(this.autoplayInterval);
         this.autoplayInterval = null;
       }
     }
     
     updateDots() {
       this.dots.forEach((dot, index) => {
         dot.classList.toggle('active', index === this.currentSlide);
       });
     }
   }
   
   // static/js/components/product-gallery.js
   class ProductGallery {
     constructor(element) {
       this.gallery = element;
       this.mainImage = element.querySelector('#main-product-image');
       this.thumbnails = element.querySelectorAll('.thumbnail');
       this.zoomContainer = element.querySelector('#image-zoom');
       
       this.init();
     }
     
     init() {
       this.bindEvents();
       this.initZoom();
     }
     
     bindEvents() {
       this.thumbnails.forEach(thumbnail => {
         thumbnail.addEventListener('click', (e) => {
           e.preventDefault();
           const newImage = thumbnail.dataset.image;
           this.changeMainImage(newImage);
           this.setActiveThumbnail(thumbnail);
         });
       });
     }
     
     changeMainImage(imageSrc) {
       // Smooth transition
       this.mainImage.style.opacity = '0';
       
       setTimeout(() => {
         this.mainImage.src = imageSrc;
         this.mainImage.style.opacity = '1';
       }, 150);
     }
     
     setActiveThumbnail(activeThumbnail) {
       this.thumbnails.forEach(thumb => thumb.classList.remove('active'));
       activeThumbnail.classList.add('active');
     }
     
     initZoom() {
       this.mainImage.addEventListener('mousemove', (e) => {
         const rect = this.mainImage.getBoundingClientRect();
         const x = ((e.clientX - rect.left) / rect.width) * 100;
         const y = ((e.clientY - rect.top) / rect.height) * 100;
         
         this.zoomContainer.style.backgroundImage = `url(${this.mainImage.src})`;
         this.zoomContainer.style.backgroundPosition = `${x}% ${y}%`;
         this.zoomContainer.style.opacity = '1';
       });
       
       this.mainImage.addEventListener('mouseleave', () => {
         this.zoomContainer.style.opacity = '0';
       });
     }
   }
   
   // static/js/components/cart.js
   class ShoppingCart {
     constructor() {
       this.cartCount = 0;
       this.cartTotal = 0;
       this.init();
     }
     
     init() {
       this.bindEvents();
       this.updateCartUI();
     }
     
     bindEvents() {
       // Add to cart buttons
       document.addEventListener('click', (e) => {
         if (e.target.classList.contains('btn-add-cart')) {
           e.preventDefault();
           const productId = e.target.dataset.product;
           const quantity = this.getQuantity(e.target);
           this.addToCart(productId, quantity);
         }
       });
       
       // Quantity update buttons
       document.addEventListener('click', (e) => {
         if (e.target.classList.contains('qty-btn')) {
           e.preventDefault();
           const action = e.target.dataset.action;
           const input = e.target.closest('.quantity-input').querySelector('input');
           this.updateQuantity(input, action);
         }
       });
       
       // Remove from cart buttons
       document.addEventListener('click', (e) => {
         if (e.target.classList.contains('btn-remove-cart')) {
           e.preventDefault();
           const itemId = e.target.dataset.item;
           this.removeFromCart(itemId);
         }
       });
     }
     
     async addToCart(productId, quantity = 1) {
       try {
         const response = await fetch('/panier/ajouter/', {
           method: 'POST',
           headers: {
             'Content-Type': 'application/x-www-form-urlencoded',
             'X-CSRFToken': this.getCsrfToken(),
           },
           body: new URLSearchParams({
             product_id: productId,
             quantity: quantity
           })
         });
         
         const data = await response.json();
         
         if (data.success) {
           this.showNotification('Produit ajouté au panier', 'success');
           this.updateCartCount(data.cart_count);
           this.updateCartTotal(data.cart_total);
         } else {
           this.showNotification(data.message, 'error');
         }
       } catch (error) {
         console.error('Error adding to cart:', error);
         this.showNotification('Erreur lors de l\'ajout au panier', 'error');
       }
     }
     
     getQuantity(button) {
       const productCard = button.closest('.product-card, .product-detail');
       const quantityInput = productCard?.querySelector('input[name="quantity"]');
       return quantityInput ? parseInt(quantityInput.value) : 1;
     }
     
     updateQuantity(input, action) {
       const currentValue = parseInt(input.value) || 1;
       const maxValue = parseInt(input.max) || 999;
       
       if (action === 'increase' && currentValue < maxValue) {
         input.value = currentValue + 1;
       } else if (action === 'decrease' && currentValue > 1) {
         input.value = currentValue - 1;
       }
       
       // Trigger change event for any listeners
       input.dispatchEvent(new Event('change'));
     }
     
     showNotification(message, type = 'info') {
       const notification = document.createElement('div');
       notification.className = `notification notification-${type}`;
       notification.innerHTML = `
         <div class="notification-content">
           <span class="notification-message">${message}</span>
           <button class="notification-close">&times;</button>
         </div>
       `;
       
       document.body.appendChild(notification);
       
       // Auto-hide after 3 seconds
       setTimeout(() => {
         notification.classList.add('fade-out');
         setTimeout(() => notification.remove(), 300);
       }, 3000);
       
       // Manual close
       notification.querySelector('.notification-close').addEventListener('click', () => {
         notification.classList.add('fade-out');
         setTimeout(() => notification.remove(), 300);
       });
     }
     
     updateCartCount(count) {
       this.cartCount = count;
       const cartCountElements = document.querySelectorAll('.cart-count');
       cartCountElements.forEach(el => {
         el.textContent = count;
         el.style.display = count > 0 ? 'inline' : 'none';
       });
     }
     
     updateCartTotal(total) {
       this.cartTotal = total;
       const cartTotalElements = document.querySelectorAll('.cart-total');
       cartTotalElements.forEach(el => {
         el.textContent = `${total} HTG`;
       });
     }
     
     getCsrfToken() {
       return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
     }
   }
   ```

3. **Mobile-First Responsive Design**
   ```scss
   // static/scss/layout/_grid.scss
   .container {
     width: 100%;
     max-width: 1200px;
     margin: 0 auto;
     padding: 0 var(--space-md);
     
     @media (min-width: 768px) {
       padding: 0 var(--space-lg);
     }
     
     @media (min-width: 1024px) {
       padding: 0 var(--space-xl);
     }
   }
   
   .grid {
     display: grid;
     gap: var(--space-md);
     
     &--2-cols {
       grid-template-columns: 1fr;
       
       @media (min-width: 768px) {
         grid-template-columns: 1fr 1fr;
       }
     }
     
     &--3-cols {
       grid-template-columns: 1fr;
       
       @media (min-width: 768px) {
         grid-template-columns: 1fr 1fr;
       }
       
       @media (min-width: 1024px) {
         grid-template-columns: repeat(3, 1fr);
       }
     }
     
     &--4-cols {
       grid-template-columns: 1fr;
       
       @media (min-width: 480px) {
         grid-template-columns: 1fr 1fr;
       }
       
       @media (min-width: 768px) {
         grid-template-columns: repeat(3, 1fr);
       }
       
       @media (min-width: 1024px) {
         grid-template-columns: repeat(4, 1fr);
       }
     }
   }
   
   // static/scss/layout/_header.scss
   .main-header {
     background: var(--white);
     border-bottom: 1px solid var(--gray-200);
     position: sticky;
     top: 0;
     z-index: var(--z-sticky);
     
     .header-container {
       display: flex;
       align-items: center;
       justify-content: space-between;
       min-height: 70px;
       gap: var(--space-md);
       
       @media (max-width: 767px) {
         flex-wrap: wrap;
         min-height: auto;
         padding: var(--space-sm) 0;
       }
     }
     
     .logo-section {
       display: flex;
       align-items: center;
       gap: var(--space-sm);
       
       img {
         height: 40px;
         width: auto;
       }
       
       .tagline {
         font-size: var(--font-size-sm);
         color: var(--gray-600);
         
         @media (max-width: 767px) {
           display: none;
         }
       }
     }
     
     .main-navigation {
       display: none;
       
       @media (min-width: 768px) {
         display: flex;
         gap: var(--space-lg);
       }
       
       .nav-item {
         display: flex;
         flex-direction: column;
         align-items: center;
         gap: var(--space-xs);
         text-decoration: none;
         color: var(--gray-700);
         font-weight: 500;
         transition: color var(--transition-fast);
         
         &:hover {
           color: var(--primary-orange);
         }
         
         icon {
           font-size: var(--font-size-lg);
         }
       }
     }
     
     .search-bar {
       flex: 1;
       max-width: 400px;
       position: relative;
       
       @media (max-width: 767px) {
         order: 3;
         flex-basis: 100%;
         max-width: none;
         margin-top: var(--space-sm);
       }
       
       input {
         width: 100%;
         padding: var(--space-sm) var(--space-lg) var(--space-sm) var(--space-md);
         border: 2px solid var(--gray-300);
         border-radius: var(--radius-lg);
         font-size: var(--font-size-base);
         transition: border-color var(--transition-fast);
         
         &:focus {
           outline: none;
           border-color: var(--primary-orange);
         }
         
         &::placeholder {
           color: var(--gray-500);
         }
       }
       
       button {
         position: absolute;
         right: var(--space-sm);
         top: 50%;
         transform: translateY(-50%);
         background: var(--primary-orange);
         color: white;
         border: none;
         border-radius: var(--radius-md);
         padding: var(--space-sm);
         cursor: pointer;
         transition: background-color var(--transition-fast);
         
         &:hover {
           background: var(--primary-orange-dark);
         }
       }
     }
     
     .user-actions {
       display: flex;
       align-items: center;
       gap: var(--space-sm);
       
       .btn-icon {
         background: transparent;
         border: none;
         font-size: var(--font-size-lg);
         color: var(--gray-700);
         cursor: pointer;
         padding: var(--space-sm);
         border-radius: var(--radius-md);
         transition: color var(--transition-fast), background-color var(--transition-fast);
         position: relative;
         
         &:hover {
           background: var(--gray-100);
           color: var(--primary-orange);
         }
         
         &.cart-btn .cart-count {
           position: absolute;
           top: 0;
           right: 0;
           background: var(--primary-orange);
           color: white;
           font-size: var(--font-size-xs);
           font-weight: 600;
           padding: 2px 6px;
           border-radius: var(--radius-full);
           min-width: 18px;
           text-align: center;
         }
       }
     }
     
     // Mobile menu toggle
     .mobile-menu-toggle {
       display: block;
       background: transparent;
       border: none;
       font-size: var(--font-size-xl);
       color: var(--gray-700);
       cursor: pointer;
       
       @media (min-width: 768px) {
         display: none;
       }
     }
     
     // Mobile navigation
     .mobile-navigation {
       display: none;
       position: fixed;
       top: 100%;
       left: 0;
       right: 0;
       background: white;
       border-top: 1px solid var(--gray-200);
       padding: var(--space-lg);
       z-index: var(--z-dropdown);
       
       &.active {
         display: block;
       }
       
       @media (min-width: 768px) {
         display: none !important;
       }
       
       .mobile-nav-item {
         display: block;
         padding: var(--space-md) 0;
         text-decoration: none;
         color: var(--gray-700);
         font-weight: 500;
         border-bottom: 1px solid var(--gray-100);
         
         &:last-child {
           border-bottom: none;
         }
         
         &:hover {
           color: var(--primary-orange);
         }
       }
     }
   }
   
   // static/scss/components/_product-card.scss
   .product-card {
     background: var(--white);
     border-radius: var(--radius-lg);
     overflow: hidden;
     box-shadow: var(--shadow-sm);
     transition: transform var(--transition-base), box-shadow var(--transition-base);
     
     &:hover {
       transform: translateY(-4px);
       box-shadow: var(--shadow-lg);
     }
     
     .product-image {
       position: relative;
       aspect-ratio: 1;
       overflow: hidden;
       
       img {
         width: 100%;
         height: 100%;
         object-fit: cover;
         transition: transform var(--transition-slow);
       }
       
       &:hover img {
         transform: scale(1.05);
       }
       
       .product-actions {
         position: absolute;
         top: var(--space-sm);
         right: var(--space-sm);
         display: flex;
         flex-direction: column;
         gap: var(--space-xs);
         opacity: 0;
         transition: opacity var(--transition-base);
       }
       
       &:hover .product-actions {
         opacity: 1;
       }
       
       .btn-quick-view,
       .btn-favorite {
         background: rgba(255, 255, 255, 0.9);
         backdrop-filter: blur(4px);
         border: none;
         border-radius: var(--radius-md);
         padding: var(--space-sm);
         font-size: var(--font-size-sm);
         cursor: pointer;
         transition: background-color var(--transition-fast);
         
         &:hover {
           background: white;
         }
       }
       
       .product-badge {
         position: absolute;
         top: var(--space-sm);
         left: var(--space-sm);
         background: var(--primary-orange);
         color: white;
         font-size: var(--font-size-xs);
         font-weight: 600;
         padding: var(--space-xs) var(--space-sm);
         border-radius: var(--radius-md);
         text-transform: uppercase;
         
         &.discount {
           background: var(--danger);
         }
         
         &.new {
           background: var(--success);
         }
       }
     }
     
     .product-info {
       padding: var(--space-lg);
       
       .product-category {
         font-size: var(--font-size-sm);
         color: var(--primary-orange);
         font-weight: 500;
         text-transform: uppercase;
         letter-spacing: 0.5px;
         margin-bottom: var(--space-xs);
       }
       
       h3 {
         margin: 0 0 var(--space-sm) 0;
         font-size: var(--font-size-lg);
         font-weight: 600;
         line-height: 1.3;
         
         a {
           text-decoration: none;
           color: var(--gray-800);
           transition: color var(--transition-fast);
           
           &:hover {
             color: var(--primary-orange);
           }
         }
       }
       
       .product-rating {
         display: flex;
         align-items: center;
         gap: var(--space-xs);
         margin-bottom: var(--space-sm);
         
         .star {
           color: var(--warning);
           font-size: var(--font-size-sm);
           
           &:not(.filled) {
             color: var(--gray-300);
           }
         }
         
         .rating-count {
           font-size: var(--font-size-sm);
           color: var(--gray-500);
         }
       }
       
       .product-price {
         display: flex;
         align-items: center;
         gap: var(--space-sm);
         margin-bottom: var(--space-md);
         
         .current-price {
           font-size: var(--font-size-xl);
           font-weight: 700;
           color: var(--primary-orange);
         }
         
         .original-price {
           font-size: var(--font-size-lg);
           color: var(--gray-500);
           text-decoration: line-through;
         }
         
         .discount {
           background: var(--danger);
           color: white;
           font-size: var(--font-size-xs);
           font-weight: 600;
           padding: var(--space-xs) var(--space-sm);
           border-radius: var(--radius-md);
         }
       }
       
       .product-vendor {
         font-size: var(--font-size-sm);
         color: var(--gray-600);
         margin-bottom: var(--space-md);
       }
       
       .btn-add-cart {
         width: 100%;
         background: var(--primary-orange);
         color: white;
         border: none;
         border-radius: var(--radius-md);
         padding: var(--space-md);
         font-weight: 600;
         cursor: pointer;
         transition: background-color var(--transition-fast);
         
         &:hover {
           background: var(--primary-orange-dark);
         }
         
         &:disabled {
           background: var(--gray-400);
           cursor: not-allowed;
         }
       }
     }
   }
   ```

4. **Accessibility Implementation**
   ```javascript
   // static/js/accessibility.js
   class AccessibilityEnhancements {
     constructor() {
       this.init();
     }
     
     init() {
       this.setupKeyboardNavigation();
       this.setupFocusManagement();
       this.setupAriaLiveRegions();
       this.setupSkipLinks();
       this.addTouchTargetHelpers();
     }
     
     setupKeyboardNavigation() {
       // Keyboard navigation for custom components
       document.addEventListener('keydown', (e) => {
         // Escape key to close modals/dropdowns
         if (e.key === 'Escape') {
           this.closeModals();
           this.closeDropdowns();
         }
         
         // Arrow key navigation for product grids
         if (e.target.closest('.products-grid')) {
           this.handleArrowNavigation(e);
         }
         
         // Enter/Space for button-like elements
         if ((e.key === 'Enter' || e.key === ' ') && e.target.hasAttribute('role') && e.target.getAttribute('role') === 'button') {
           e.preventDefault();
           e.target.click();
         }
       });
     }
     
     handleArrowNavigation(e) {
       const products = Array.from(document.querySelectorAll('.product-card a'));
       const currentIndex = products.indexOf(document.activeElement);
       
       if (currentIndex === -1) return;
       
       let newIndex;
       const columns = this.getGridColumns();
       
       switch (e.key) {
         case 'ArrowRight':
           newIndex = Math.min(currentIndex + 1, products.length - 1);
           break;
         case 'ArrowLeft':
           newIndex = Math.max(currentIndex - 1, 0);
           break;
         case 'ArrowDown':
           newIndex = Math.min(currentIndex + columns, products.length - 1);
           break;
         case 'ArrowUp':
           newIndex = Math.max(currentIndex - columns, 0);
           break;
         default:
           return;
       }
       
       e.preventDefault();
       products[newIndex].focus();
     }
     
     getGridColumns() {
       const grid = document.querySelector('.products-grid');
       if (!grid) return 1;
       
       const styles = window.getComputedStyle(grid);
       const columns = styles.gridTemplateColumns.split(' ').length;
       return columns;
     }
     
     setupFocusManagement() {
       // Focus trap for modals
       document.addEventListener('focusin', (e) => {
         const modal = e.target.closest('.modal.active');
         if (modal) {
           const focusableElements = modal.querySelectorAll(
             'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
           );
           
           if (focusableElements.length === 0) return;
           
           const firstElement = focusableElements[0];
           const lastElement = focusableElements[focusableElements.length - 1];
           
           // If focus moves outside modal, bring it back
           if (!modal.contains(e.target)) {
             firstElement.focus();
           }
         }
       });
       
       // Save focus state when opening modals
       document.addEventListener('click', (e) => {
         if (e.target.hasAttribute('data-modal-trigger')) {
           e.target.dataset.returnFocus = 'true';
         }
       });
     }
     
     setupAriaLiveRegions() {
       // Create live region for cart updates
       const cartLiveRegion = document.createElement('div');
       cartLiveRegion.setAttribute('aria-live', 'polite');
       cartLiveRegion.setAttribute('aria-atomic', 'true');
       cartLiveRegion.className = 'sr-only';
       cartLiveRegion.id = 'cart-live-region';
       document.body.appendChild(cartLiveRegion);
       
       // Create live region for form errors
       const errorLiveRegion = document.createElement('div');
       errorLiveRegion.setAttribute('aria-live', 'assertive');
       errorLiveRegion.setAttribute('aria-atomic', 'true');
       errorLiveRegion.className = 'sr-only';
       errorLiveRegion.id = 'error-live-region';
       document.body.appendChild(errorLiveRegion);
     }
     
     announceCartUpdate(message) {
       const liveRegion = document.getElementById('cart-live-region');
       if (liveRegion) {
         liveRegion.textContent = message;
       }
     }
     
     announceError(message) {
       const liveRegion = document.getElementById('error-live-region');
       if (liveRegion) {
         liveRegion.textContent = message;
       }
     }
     
     setupSkipLinks() {
       // Add skip to main content link
       const skipLink = document.createElement('a');
       skipLink.href = '#main-content';
       skipLink.textContent = 'Passer au contenu principal';
       skipLink.className = 'skip-link';
       skipLink.style.cssText = `
         position: absolute;
         top: -40px;
         left: 6px;
         background: var(--primary-orange);
         color: white;
         padding: 8px;
         text-decoration: none;
         border-radius: 4px;
         z-index: 1000;
         transition: top 0.3s;
       `;
       
       skipLink.addEventListener('focus', () => {
         skipLink.style.top = '6px';
       });
       
       skipLink.addEventListener('blur', () => {
         skipLink.style.top = '-40px';
       });
       
       document.body.insertBefore(skipLink, document.body.firstChild);
     }
     
     addTouchTargetHelpers() {
       // Ensure touch targets are at least 44px for mobile
       const style = document.createElement('style');
       style.textContent = `
         @media (pointer: coarse) {
           button, 
           input[type="button"], 
           input[type="submit"], 
           .btn,
           .btn-icon {
             min-height: 44px;
             min-width: 44px;
           }
         }
       `;
       document.head.appendChild(style);
     }
     
     closeModals() {
       const activeModals = document.querySelectorAll('.modal.active');
       activeModals.forEach(modal => {
         modal.classList.remove('active');
         
         // Return focus to trigger element
         const trigger = document.querySelector('[data-return-focus="true"]');
         if (trigger) {
           trigger.focus();
           trigger.removeAttribute('data-return-focus');
         }
       });
     }
     
     closeDropdowns() {
       const activeDropdowns = document.querySelectorAll('.dropdown.active');
       activeDropdowns.forEach(dropdown => {
         dropdown.classList.remove('active');
       });
     }
   }
   
   // Screen reader only utility class
   const srOnlyCSS = `
     .sr-only {
       position: absolute;
       width: 1px;
       height: 1px;
       padding: 0;
       margin: -1px;
       overflow: hidden;
       clip: rect(0, 0, 0, 0);
       white-space: nowrap;
       border: 0;
     }
   `;
   
   const style = document.createElement('style');
   style.textContent = srOnlyCSS;
   document.head.appendChild(style);
   ```

5. **Performance Optimization**
   ```javascript
   // static/js/performance.js
   class PerformanceOptimizer {
     constructor() {
       this.init();
     }
     
     init() {
       this.setupLazyLoading();
       this.setupImageOptimization();
       this.setupScrollOptimization();
       this.preloadCriticalResources();
       this.initServiceWorker();
     }
     
     setupLazyLoading() {
       // Intersection Observer for lazy loading images
       if ('IntersectionObserver' in window) {
         const imageObserver = new IntersectionObserver((entries, observer) => {
           entries.forEach(entry => {
             if (entry.isIntersecting) {
               const img = entry.target;
               img.src = img.dataset.src;
               img.classList.remove('lazy');
               observer.unobserve(img);
             }
           });
         }, {
           rootMargin: '50px 0px'
         });
         
         document.querySelectorAll('img[data-src]').forEach(img => {
           imageObserver.observe(img);
         });
       } else {
         // Fallback for older browsers
         document.querySelectorAll('img[data-src]').forEach(img => {
           img.src = img.dataset.src;
         });
       }
     }
     
     setupImageOptimization() {
       // Convert images to WebP if supported
       const supportsWebP = this.checkWebPSupport();
       
       if (supportsWebP) {
         document.querySelectorAll('img[data-webp]').forEach(img => {
           img.src = img.dataset.webp;
         });
       }
       
       // Responsive images based on screen size
       this.setupResponsiveImages();
     }
     
     checkWebPSupport() {
       return new Promise(resolve => {
         const webP = new Image();
         webP.onload = webP.onerror = () => {
           resolve(webP.height === 2);
         };
         webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
       });
     }
     
     setupResponsiveImages() {
       const updateImageSources = () => {
         const screenWidth = window.innerWidth;
         
         document.querySelectorAll('img[data-sizes]').forEach(img => {
           const sizes = JSON.parse(img.dataset.sizes);
           let appropriateSize = sizes.default;
           
           Object.keys(sizes).forEach(breakpoint => {
             if (breakpoint !== 'default' && screenWidth >= parseInt(breakpoint)) {
               appropriateSize = sizes[breakpoint];
             }
           });
           
           if (img.src !== appropriateSize) {
             img.src = appropriateSize;
           }
         });
       };
       
       // Update on resize (debounced)
       let resizeTimeout;
       window.addEventListener('resize', () => {
         clearTimeout(resizeTimeout);
         resizeTimeout = setTimeout(updateImageSources, 250);
       });
       
       updateImageSources();
     }
     
     setupScrollOptimization() {
       // Throttled scroll events
       let scrollTimeout;
       let isScrolling = false;
       
       const throttledScroll = (callback) => {
         if (!isScrolling) {
           requestAnimationFrame(() => {
             callback();
             isScrolling = false;
           });
           isScrolling = true;
         }
       };
       
       window.addEventListener('scroll', () => {
         throttledScroll(() => {
           this.handleScroll();
         });
       });
     }
     
     handleScroll() {
       const scrollY = window.scrollY;
       const header = document.querySelector('.main-header');
       
       // Add/remove scrolled class for header styling
       if (scrollY > 10) {
         header.classList.add('scrolled');
       } else {
         header.classList.remove('scrolled');
       }
       
       // Show/hide back to top button
       const backToTopBtn = document.getElementById('back-to-top');
       if (backToTopBtn) {
         if (scrollY > 300) {
           backToTopBtn.style.display = 'block';
         } else {
           backToTopBtn.style.display = 'none';
         }
       }
     }
     
     preloadCriticalResources() {
       // Preload critical CSS
       const criticalCSS = document.createElement('link');
       criticalCSS.rel = 'preload';
       criticalCSS.href = '/static/css/critical.css';
       criticalCSS.as = 'style';
       document.head.appendChild(criticalCSS);
       
       // Preload important fonts
       const font = document.createElement('link');
       font.rel = 'preload';
       font.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap';
       font.as = 'style';
       document.head.appendChild(font);
       
       // DNS prefetch for external resources
       const dnsPrefetch = document.createElement('link');
       dnsPrefetch.rel = 'dns-prefetch';
       dnsPrefetch.href = '//fonts.googleapis.com';
       document.head.appendChild(dnsPrefetch);
     }
     
     initServiceWorker() {
       if ('serviceWorker' in navigator) {
         navigator.serviceWorker.register('/sw.js')
           .then(registration => {
             console.log('Service Worker registered:', registration);
           })
           .catch(error => {
             console.log('Service Worker registration failed:', error);
           });
       }
     }
     
     // Critical rendering path optimization
     optimizeCriticalPath() {
       // Move non-critical CSS to load async
       const nonCriticalCSS = document.querySelectorAll('link[rel="stylesheet"]:not([data-critical])');
       nonCriticalCSS.forEach(link => {
         const href = link.href;
         link.media = 'print';
         link.onload = () => {
           link.media = 'all';
         };
         
         // Fallback for older browsers
         setTimeout(() => {
           link.media = 'all';
         }, 100);
       });
     }
   }
   
   // Initialize performance optimizations when DOM is ready
   if (document.readyState === 'loading') {
     document.addEventListener('DOMContentLoaded', () => {
       new PerformanceOptimizer();
     });
   } else {
     new PerformanceOptimizer();
   }
   ```

6. **Main Application Initialization**
   ```javascript
   // static/js/main.js
   document.addEventListener('DOMContentLoaded', function() {
     // Initialize core components
     initializeComponents();
     
     // Initialize accessibility enhancements
     new AccessibilityEnhancements();
     
     // Initialize shopping cart
     window.shoppingCart = new ShoppingCart();
     
     // Initialize search functionality
     initializeSearch();
     
     // Set up CSRF token for all AJAX requests
     setupCSRFToken();
     
     // Initialize animations
     initializeAnimations();
   });
   
   function initializeComponents() {
     // Initialize hero carousel
     const heroCarousel = document.querySelector('.hero-carousel');
     if (heroCarousel) {
       new HeroCarousel(heroCarousel);
     }
     
     // Initialize product galleries
     document.querySelectorAll('.product-gallery').forEach(gallery => {
       new ProductGallery(gallery);
     });
     
     // Initialize mobile menu
     const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
     const mobileMenu = document.querySelector('.mobile-navigation');
     
     if (mobileMenuToggle && mobileMenu) {
       mobileMenuToggle.addEventListener('click', () => {
         mobileMenu.classList.toggle('active');
         mobileMenuToggle.setAttribute('aria-expanded', 
           mobileMenu.classList.contains('active')
         );
       });
     }
     
     // Initialize modals
     document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
       trigger.addEventListener('click', (e) => {
         e.preventDefault();
         const modalId = trigger.dataset.modalTrigger;
         const modal = document.getElementById(modalId);
         if (modal) {
           openModal(modal);
         }
       });
     });
     
     // Initialize tooltips
     initializeTooltips();
   }
   
   function initializeSearch() {
     const searchForm = document.querySelector('.search-bar form');
     const searchInput = searchForm?.querySelector('input[name="query"]');
     
     if (searchInput) {
       // Search suggestions
       let searchTimeout;
       searchInput.addEventListener('input', (e) => {
         clearTimeout(searchTimeout);
         searchTimeout = setTimeout(() => {
           if (e.target.value.length >= 2) {
             fetchSearchSuggestions(e.target.value);
           }
         }, 300);
       });
       
       // Clear suggestions on focus out
       searchInput.addEventListener('blur', () => {
         setTimeout(() => {
           clearSearchSuggestions();
         }, 200);
       });
     }
   }
   
   async function fetchSearchSuggestions(query) {
     try {
       const response = await fetch(`/api/v1/autocomplete/?q=${encodeURIComponent(query)}`);
       const data = await response.json();
       displaySearchSuggestions(data.suggestions);
     } catch (error) {
       console.error('Search suggestions error:', error);
     }
   }
   
   function displaySearchSuggestions(suggestions) {
     let suggestionsContainer = document.getElementById('search-suggestions');
     
     if (!suggestionsContainer) {
       suggestionsContainer = document.createElement('div');
       suggestionsContainer.id = 'search-suggestions';
       suggestionsContainer.className = 'search-suggestions';
       document.querySelector('.search-bar').appendChild(suggestionsContainer);
     }
     
     suggestionsContainer.innerHTML = suggestions.map(suggestion => 
       `<button type="button" class="suggestion-item" data-query="${suggestion.query}">
         ${suggestion.name}
         <span class="suggestion-category">${suggestion.category}</span>
       </button>`
     ).join('');
     
     // Add click handlers
     suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
       item.addEventListener('click', () => {
         const query = item.dataset.query;
         document.querySelector('.search-bar input').value = query;
         document.querySelector('.search-bar form').submit();
       });
     });
   }
   
   function clearSearchSuggestions() {
     const container = document.getElementById('search-suggestions');
     if (container) {
       container.remove();
     }
   }
   
   function setupCSRFToken() {
     const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
     
     if (csrfToken) {
       // Set default headers for fetch requests
       const originalFetch = window.fetch;
       window.fetch = function(url, options = {}) {
         if (options.method && options.method.toUpperCase() !== 'GET') {
           options.headers = options.headers || {};
           options.headers['X-CSRFToken'] = csrfToken;
         }
         return originalFetch(url, options);
       };
     }
   }
   
   function openModal(modal) {
     modal.classList.add('active');
     modal.setAttribute('aria-hidden', 'false');
     
     // Focus first focusable element
     const focusableElement = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
     if (focusableElement) {
       focusableElement.focus();
     }
     
     // Close on backdrop click
     modal.addEventListener('click', (e) => {
       if (e.target === modal) {
         closeModal(modal);
       }
     });
     
     // Close button
     const closeBtn = modal.querySelector('.modal-close');
     if (closeBtn) {
       closeBtn.addEventListener('click', () => closeModal(modal));
     }
   }
   
   function closeModal(modal) {
     modal.classList.remove('active');
     modal.setAttribute('aria-hidden', 'true');
   }
   
   function initializeTooltips() {
     document.querySelectorAll('[data-tooltip]').forEach(element => {
       element.addEventListener('mouseenter', showTooltip);
       element.addEventListener('mouseleave', hideTooltip);
       element.addEventListener('focus', showTooltip);
       element.addEventListener('blur', hideTooltip);
     });
   }
   
   function showTooltip(e) {
     const tooltip = document.createElement('div');
     tooltip.className = 'tooltip';
     tooltip.textContent = e.target.dataset.tooltip;
     tooltip.setAttribute('role', 'tooltip');
     
     document.body.appendChild(tooltip);
     
     const rect = e.target.getBoundingClientRect();
     tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
     tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
     
     e.target.tooltipElement = tooltip;
   }
   
   function hideTooltip(e) {
     if (e.target.tooltipElement) {
       e.target.tooltipElement.remove();
       delete e.target.tooltipElement;
     }
   }
   
   function initializeAnimations() {
     // Intersection Observer for scroll animations
     if ('IntersectionObserver' in window) {
       const animationObserver = new IntersectionObserver((entries) => {
         entries.forEach(entry => {
           if (entry.isIntersecting) {
             entry.target.classList.add('animate-in');
             animationObserver.unobserve(entry.target);
           }
         });
       }, {
         threshold: 0.1,
         rootMargin: '0px 0px -50px 0px'
       });
       
       document.querySelectorAll('.animate-on-scroll').forEach(element => {
         animationObserver.observe(element);
       });
     }
   }
   
   // Back to top button
   const backToTopBtn = document.createElement('button');
   backToTopBtn.id = 'back-to-top';
   backToTopBtn.innerHTML = '↑';
   backToTopBtn.setAttribute('aria-label', 'Retour en haut');
   backToTopBtn.style.cssText = `
     position: fixed;
     bottom: 20px;
     right: 20px;
     background: var(--primary-orange);
     color: white;
     border: none;
     border-radius: 50%;
     width: 50px;
     height: 50px;
     font-size: 20px;
     cursor: pointer;
     display: none;
     z-index: 1000;
     box-shadow: var(--shadow-lg);
     transition: all var(--transition-base);
   `;
   
   backToTopBtn.addEventListener('click', () => {
     window.scrollTo({ top: 0, behavior: 'smooth' });
   });
   
   document.body.appendChild(backToTopBtn);
   ```

#### Acceptance Criteria
- [ ] Complete CSS framework with design system variables implemented
- [ ] All interactive components work smoothly across devices
- [ ] Mobile-first responsive design implemented and tested
- [ ] WCAG 2.1 AA accessibility compliance achieved
- [ ] Performance metrics: LCP < 2.5s, FID < 100ms, CLS < 0.1
- [ ] Cross-browser compatibility verified (Chrome, Firefox, Safari, Edge)
- [ ] Search functionality with autocomplete working
- [ ] Shopping cart updates without page refresh
- [ ] Image lazy loading and optimization implemented
- [ ] Keyboard navigation fully functional
- [ ] Screen reader compatibility verified

---

## Project Completion & Next Steps

### Task 10: Quality Assurance & Launch Preparation
**Priority**: High | **Estimated Time**: 8 hours

#### Final Checklist
- [ ] Complete test suite passes (unit, integration, E2E)
- [ ] Security audit completed
- [ ] Performance benchmarks met
- [ ] Accessibility compliance verified
- [ ] Cross-browser testing completed
- [ ] Mobile responsiveness validated
- [ ] MonCash integration tested in sandbox
- [ ] Database migrations tested in staging
- [ ] Error handling and logging configured
- [ ] Backup and recovery procedures documented

#### Launch Readiness Criteria
- [ ] Production environment configured
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Monitoring systems active
- [ ] Team training completed
- [ ] User documentation created
- [ ] Marketing materials prepared
- [ ] Launch communication plan executed

---

This comprehensive task list provides a structured approach to building the Afèpanou marketplace from foundation to launch. Each phase builds upon the previous ones, ensuring a solid, well-tested, and user-friendly platform that serves the Haitian entrepreneurial community effectively.