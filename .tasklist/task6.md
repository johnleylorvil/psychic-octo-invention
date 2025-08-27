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
