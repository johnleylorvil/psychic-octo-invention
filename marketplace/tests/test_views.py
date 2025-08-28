# Unit tests for Afèpanou marketplace views
import pytest
import json
from decimal import Decimal
from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core import mail

from marketplace.models import Category, Product, Cart, CartItem, Order
from .factories import (
    UserFactory, SellerUserFactory, CategoryFactory, ProductFactory,
    CartFactory, CartItemFactory, OrderFactory, VendorProfileFactory
)

User = get_user_model()


@pytest.mark.django_db
class TestHomePageView:
    """Test suite for HomePage view"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
        
    def test_home_page_loads_successfully(self):
        """Test home page loads with correct status"""
        response = self.client.get(reverse('home'))
        assert response.status_code == 200
        assert 'pages/home.html' in [t.name for t in response.templates]
    
    def test_home_page_context_data(self):
        """Test home page context contains required data"""
        # Create test data
        CategoryFactory.create_batch(3, is_featured=True, is_active=True)
        ProductFactory.create_batch(5, is_featured=True, is_active=True)
        
        response = self.client.get(reverse('home'))
        
        assert 'featured_categories' in response.context
        assert 'featured_products' in response.context
        assert len(response.context['featured_categories']) == 3
        assert len(response.context['featured_products']) == 5
    
    def test_home_page_with_inactive_items(self):
        """Test home page excludes inactive categories and products"""
        # Create active and inactive items
        CategoryFactory.create_batch(2, is_featured=True, is_active=True)
        CategoryFactory.create_batch(2, is_featured=True, is_active=False)
        ProductFactory.create_batch(3, is_featured=True, is_active=True)
        ProductFactory.create_batch(2, is_featured=True, is_active=False)
        
        response = self.client.get(reverse('home'))
        
        # Should only show active items
        assert len(response.context['featured_categories']) == 2
        assert len(response.context['featured_products']) == 3


@pytest.mark.django_db 
class TestProductDetailView:
    """Test suite for ProductDetail view"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
        self.product = ProductFactory(is_active=True)
    
    def test_product_detail_loads_successfully(self):
        """Test product detail page loads"""
        url = reverse('product_detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        
        assert response.status_code == 200
        assert response.context['product'] == self.product
        assert 'pages/product_detail.html' in [t.name for t in response.templates]
    
    def test_product_detail_inactive_product(self):
        """Test accessing inactive product returns 404"""
        inactive_product = ProductFactory(is_active=False)
        url = reverse('product_detail', kwargs={'slug': inactive_product.slug})
        response = self.client.get(url)
        
        assert response.status_code == 404
    
    def test_product_detail_nonexistent_product(self):
        """Test accessing non-existent product returns 404"""
        url = reverse('product_detail', kwargs={'slug': 'nonexistent-product'})
        response = self.client.get(url)
        
        assert response.status_code == 404
    
    def test_product_detail_increments_view_count(self):
        """Test that viewing product increments view count"""
        initial_count = self.product.view_count
        url = reverse('product_detail', kwargs={'slug': self.product.slug})
        
        self.client.get(url)
        self.product.refresh_from_db()
        
        assert self.product.view_count == initial_count + 1


@pytest.mark.django_db
class TestCategoryListView:
    """Test suite for CategoryList view"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
        self.category = CategoryFactory(is_active=True)
        # Create products in this category
        ProductFactory.create_batch(8, category=self.category, is_active=True)
        ProductFactory.create_batch(2, category=self.category, is_active=False)
    
    def test_category_list_loads_successfully(self):
        """Test category list page loads"""
        url = reverse('category_list', kwargs={'slug': self.category.slug})
        response = self.client.get(url)
        
        assert response.status_code == 200
        assert response.context['category'] == self.category
        assert 'pages/category_list.html' in [t.name for t in response.templates]
    
    def test_category_list_shows_active_products_only(self):
        """Test category list shows only active products"""
        url = reverse('category_list', kwargs={'slug': self.category.slug})
        response = self.client.get(url)
        
        products = response.context['products']
        assert len(products) == 8  # Only active products
        
        for product in products:
            assert product.is_active
            assert product.category == self.category
    
    def test_category_list_pagination(self):
        """Test category list pagination works"""
        # Create many products to test pagination
        ProductFactory.create_batch(25, category=self.category, is_active=True)
        
        url = reverse('category_list', kwargs={'slug': self.category.slug})
        response = self.client.get(url)
        
        # Should be paginated (default 20 per page)
        assert response.context['is_paginated']
        assert len(response.context['products']) == 20
    
    def test_category_list_inactive_category(self):
        """Test accessing inactive category returns 404"""
        inactive_category = CategoryFactory(is_active=False)
        url = reverse('category_list', kwargs={'slug': inactive_category.slug})
        response = self.client.get(url)
        
        assert response.status_code == 404


@pytest.mark.django_db
class TestCartViews:
    """Test suite for cart-related views"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
        self.user = UserFactory()
        self.product = ProductFactory(stock_quantity=10, is_active=True)
    
    def test_add_to_cart_authenticated_user(self):
        """Test adding product to cart for authenticated user"""
        self.client.force_login(self.user)
        
        url = reverse('add_to_cart')
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        
        response = self.client.post(url, data)
        
        assert response.status_code == 302  # Redirect after successful add
        
        # Check cart was created and item added
        cart = Cart.objects.get(user=self.user)
        cart_item = cart.items.get(product=self.product)
        assert cart_item.quantity == 2
    
    def test_add_to_cart_anonymous_user(self):
        """Test adding product to cart for anonymous user"""
        url = reverse('add_to_cart')
        data = {
            'product_id': self.product.id,
            'quantity': 1
        }
        
        response = self.client.post(url, data)
        
        # Should create session-based cart
        session_id = self.client.session.session_key
        cart = Cart.objects.get(session_id=session_id)
        cart_item = cart.items.get(product=self.product)
        assert cart_item.quantity == 1
    
    def test_add_to_cart_insufficient_stock(self):
        """Test adding more items than available stock"""
        self.product.stock_quantity = 3
        self.product.save()
        
        self.client.force_login(self.user)
        
        url = reverse('add_to_cart')
        data = {
            'product_id': self.product.id,
            'quantity': 5  # More than available
        }
        
        response = self.client.post(url, data)
        
        # Should redirect with error message
        messages = list(get_messages(response.wsgi_request))
        assert any('stock' in str(msg).lower() for msg in messages)
    
    def test_cart_view_authenticated_user(self):
        """Test cart view for authenticated user"""
        self.client.force_login(self.user)
        cart = CartFactory(user=self.user)
        CartItemFactory.create_batch(2, cart=cart)
        
        response = self.client.get(reverse('cart'))
        
        assert response.status_code == 200
        assert response.context['cart'] == cart
        assert len(response.context['cart_items']) == 2
    
    def test_remove_from_cart(self):
        """Test removing item from cart"""
        self.client.force_login(self.user)
        cart = CartFactory(user=self.user)
        cart_item = CartItemFactory(cart=cart, product=self.product)
        
        url = reverse('remove_from_cart')
        data = {'cart_item_id': cart_item.id}
        
        response = self.client.post(url, data)
        
        assert response.status_code == 302
        assert not CartItem.objects.filter(id=cart_item.id).exists()


@pytest.mark.django_db
class TestAuthenticationViews:
    """Test suite for authentication views"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
    
    def test_registration_view_get(self):
        """Test registration form display"""
        response = self.client.get(reverse('register'))
        
        assert response.status_code == 200
        assert 'account/register.html' in [t.name for t in response.templates]
        assert 'form' in response.context
    
    def test_registration_view_post_valid_data(self):
        """Test user registration with valid data"""
        data = {
            'email': 'newuser@test.com',
            'first_name': 'Jean',
            'last_name': 'Pierre',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'phone': '+509 1234-5678'
        }
        
        response = self.client.post(reverse('register'), data)
        
        assert response.status_code == 302  # Redirect after successful registration
        assert User.objects.filter(email='newuser@test.com').exists()
    
    def test_registration_view_post_invalid_data(self):
        """Test user registration with invalid data"""
        data = {
            'email': 'invalid-email',
            'first_name': '',
            'password1': '123',  # Too simple
            'password2': '456'   # Doesn't match
        }
        
        response = self.client.post(reverse('register'), data)
        
        assert response.status_code == 200  # Stay on form
        assert response.context['form'].errors
        assert not User.objects.filter(email='invalid-email').exists()
    
    def test_login_view_get(self):
        """Test login form display"""
        response = self.client.get(reverse('login'))
        
        assert response.status_code == 200
        assert 'account/login.html' in [t.name for t in response.templates]
    
    def test_login_view_post_valid_credentials(self):
        """Test login with valid credentials"""
        user = UserFactory(email='test@example.com')
        user.set_password('testpass123')
        user.save()
        
        data = {
            'username': 'test@example.com',  # Using email as username
            'password': 'testpass123'
        }
        
        response = self.client.post(reverse('login'), data)
        
        assert response.status_code == 302  # Redirect after login
        assert '_auth_user_id' in self.client.session
    
    def test_login_view_post_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(reverse('login'), data)
        
        assert response.status_code == 200  # Stay on form
        assert '_auth_user_id' not in self.client.session
    
    def test_logout_view(self):
        """Test user logout"""
        user = UserFactory()
        self.client.force_login(user)
        
        response = self.client.post(reverse('logout'))
        
        assert response.status_code == 302  # Redirect after logout
        assert '_auth_user_id' not in self.client.session


@pytest.mark.django_db
class TestSellerViews:
    """Test suite for seller-related views"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
        self.seller = SellerUserFactory()
        self.vendor = VendorProfileFactory(user=self.seller)
    
    def test_become_seller_view_get_anonymous(self):
        """Test become seller form for anonymous user"""
        response = self.client.get(reverse('become_seller'))
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/login' in response.url
    
    def test_become_seller_view_get_authenticated(self):
        """Test become seller form for authenticated user"""
        user = UserFactory(is_seller=False)
        self.client.force_login(user)
        
        response = self.client.get(reverse('become_seller'))
        
        assert response.status_code == 200
        assert 'account/become_seller.html' in [t.name for t in response.templates]
    
    def test_become_seller_view_already_seller(self):
        """Test become seller view for existing seller"""
        self.client.force_login(self.seller)
        
        response = self.client.get(reverse('become_seller'))
        
        # Should redirect to seller dashboard
        assert response.status_code == 302
    
    def test_seller_dashboard_view_access_control(self):
        """Test seller dashboard access control"""
        # Test non-seller access
        regular_user = UserFactory(is_seller=False)
        self.client.force_login(regular_user)
        
        response = self.client.get(reverse('seller_dashboard'))
        assert response.status_code == 403  # Forbidden
        
        # Test seller access
        self.client.force_login(self.seller)
        response = self.client.get(reverse('seller_dashboard'))
        assert response.status_code == 200
    
    def test_seller_dashboard_context_data(self):
        """Test seller dashboard context contains required data"""
        self.client.force_login(self.seller)
        
        # Create test data for this seller
        ProductFactory.create_batch(5, seller=self.seller)
        OrderFactory.create_batch(3, user=self.seller)
        
        response = self.client.get(reverse('seller_dashboard'))
        
        assert 'total_products' in response.context
        assert 'total_orders' in response.context
        assert 'recent_orders' in response.context
        assert response.context['total_products'] == 5


@pytest.mark.django_db
class TestAjaxViews:
    """Test suite for AJAX views"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
        self.user = UserFactory()
        self.product = ProductFactory()
    
    def test_product_search_ajax(self):
        """Test AJAX product search"""
        # Create products with known names
        ProductFactory(name="iPhone 13", is_active=True)
        ProductFactory(name="iPad Pro", is_active=True)
        ProductFactory(name="MacBook Air", is_active=True)
        ProductFactory(name="Samsung Galaxy", is_active=False)  # Inactive
        
        url = reverse('ajax_product_search')
        response = self.client.get(url, {'q': 'i'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Should return products containing 'i' but only active ones
        product_names = [p['name'] for p in data['products']]
        assert 'iPhone 13' in product_names
        assert 'iPad Pro' in product_names
        assert 'Samsung Galaxy' not in product_names  # Inactive
    
    def test_add_to_cart_ajax(self):
        """Test AJAX add to cart"""
        self.client.force_login(self.user)
        
        url = reverse('ajax_add_to_cart')
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        
        response = self.client.post(
            url, data, 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.content)
        
        assert response_data['success']
        assert 'cart_count' in response_data
        assert 'message' in response_data
    
    def test_update_cart_quantity_ajax(self):
        """Test AJAX cart quantity update"""
        self.client.force_login(self.user)
        cart = CartFactory(user=self.user)
        cart_item = CartItemFactory(cart=cart, product=self.product, quantity=1)
        
        url = reverse('ajax_update_cart')
        data = {
            'cart_item_id': cart_item.id,
            'quantity': 3
        }
        
        response = self.client.post(
            url, data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        assert response.status_code == 200
        response_data = json.loads(response.content)
        
        assert response_data['success']
        
        cart_item.refresh_from_db()
        assert cart_item.quantity == 3
    
    def test_ajax_view_without_ajax_header(self):
        """Test AJAX view called without AJAX header"""
        url = reverse('ajax_product_search')
        response = self.client.get(url, {'q': 'test'})
        
        # Should return 400 Bad Request
        assert response.status_code == 400


@pytest.mark.django_db
class TestCheckoutViews:
    """Test suite for checkout views"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
        self.user = UserFactory()
        self.cart = CartFactory(user=self.user)
        self.cart_item = CartItemFactory(cart=self.cart)
    
    def test_checkout_view_access_control(self):
        """Test checkout requires authentication"""
        response = self.client.get(reverse('checkout'))
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/login' in response.url
    
    def test_checkout_view_empty_cart(self):
        """Test checkout with empty cart"""
        empty_cart = CartFactory(user=self.user)
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('checkout'))
        
        # Should redirect to cart page
        assert response.status_code == 302
        assert reverse('cart') in response.url
    
    def test_checkout_view_with_items(self):
        """Test checkout with items in cart"""
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('checkout'))
        
        assert response.status_code == 200
        assert 'checkout/checkout.html' in [t.name for t in response.templates]
        assert 'cart' in response.context
        assert 'form' in response.context
    
    @patch('marketplace.services.payment_service.PaymentService.create_payment')
    def test_checkout_post_valid_data(self, mock_create_payment):
        """Test checkout form submission with valid data"""
        mock_create_payment.return_value = {
            'success': True,
            'payment_url': 'https://payment.example.com/pay/123'
        }
        
        self.client.force_login(self.user)
        
        data = {
            'shipping_first_name': 'Jean',
            'shipping_last_name': 'Pierre',
            'shipping_address': '123 Rue Example',
            'shipping_city': 'Port-au-Prince',
            'shipping_country': 'Haïti',
            'phone': '+509 1234-5678',
            'payment_method': 'moncash'
        }
        
        response = self.client.post(reverse('checkout'), data)
        
        # Should redirect to payment
        assert response.status_code == 302
        assert Order.objects.filter(user=self.user).exists()
    
    def test_checkout_post_invalid_data(self):
        """Test checkout form submission with invalid data"""
        self.client.force_login(self.user)
        
        data = {
            'shipping_first_name': '',  # Required field missing
            'shipping_address': '',     # Required field missing
        }
        
        response = self.client.post(reverse('checkout'), data)
        
        assert response.status_code == 200  # Stay on form
        assert response.context['form'].errors
        assert not Order.objects.filter(user=self.user).exists()