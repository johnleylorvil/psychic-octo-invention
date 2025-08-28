# Testing Troubleshooting Guide - Afèpanou Marketplace

## Common Test Issues and Solutions

### Database Issues

#### Issue: `django.db.utils.OperationalError: database is locked`
**Cause**: SQLite database is locked by another process or test transaction not closed properly.

**Solutions**:
```bash
# 1. Use --reuse-db flag to reuse test database
python -m pytest --ds=config.settings --reuse-db

# 2. Restart test database
python -m pytest --ds=config.settings --create-db

# 3. Clear SQLite lock (if exists)
rm db.sqlite3-journal
```

#### Issue: `IntegrityError: UNIQUE constraint failed`
**Cause**: Factory data collision or test data not properly cleaned.

**Solutions**:
```python
# Use sequences in factories
email = factory.Sequence(lambda n: f"user{n}@test.com")

# Or use LazyAttribute with uuid
from uuid import uuid4
email = factory.LazyAttribute(lambda obj: f"{uuid4().hex[:8]}@test.com")
```

#### Issue: `RelatedObjectDoesNotExist` errors
**Cause**: Missing related objects in factory or test data.

**Solutions**:
```python
# Use SubFactory for related objects
seller = factory.SubFactory(SellerUserFactory)

# Or create dependencies explicitly in tests
user = UserFactory()
product = ProductFactory(seller=user)
```

### Factory Issues

#### Issue: `FactoryError: Unable to create`
**Cause**: Invalid factory configuration or circular dependencies.

**Solutions**:
```python
# Check for circular imports in factories
# Use lazy imports if needed
def lazy_model():
    from marketplace.models import Product
    return Product

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = lazy_model

# Or use string references
class Meta:
    model = 'marketplace.Product'
```

#### Issue: `ValidationError` in factory creation
**Cause**: Factory data doesn't meet model validation requirements.

**Solutions**:
```python
# Add custom validation in factory
@factory.post_generation
def validate_data(obj, create, extracted, **kwargs):
    if create:
        obj.full_clean()  # Validate before save
```

### Performance Test Issues

#### Issue: `AssertionError: Query took X.XXs, expected < X.Xs`
**Cause**: Database queries not optimized or test environment too slow.

**Solutions**:
```python
# 1. Use select_related and prefetch_related
products = Product.objects.select_related('category', 'seller')\
                         .prefetch_related('images')

# 2. Add database indexes in model Meta
class Meta:
    indexes = [
        models.Index(fields=['is_active', 'created_at']),
    ]

# 3. Adjust performance expectations for test environment
assert query_time < 2.0  # More lenient for slow test environments
```

#### Issue: Memory usage tests failing
**Cause**: Other processes consuming memory or Python garbage collection.

**Solutions**:
```python
import gc

# Force garbage collection before memory tests
gc.collect()

# Use memory profiling for debugging
from memory_profiler import profile

@profile
def test_memory_usage(self):
    # Test code here
```

### Integration Test Issues

#### Issue: `NoReverseMatch` for URL patterns
**Cause**: URL patterns not properly configured or missing.

**Solutions**:
```python
# Check that URLs are included in main urlpatterns
# In config/urls.py
urlpatterns = [
    path('', include('marketplace.urls')),
]

# Verify URL name in test
from django.urls import reverse
url = reverse('product_detail', kwargs={'slug': 'test-product'})
```

#### Issue: CSRF token missing in forms
**Cause**: CSRF middleware enabled but token not included in test requests.

**Solutions**:
```python
# Use Django test client which handles CSRF automatically
response = self.client.post(url, data, follow=True)

# Or disable CSRF for specific tests
@override_settings(CSRF_COOKIE_SECURE=False)
def test_form_submission(self):
    pass

# Or get CSRF token explicitly
from django.middleware.csrf import get_token
csrf_token = get_token(request)
```

### Mock and Patch Issues

#### Issue: `AttributeError: module has no attribute`
**Cause**: Incorrect import path or timing in mock patches.

**Solutions**:
```python
# Mock where the function is used, not where it's defined
# Wrong:
@patch('marketplace.services.email_service.send_email')

# Right:
@patch('marketplace.views.checkout.send_email')

# Or use string paths
@patch('marketplace.services.email_service.EmailService.send_email')
```

#### Issue: Mocks not being called or wrong call count
**Cause**: Mock not properly configured or multiple code paths.

**Solutions**:
```python
# Verify mock configuration
mock_function.assert_called_once_with(expected_args)

# Debug mock calls
print(mock_function.call_args_list)
print(mock_function.call_count)

# Reset mocks between tests
def setUp(self):
    self.mock_function.reset_mock()
```

### Coverage Issues

#### Issue: Coverage lower than expected
**Cause**: Code paths not tested or tests not running all branches.

**Solutions**:
```bash
# Generate detailed coverage report
python -m pytest --cov=marketplace --cov-report=html

# View missed lines
python -m pytest --cov=marketplace --cov-report=term-missing

# Exclude specific files if needed
# In .coveragerc
[run]
omit = 
    */migrations/*
    */venv/*
    */tests/*
```

#### Issue: `CoverageException: No data to report`
**Cause**: Coverage plugin not finding test files or source code.

**Solutions**:
```bash
# Ensure coverage is measuring correct source
python -m pytest --cov=marketplace.models --cov=marketplace.views

# Check working directory
python -m pytest --cov=. marketplace/tests/
```

### Environment Issues

#### Issue: `ImproperlyConfigured: settings not configured`
**Cause**: Django settings not properly loaded for tests.

**Solutions**:
```bash
# Always specify Django settings
python -m pytest --ds=config.settings

# Or set environment variable
export DJANGO_SETTINGS_MODULE=config.settings
python -m pytest
```

#### Issue: Import errors in tests
**Cause**: Python path or Django app not properly configured.

**Solutions**:
```bash
# Ensure Django is configured before imports
python manage.py check

# Add to pythonpath if needed
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### Haiti-Specific Test Issues

#### Issue: Phone number validation failing
**Cause**: Faker generating non-Haitian phone numbers.

**Solutions**:
```python
# Create custom Haitian phone provider
from faker.providers import BaseProvider

class HaitianPhoneProvider(BaseProvider):
    def haitian_phone(self):
        return f"+509 {self.random_int(1000, 9999)}-{self.random_int(1000, 9999)}"

# Use in factory
phone = factory.LazyAttribute(lambda obj: fake.haitian_phone())
```

#### Issue: MonCash integration test failures
**Cause**: External API calls or improper mocking.

**Solutions**:
```python
# Always mock external services
@patch('marketplace.services.payment_service.moncash_api_call')
def test_moncash_payment(self, mock_api):
    mock_api.return_value = {'status': 'success', 'transaction_id': '123'}
    # Test code here
```

### CI/CD Issues

#### Issue: Tests pass locally but fail in CI
**Cause**: Different environment, timezone, or dependencies.

**Solutions**:
```yaml
# In GitHub Actions, ensure proper Python version and dependencies
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.10'

- name: Install dependencies
  run: |
    pip install -r requirements.txt
    pip install -r requirements/testing.txt
```

#### Issue: Database connection errors in CI
**Cause**: Database service not available or wrong configuration.

**Solutions**:
```yaml
# Add database service in CI
services:
  postgres:
    image: postgres:13
    env:
      POSTGRES_PASSWORD: postgres
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

## Debugging Strategies

### 1. Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In test
def test_something(self, caplog):
    with caplog.at_level(logging.DEBUG):
        # Test code
        pass
    assert "expected log message" in caplog.text
```

### 2. Use pdb for Interactive Debugging
```python
import pdb; pdb.set_trace()  # Add breakpoint in test
```

### 3. Inspect Database State
```python
def test_debug_database(self):
    # Print all objects to debug
    print("Users:", list(User.objects.all()))
    print("Products:", list(Product.objects.all()))
```

### 4. Test Individual Components
```bash
# Run specific test file
python -m pytest marketplace/tests/test_models.py -v

# Run specific test class
python -m pytest marketplace/tests/test_models.py::TestUserModel -v

# Run specific test method
python -m pytest marketplace/tests/test_models.py::TestUserModel::test_user_creation -v
```

### 5. Performance Profiling
```bash
# Install line_profiler
pip install line_profiler

# Profile specific function
kernprof -l -v test_function.py
```

## Best Practices for Avoiding Issues

1. **Always use factories for test data** - Ensures consistent, valid test data
2. **Mock external dependencies** - Prevents tests from failing due to external services
3. **Use transactions for test isolation** - Ensures tests don't interfere with each other
4. **Test both success and failure cases** - Improves code coverage and reliability
5. **Keep tests focused and atomic** - Makes debugging easier when tests fail
6. **Use descriptive test names** - Makes it clear what functionality is being tested
7. **Regular cleanup** - Remove unused test code and keep tests maintainable

## Getting Help

1. **Check Django test documentation**: https://docs.djangoproject.com/en/stable/topics/testing/
2. **pytest documentation**: https://docs.pytest.org/
3. **Factory Boy documentation**: https://factoryboy.readthedocs.io/
4. **Review test logs and error messages carefully** - They often contain the exact issue
5. **Use Django shell for manual testing**: `python manage.py shell`
6. **Check Django debug toolbar in development** - Helps identify slow queries and issues