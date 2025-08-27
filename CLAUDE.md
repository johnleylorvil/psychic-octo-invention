# Afèpanou - Haitian E-Commerce Marketplace

## Project Overview

**Afèpanou** is a comprehensive e-commerce marketplace platform specifically designed for Haiti, enabling local vendors to sell their products online through a modern, secure, and culturally-appropriate digital ecosystem. The platform integrates MonCash as the primary payment processor and focuses on supporting the Haitian economy by connecting local sellers with consumers.

### Mission Statement
Create a digital ecosystem that supports Haitian economic growth by connecting local vendors to consumers through a modern, secure, and culturally-appropriate e-commerce platform.

### Key Value Propositions
- **For Buyers**: Discover and purchase authentic Haitian products and services
- **For Sellers**: Modern platform to grow their business and reach broader markets
- **For Community**: Contribute to collective economic development of Haiti

### Core Features
- Multi-vendor marketplace with vendor onboarding
- MonCash payment integration (Digicel)
- Haitian localization (French language, HTG currency, local addressing)
- Product catalog with categories specific to Haitian market
- Order management and tracking system
- Review and rating system
- Mobile-responsive design optimized for Haitian internet infrastructure

---

## Technical Requirements

### System Architecture
- **Backend Framework**: Django 4.x + Django REST Framework
- **Database**: PostgreSQL (hosted on Railway)
- **Cache & Message Broker**: Redis (sessions, cache, Celery tasks)
- **Media Storage**: Backblaze B2 (S3-compatible)
- **Payment Processing**: MonCash API (Digicel Haiti)
- **Async Task Processing**: Celery + Redis
- **Deployment Platform**: Railway.app
- **Frontend**: Django Templates + Modern CSS/JavaScript

### Core Dependencies
```python
# Backend Core
Django==4.2.x
djangorestframework==3.14.x
celery==5.3.x
redis==4.6.x
psycopg2-binary==2.9.x

# Storage & Media
boto3==1.28.x  # For Backblaze B2
django-storages==1.13.x

# Authentication & Security  
djangorestframework-simplejwt==5.2.x
django-cors-headers==4.2.x

# Monitoring & Logging
sentry-sdk==1.30.x

# Development
python-dotenv==1.0.x
django-debug-toolbar==4.1.x
```

### Infrastructure Requirements
- **Database**: PostgreSQL 14+ with minimum 1GB RAM
- **Redis**: Redis 6.x for caching and Celery broker
- **Storage**: Backblaze B2 bucket for media files
- **Monitoring**: Sentry for error tracking
- **SSL**: HTTPS certificate for production

### Localization Specifications
- **Primary Language**: French (fr-ht)
- **Currency**: HTG (Haitian Gourde)
- **Timezone**: America/Port-au-Prince
- **Default Location**: Port-au-Prince, Haiti
- **Payment Method**: MonCash integration

---

## Design System & UI Guidelines

### Brand Identity
- **Primary Color**: Orange (#E67E22) - representing warmth, energy, and growth
- **Secondary Colors**: Dark Orange (#D35400), Light Orange (#F39C12)
- **Neutral Colors**: White (#FFFFFF), Light Gray (#F8F9FA), Dark Gray (#343A40)
- **Typography**: Inter font family (web-safe fallbacks: system fonts)

### Color Palette
```css
:root {
  /* Brand Colors */
  --primary-orange: #E67E22;
  --primary-orange-dark: #D35400;
  --primary-orange-light: #F39C12;
  
  /* Neutral Colors */
  --white: #FFFFFF;
  --light-gray: #F8F9FA;
  --medium-gray: #6C757D;
  --dark-gray: #343A40;
  --black: #000000;
  
  /* Functional Colors */
  --success: #27AE60;
  --warning: #F39C12;
  --error: #E74C3C;
  --info: #3498DB;
  
  /* Gradients */
  --gradient-hero: linear-gradient(135deg, #E67E22 0%, #D35400 50%, #A0522D 100%);
  --gradient-card: linear-gradient(135deg, rgba(230, 126, 34, 0.1) 0%, rgba(211, 84, 0, 0.05) 100%);
}
```

### Typography Scale
```css
/* Typography System */
.text-h1 { font-size: 48px; font-weight: 700; line-height: 1.2; }
.text-h2 { font-size: 36px; font-weight: 600; line-height: 1.3; }
.text-h3 { font-size: 24px; font-weight: 600; line-height: 1.4; }
.text-h4 { font-size: 20px; font-weight: 600; line-height: 1.4; }
.text-body { font-size: 16px; font-weight: 400; line-height: 1.6; }
.text-small { font-size: 14px; font-weight: 400; line-height: 1.5; }
.text-caption { font-size: 12px; font-weight: 400; line-height: 1.4; }
```

### Component Guidelines
- **Border Radius**: 8px (buttons), 12px (cards), 20px (pills)
- **Shadows**: Subtle shadows using primary orange with low opacity
- **Spacing**: 8px base unit system (8, 16, 24, 32, 48, 64px)
- **Breakpoints**: Mobile-first responsive design (320px, 768px, 1024px, 1440px)

### UI Components
```css
/* Button Styles */
.btn-primary {
  background: var(--primary-orange);
  color: white;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(230, 126, 34, 0.3);
}

.btn-secondary {
  background: transparent;
  color: var(--primary-orange);
  border: 2px solid var(--primary-orange);
  border-radius: 8px;
  padding: 10px 22px;
  font-weight: 600;
}

/* Card Components */
.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(230, 126, 34, 0.1);
  padding: 24px;
  border: 1px solid rgba(230, 126, 34, 0.1);
}
```

---

## Application Structure & Architecture

### Django Project Structure
```
rbackend/
├── config/                     # Django project settings
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py            # Base settings
│   │   ├── development.py     # Dev settings
│   │   ├── production.py      # Prod settings
│   │   └── testing.py         # Test settings
│   ├── celery.py              # Celery configuration
│   ├── urls.py                # Root URL configuration
│   ├── wsgi.py                # WSGI application
│   └── asgi.py                # ASGI application (future WebSocket support)
│
├── marketplace/               # Core marketplace application
│   ├── models/                # Data models (organized by domain)
│   │   ├── __init__.py
│   │   ├── user.py           # User and seller models
│   │   ├── product.py        # Product, Category models
│   │   ├── order.py          # Order, Payment models
│   │   └── content.py        # CMS, Banner models
│   ├── views/                 # View controllers
│   │   ├── __init__.py
│   │   ├── api/              # REST API views
│   │   ├── pages.py          # Template-based views
│   │   └── ajax.py           # AJAX endpoints
│   ├── serializers/           # DRF serializers
│   ├── forms/                 # Django forms
│   ├── services/              # Business logic services
│   ├── tasks/                 # Celery tasks
│   ├── admin.py              # Django admin configuration
│   ├── apps.py               # App configuration
│   └── urls.py               # App URL patterns
│
├── templates/                 # HTML templates
│   ├── base/
│   │   ├── base.html         # Base template
│   │   ├── header.html       # Global header
│   │   └── footer.html       # Global footer
│   ├── pages/
│   │   ├── home.html         # Homepage
│   │   ├── category.html     # Category listing
│   │   ├── product.html      # Product details
│   │   ├── cart.html         # Shopping cart
│   │   └── checkout.html     # Checkout process
│   ├── account/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   └── seller/
│       ├── dashboard.html
│       └── products.html
│
├── static/                    # Static files
│   ├── css/
│   │   ├── main.css          # Main stylesheet
│   │   └── components/       # Component-specific styles
│   ├── js/
│   │   ├── main.js           # Main JavaScript
│   │   ├── components/       # JavaScript components
│   │   └── vendor/           # Third-party libraries
│   ├── images/
│   └── fonts/
│
├── media/                     # Local media files (development)
├── logs/                      # Application logs
├── requirements/              # Requirements files
│   ├── base.txt              # Base requirements
│   ├── development.txt       # Development requirements
│   └── production.txt        # Production requirements
└── manage.py                 # Django management script
```

### Database Schema Design

#### Core Models Overview
```python
# User Management
- User (extends AbstractUser): Enhanced user model for Haiti
- UserProfile: Extended user information and preferences
- SellerProfile: Seller-specific information and settings

# Product Catalog
- Category: Hierarchical product categories
- Product: Product information with specifications
- ProductImage: Product image gallery
- ProductVariant: Product variations (size, color, etc.)

# E-commerce
- Cart: Shopping cart management
- CartItem: Individual cart items
- Order: Order management
- OrderItem: Order line items
- Transaction: Payment transactions with MonCash

# Content Management
- Banner: Homepage carousel banners
- MediaContentSection: CMS content sections
- Page: Static pages (About, Terms, etc.)

# Social Features
- Review: Product reviews and ratings
- Wishlist: User wishlist functionality
```

### API Design Principles

#### RESTful API Structure
```
/api/v1/
├── auth/                      # Authentication endpoints
│   ├── login/
│   ├── register/
│   ├── logout/
│   └── refresh/
├── products/                  # Product management
│   ├── /                     # List/create products
│   ├── /{id}/                # Product details
│   ├── categories/           # Categories
│   └── search/               # Product search
├── cart/                      # Shopping cart
│   ├── /                     # Cart contents
│   ├── add/                  # Add to cart
│   └── remove/               # Remove from cart
├── orders/                    # Order management
│   ├── /                     # List orders
│   ├── create/               # Create order
│   └── /{id}/                # Order details
├── payments/                  # Payment processing
│   ├── moncash/              # MonCash integration
│   └── webhook/              # Payment webhooks
└── users/                     # User management
    ├── profile/              # User profile
    └── seller/               # Seller management
```

---

## Implementation Guidelines

### Development Workflow

#### 1. Environment Setup
```bash
# Clone repository
git clone <repository-url>
cd afèpanou

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/development.txt

# Environment variables
cp .env.example .env
# Edit .env with your configuration

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

#### 2. Code Quality Standards
- **PEP 8**: Python code style compliance
- **Type Hints**: Use Python type hints for all functions
- **Docstrings**: Document all classes and functions
- **Testing**: Minimum 80% test coverage
- **Linting**: Black formatter + Flake8 linter
- **Security**: Django security best practices

#### 3. Git Workflow
- **Branches**: feature/task-name, bugfix/issue-name, hotfix/critical-fix
- **Commits**: Conventional commit messages
- **Pull Requests**: Required for all changes to main branch
- **Code Review**: At least one reviewer required

### MonCash Integration Guidelines

#### Authentication Flow
```python
# MonCash OAuth2 Authentication
def get_moncash_access_token():
    """Authenticate with MonCash API and get access token"""
    url = f"{MONCASH_BASE_URL}/Api/oauth/token"
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'client_credentials',
        'client_id': settings.MONCASH_CLIENT_ID,
        'client_secret': settings.MONCASH_CLIENT_SECRET,
        'scope': 'read,write'
    }
    
    response = requests.post(url, headers=headers, data=data)
    return response.json().get('access_token')
```

#### Payment Processing
```python
# Payment Creation and Verification
class PaymentService:
    def create_payment(self, order, amount):
        """Create MonCash payment for order"""
        # Implementation details
        pass
    
    def verify_payment(self, transaction_id):
        """Verify payment status with MonCash"""
        # Implementation details
        pass
    
    def handle_webhook(self, webhook_data):
        """Process MonCash webhook notifications"""
        # Implementation details
        pass
```

### Security Implementation

#### Security Checklist
- [ ] HTTPS enforcement in production
- [ ] CSRF protection enabled
- [ ] SQL injection prevention (Django ORM)
- [ ] XSS protection (template escaping)
- [ ] Secure password storage (Django's built-in)
- [ ] Rate limiting on API endpoints
- [ ] Input validation and sanitization
- [ ] Secure file upload handling
- [ ] Environment variable protection
- [ ] Database connection security

#### Authentication & Authorization
```python
# Custom permissions for marketplace
class IsSellerPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_seller

class IsProductOwnerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.seller == request.user
```

### Performance Optimization

#### Database Optimization
- **Indexing**: Proper database indexes on frequently queried fields
- **Query Optimization**: Use select_related() and prefetch_related()
- **Connection Pooling**: Database connection pooling in production
- **Caching**: Redis caching for frequently accessed data

#### Frontend Performance
- **Image Optimization**: WebP format with fallbacks
- **Code Splitting**: Separate JavaScript bundles for different pages
- **CSS Optimization**: Minification and critical CSS inlining
- **CDN**: Static file delivery through CDN

#### Monitoring & Logging
```python
# Structured logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

---

## Testing Strategy

### Testing Pyramid
1. **Unit Tests**: Individual component testing (70%)
2. **Integration Tests**: API endpoint testing (20%)
3. **End-to-End Tests**: User journey testing (10%)

### Testing Framework Setup
```python
# Test configuration
# requirements/testing.txt
pytest==7.4.x
pytest-django==4.5.x
pytest-cov==4.0.x
factory-boy==3.3.x
fake2db==0.1.x

# Test database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_afepanou',
        'USER': 'test_user',
        'PASSWORD': 'test_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Sample Test Cases
```python
# Product model tests
class ProductModelTest(TestCase):
    def test_product_creation(self):
        """Test product can be created with required fields"""
        
    def test_product_price_calculation(self):
        """Test promotional price calculation"""
        
    def test_product_slug_generation(self):
        """Test automatic slug generation from name"""

# API endpoint tests  
class ProductAPITest(APITestCase):
    def test_product_list_endpoint(self):
        """Test product listing API endpoint"""
        
    def test_product_search_functionality(self):
        """Test product search API"""
        
    def test_unauthorized_product_creation(self):
        """Test product creation requires authentication"""
```

---

## Deployment & DevOps

### Production Deployment Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] SSL certificate installed
- [ ] Monitoring systems active
- [ ] Backup procedures tested
- [ ] Performance benchmarks established

### Environment Configuration
```python
# Production settings
DEBUG = False
ALLOWED_HOSTS = ['afepanou.com', 'www.afepanou.com']

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database configuration for Railway
DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}
```

This documentation serves as the comprehensive guide for developing, maintaining, and scaling the Afèpanou marketplace platform. Regular updates should be made as the project evolves and new features are implemented.