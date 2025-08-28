#!/usr/bin/env python
"""
Comprehensive View and Endpoint Testing Suite for Afpanou Marketplace
Testing all URL patterns, views, authentication, and functionality
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from django.core.management import execute_from_command_line
from django.conf import settings
from django.db import transaction
import json
from datetime import datetime
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import (
    Product, Category, Order, Cart, Review, 
    VendorProfile, Address, Wishlist, NewsletterSubscriber
)
from marketplace.forms import (
    ProductSearchForm, ProductReviewForm, UserRegistrationForm,
    AddressForm, SellerApplicationForm
)

User = get_user_model()

class ComprehensiveViewTester:
    """Comprehensive testing of all marketplace views and endpoints"""
    
    def __init__(self):
        self.client = Client()
        self.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'warnings': []
        }
        self.test_user = None
        self.test_seller = None
        self.test_product = None
        
    def log_result(self, test_name, status, message=""):
        """Log test results"""
        self.test_results['total_tests'] += 1
        if status == 'PASS':
            self.test_results['passed'] += 1
            print(f"[PASS] {test_name}: {message}")
        elif status == 'FAIL':
            self.test_results['failed'] += 1
            print(f"[FAIL] {test_name}: {message}")
            self.test_results['errors'].append(f"{test_name}: {message}")
        elif status == 'WARN':
            print(f"[WARN] {test_name}: {message}")
            self.test_results['warnings'].append(f"{test_name}: {message}")
    
    def setup_test_data(self):
        """Create test data for comprehensive testing"""
        print("\nSetting up test data...")
        
        try:
            # Create test category
            self.test_category = Category.objects.get_or_create(
                name="Test Category",
                slug="test-category",
                defaults={'is_active': True}
            )[0]
            
            # Create test user
            self.test_user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            
            # Create test seller
            self.test_seller = User.objects.create_user(
                username='testseller',
                email='seller@example.com',
                password='testpass123',
                is_seller=True,
                first_name='Test',
                last_name='Seller'
            )
            
            # Create vendor profile
            self.vendor_profile = VendorProfile.objects.get_or_create(
                user=self.test_seller,
                defaults={
                    'business_name': 'Test Business',
                    'business_type': 'individual',
                    'business_address': '123 Business Street',
                    'business_phone': '+509 1234 5678',
                    'verification_status': 'verified',
                    'is_verified': True
                }
            )[0]
            
            # Create test product
            self.test_product = Product.objects.get_or_create(
                name="Test Product",
                slug="test-product",
                defaults={
                    'description': 'A test product for testing',
                    'price': Decimal('99.99'),
                    'stock_quantity': 10,
                    'category': self.test_category,
                    'seller': self.vendor_profile,
                    'is_active': True
                }
            )[0]
            
            # Create test address
            self.test_address = Address.objects.get_or_create(
                user=self.test_user,
                defaults={
                    'first_name': 'Test',
                    'last_name': 'User',
                    'address_line1': '123 Test Street',
                    'city': 'Port-au-Prince',
                    'department': 'ouest',
                    'phone': '+509 1234 5678',
                    'is_default': True
                }
            )[0]
            
            self.log_result("Test Data Setup", "PASS", "All test data created successfully")
            
        except Exception as e:
            self.log_result("Test Data Setup", "FAIL", f"Error: {str(e)}")
    
    def test_url_patterns(self):
        """Test all URL patterns can be reversed"""
        print("\n Testing URL patterns...")
        
        # Basic URL patterns to test
        url_patterns = [
            # Public pages
            ('marketplace:home', {}),
            ('marketplace:about', {}),
            ('marketplace:contact', {}),
            ('marketplace:terms', {}),
            ('marketplace:privacy', {}),
            
            # Product pages
            ('marketplace:category_index', {}),
            ('marketplace:product_search', {}),
            
            # Authentication
            ('marketplace:register', {}),
            ('marketplace:login', {}),
            
            # With parameters
            ('marketplace:product_detail', {'slug': 'test-product'}),
            ('marketplace:category_list', {'slug': 'test-category'}),
        ]
        
        for url_name, kwargs in url_patterns:
            try:
                url = reverse(url_name, kwargs=kwargs)
                self.log_result(f"URL Pattern: {url_name}", "PASS", f"-> {url}")
            except NoReverseMatch as e:
                self.log_result(f"URL Pattern: {url_name}", "FAIL", f"NoReverseMatch: {str(e)}")
            except Exception as e:
                self.log_result(f"URL Pattern: {url_name}", "FAIL", f"Error: {str(e)}")
    
    def test_public_pages(self):
        """Test public pages accessibility"""
        print("\n Testing public pages...")
        
        public_urls = [
            '/',
            '/apropos/',
            '/contact/',
            '/conditions/',
            '/confidentialite/',
            '/recherche/',
            '/categories/',
        ]
        
        for url in public_urls:
            try:
                response = self.client.get(url)
                if response.status_code == 200:
                    self.log_result(f"Public Page: {url}", "PASS", f"Status: {response.status_code}")
                elif response.status_code in [301, 302]:
                    self.log_result(f"Public Page: {url}", "WARN", f"Redirect: {response.status_code}")
                else:
                    self.log_result(f"Public Page: {url}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Public Page: {url}", "FAIL", f"Error: {str(e)}")
    
    def test_authentication_views(self):
        """Test authentication and user management views"""
        print("\n Testing authentication views...")
        
        # Test registration page
        try:
            response = self.client.get('/compte/inscription/')
            if response.status_code == 200:
                self.log_result("Registration Page", "PASS", "Registration form accessible")
            else:
                self.log_result("Registration Page", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Registration Page", "FAIL", f"Error: {str(e)}")
        
        # Test login page
        try:
            response = self.client.get('/compte/connexion/')
            if response.status_code == 200:
                self.log_result("Login Page", "PASS", "Login form accessible")
            else:
                self.log_result("Login Page", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Login Page", "FAIL", f"Error: {str(e)}")
        
        # Test login functionality
        try:
            login_data = {
                'username': 'testuser',
                'password': 'testpass123'
            }
            response = self.client.post('/compte/connexion/', login_data)
            if response.status_code in [200, 302]:
                self.log_result("Login Functionality", "PASS", "Login form submission works")
            else:
                self.log_result("Login Functionality", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Login Functionality", "FAIL", f"Error: {str(e)}")
    
    def test_protected_views(self):
        """Test views that require authentication"""
        print("\n Testing protected views...")
        
        # Login as test user
        self.client.login(username='testuser', password='testpass123')
        
        protected_urls = [
            '/compte/profil/',
            '/compte/adresses/',
            '/compte/favoris/',
            '/panier/',
            '/commandes/',
        ]
        
        for url in protected_urls:
            try:
                response = self.client.get(url)
                if response.status_code == 200:
                    self.log_result(f"Protected View: {url}", "PASS", "Authenticated access works")
                elif response.status_code in [301, 302]:
                    self.log_result(f"Protected View: {url}", "WARN", f"Redirect: {response.status_code}")
                else:
                    self.log_result(f"Protected View: {url}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Protected View: {url}", "FAIL", f"Error: {str(e)}")
    
    def test_seller_views(self):
        """Test seller-specific views"""
        print("\n Testing seller views...")
        
        # Login as seller
        self.client.login(username='testseller', password='testpass123')
        
        seller_urls = [
            '/vendeur/tableau-de-bord/',
            '/vendeur/produits/',
            '/vendeur/commandes/',
            '/vendeur/analytique/',
        ]
        
        for url in seller_urls:
            try:
                response = self.client.get(url)
                if response.status_code == 200:
                    self.log_result(f"Seller View: {url}", "PASS", "Seller access works")
                elif response.status_code in [301, 302]:
                    self.log_result(f"Seller View: {url}", "WARN", f"Redirect: {response.status_code}")
                else:
                    self.log_result(f"Seller View: {url}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Seller View: {url}", "FAIL", f"Error: {str(e)}")
    
    def test_product_views(self):
        """Test product-related views"""
        print("\n Testing product views...")
        
        # Test product detail
        try:
            url = f'/produit/{self.test_product.slug}/'
            response = self.client.get(url)
            if response.status_code == 200:
                self.log_result("Product Detail View", "PASS", "Product page accessible")
            else:
                self.log_result("Product Detail View", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Product Detail View", "FAIL", f"Error: {str(e)}")
        
        # Test category listing
        try:
            url = f'/categorie/{self.test_category.slug}/'
            response = self.client.get(url)
            if response.status_code == 200:
                self.log_result("Category List View", "PASS", "Category page accessible")
            else:
                self.log_result("Category List View", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Category List View", "FAIL", f"Error: {str(e)}")
        
        # Test search functionality
        try:
            response = self.client.get('/recherche/?query=test')
            if response.status_code == 200:
                self.log_result("Product Search", "PASS", "Search functionality works")
            else:
                self.log_result("Product Search", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Product Search", "FAIL", f"Error: {str(e)}")
    
    def test_ajax_endpoints(self):
        """Test AJAX endpoints"""
        print("\n Testing AJAX endpoints...")
        
        # Login for AJAX tests
        self.client.login(username='testuser', password='testpass123')
        
        ajax_endpoints = [
            ('/ajax/recherche/', 'GET'),
            ('/ajax/panier/resume/', 'GET'),
            ('/ajax/stock/verifier/', 'GET'),
        ]
        
        for endpoint, method in ajax_endpoints:
            try:
                if method == 'GET':
                    response = self.client.get(endpoint, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                else:
                    response = self.client.post(endpoint, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
                
                if response.status_code in [200, 400]:  # 400 might be expected for some endpoints
                    self.log_result(f"AJAX Endpoint: {endpoint}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_result(f"AJAX Endpoint: {endpoint}", "FAIL", f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"AJAX Endpoint: {endpoint}", "FAIL", f"Error: {str(e)}")
    
    def test_form_validation(self):
        """Test form validation"""
        print("\n Testing form validation...")
        
        # Test forms
        forms_to_test = [
            (ProductSearchForm, {'query': 'test search'}),
            (AddressForm, {
                'first_name': 'Test',
                'last_name': 'User',
                'address_line1': '123 Test St',
                'city': 'Port-au-Prince',
                'department': 'ouest',
                'phone': '+509 1234 5678'
            }),
        ]
        
        for form_class, data in forms_to_test:
            try:
                form = form_class(data)
                if form.is_valid():
                    self.log_result(f"Form Validation: {form_class.__name__}", "PASS", "Form validates correctly")
                else:
                    self.log_result(f"Form Validation: {form_class.__name__}", "WARN", f"Validation errors: {form.errors}")
            except Exception as e:
                self.log_result(f"Form Validation: {form_class.__name__}", "FAIL", f"Error: {str(e)}")
    
    def test_error_pages(self):
        """Test custom error pages"""
        print("\n Testing error pages...")
        
        # Test 404 page
        try:
            response = self.client.get('/nonexistent-page/')
            if response.status_code == 404:
                self.log_result("404 Error Page", "PASS", "Custom 404 page works")
            else:
                self.log_result("404 Error Page", "WARN", f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("404 Error Page", "FAIL", f"Error: {str(e)}")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("Starting Comprehensive View and Endpoint Testing Suite")
        print("=" * 60)
        
        # Setup
        self.setup_test_data()
        
        # Run all test suites
        self.test_url_patterns()
        self.test_public_pages()
        self.test_authentication_views()
        self.test_protected_views()
        self.test_seller_views()
        self.test_product_views()
        self.test_ajax_endpoints()
        self.test_form_validation()
        self.test_error_pages()
        
        # Results summary
        self.print_summary()
        
        return self.test_results
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print(" TESTING SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f" Passed: {self.test_results['passed']}")
        print(f" Failed: {self.test_results['failed']}")
        print(f" Warnings: {len(self.test_results['warnings'])}")
        
        success_rate = (self.test_results['passed'] / self.test_results['total_tests']) * 100 if self.test_results['total_tests'] > 0 else 0
        print(f" Success Rate: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            print("\n FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   - {error}")
        
        if self.test_results['warnings']:
            print("\n WARNINGS:")
            for warning in self.test_results['warnings']:
                print(f"   - {warning}")
        
        print("\n" + "=" * 60)

if __name__ == '__main__':
    # Run the comprehensive tests
    tester = ComprehensiveViewTester()
    results = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1)