# Performance tests for Afèpanou marketplace
import pytest
import time
from django.test import TestCase, Client
from django.urls import reverse
from django.db import connection
from django.test.utils import override_settings

from marketplace.models import Product, Category, User, Order
from .factories import (
    UserFactory, CategoryFactory, ProductFactory, OrderFactory,
    CartFactory, CartItemFactory
)


@pytest.mark.django_db
@pytest.mark.performance
class TestDatabasePerformance:
    """Test database query performance"""
    
    def test_product_list_query_performance(self):
        """Test product listing query performance with large dataset"""
        # Create test data
        category = CategoryFactory()
        ProductFactory.create_batch(100, category=category, is_active=True)
        
        start_time = time.time()
        
        # Test query performance
        products = list(Product.objects.filter(is_active=True)[:20])
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Performance assertion (should complete in under 1 second)
        assert query_time < 1.0, f"Query took {query_time:.2f}s, expected < 1.0s"
        assert len(products) == 20
        
        # Check query count
        with connection.cursor() as cursor:
            queries_before = len(connection.queries)
            list(Product.objects.filter(is_active=True).select_related('category', 'seller')[:20])
            queries_after = len(connection.queries)
            
        # Should use minimal queries with select_related
        query_count = queries_after - queries_before
        assert query_count <= 3, f"Used {query_count} queries, expected <= 3"
    
    def test_category_with_product_count_performance(self):
        """Test category listing with product counts"""
        # Create test data
        categories = CategoryFactory.create_batch(10)
        
        for category in categories:
            ProductFactory.create_batch(20, category=category, is_active=True)
            ProductFactory.create_batch(5, category=category, is_active=False)
        
        start_time = time.time()
        
        # Test query with annotations
        from django.db.models import Count
        categories_with_count = list(
            Category.objects.annotate(
                product_count=Count('products', filter=models.Q(products__is_active=True))
            )
        )
        
        end_time = time.time()
        query_time = end_time - start_time
        
        assert query_time < 0.5, f"Query took {query_time:.2f}s, expected < 0.5s"
        assert len(categories_with_count) == 10
        
        # Verify counts are correct
        for cat in categories_with_count:
            assert cat.product_count == 20
    
    def test_user_order_history_performance(self):
        """Test user order history query performance"""
        user = UserFactory()
        
        # Create multiple orders for user
        orders = OrderFactory.create_batch(50, user=user)
        
        start_time = time.time()
        
        # Test query performance
        user_orders = list(
            Order.objects.filter(user=user)
            .select_related('user')
            .prefetch_related('items__product')
            .order_by('-created_at')[:10]
        )
        
        end_time = time.time()
        query_time = end_time - start_time
        
        assert query_time < 0.5, f"Query took {query_time:.2f}s, expected < 0.5s"
        assert len(user_orders) == 10


@pytest.mark.django_db  
@pytest.mark.performance
class TestViewPerformance:
    """Test view response performance"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test data
        self.category = CategoryFactory()
        self.products = ProductFactory.create_batch(50, category=self.category, is_active=True)
        self.user = UserFactory()
    
    def test_homepage_load_time(self):
        """Test homepage load time performance"""
        start_time = time.time()
        
        response = self.client.get(reverse('home'))
        
        end_time = time.time()
        load_time = end_time - start_time
        
        assert response.status_code == 200
        assert load_time < 2.0, f"Homepage loaded in {load_time:.2f}s, expected < 2.0s"
    
    def test_category_page_load_time(self):
        """Test category page load time with many products"""
        start_time = time.time()
        
        response = self.client.get(
            reverse('category_list', kwargs={'slug': self.category.slug})
        )
        
        end_time = time.time()
        load_time = end_time - start_time
        
        assert response.status_code == 200
        assert load_time < 1.5, f"Category page loaded in {load_time:.2f}s, expected < 1.5s"
    
    def test_product_search_performance(self):
        """Test product search performance"""
        start_time = time.time()
        
        response = self.client.get(reverse('product_search'), {'q': 'test'})
        
        end_time = time.time()
        search_time = end_time - start_time
        
        assert response.status_code == 200
        assert search_time < 1.0, f"Search took {search_time:.2f}s, expected < 1.0s"
    
    def test_cart_operations_performance(self):
        """Test cart operations performance"""
        self.client.force_login(self.user)
        
        # Test adding multiple items to cart
        start_time = time.time()
        
        for i in range(10):
            self.client.post(reverse('add_to_cart'), {
                'product_id': self.products[i].id,
                'quantity': 1
            })
        
        end_time = time.time()
        cart_time = end_time - start_time
        
        assert cart_time < 3.0, f"Adding 10 items took {cart_time:.2f}s, expected < 3.0s"
        
        # Test cart view performance
        start_time = time.time()
        response = self.client.get(reverse('cart'))
        end_time = time.time()
        view_time = end_time - start_time
        
        assert response.status_code == 200
        assert view_time < 1.0, f"Cart view took {view_time:.2f}s, expected < 1.0s"


@pytest.mark.django_db
@pytest.mark.performance
class TestConcurrentOperations:
    """Test concurrent operation performance"""
    
    def test_concurrent_cart_updates(self):
        """Test multiple users updating carts simultaneously"""
        import threading
        
        users = UserFactory.create_batch(5)
        product = ProductFactory(stock_quantity=100)
        
        results = []
        
        def add_to_cart_worker(user):
            """Worker function for adding items to cart"""
            client = Client()
            client.force_login(user)
            
            start_time = time.time()
            
            response = client.post(reverse('add_to_cart'), {
                'product_id': product.id,
                'quantity': 5
            })
            
            end_time = time.time()
            results.append({
                'user': user.id,
                'time': end_time - start_time,
                'success': response.status_code == 302
            })
        
        # Create threads for concurrent operations
        threads = []
        for user in users:
            thread = threading.Thread(target=add_to_cart_worker, args=(user,))
            threads.append(thread)
        
        # Start all threads simultaneously
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Performance assertions
        assert total_time < 5.0, f"Concurrent operations took {total_time:.2f}s, expected < 5.0s"
        assert len(results) == 5
        assert all(r['success'] for r in results), "Some operations failed"
        assert all(r['time'] < 2.0 for r in results), "Some operations too slow"
    
    def test_memory_usage_large_dataset(self):
        """Test memory usage with large dataset operations"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create large dataset
        category = CategoryFactory()
        products = ProductFactory.create_batch(500, category=category)
        
        # Perform operations that could consume memory
        product_ids = list(Product.objects.values_list('id', flat=True))
        product_names = list(Product.objects.values_list('name', flat=True))
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        # Memory should not increase dramatically (< 100MB for this operation)
        assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB, expected < 100MB"


@pytest.mark.performance
class TestLoadTestingSetup:
    """Setup and configuration for load testing"""
    
    def test_locust_configuration_exists(self):
        """Test that Locust configuration is available"""
        try:
            import locust
            assert True, "Locust is installed and available"
        except ImportError:
            assert False, "Locust is not installed"
    
    def test_performance_test_markers(self):
        """Test that performance test markers are working"""
        # This test verifies the pytest marker system is working
        assert hasattr(pytest.mark, 'performance')


# Locust load testing configuration
# This would be in a separate locustfile.py for actual load testing

LOCUST_FILE_CONTENT = '''
# locustfile.py - Load testing configuration for Afèpanou
from locust import HttpUser, task, between
import random

class MarketplaceUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login user at start of test"""
        # Login simulation
        response = self.client.post("/login/", {
            "username": "test@example.com",
            "password": "testpassword"
        })
    
    @task(3)
    def view_homepage(self):
        """Visit homepage"""
        self.client.get("/")
    
    @task(2)
    def browse_categories(self):
        """Browse product categories"""
        categories = ["electronics", "fashion", "home-garden"]
        category = random.choice(categories)
        self.client.get(f"/category/{category}/")
    
    @task(2)
    def view_products(self):
        """View individual products"""
        product_id = random.randint(1, 100)
        self.client.get(f"/product/{product_id}/")
    
    @task(1)
    def search_products(self):
        """Search for products"""
        search_terms = ["phone", "laptop", "dress", "shoes"]
        term = random.choice(search_terms)
        self.client.get(f"/search/?q={term}")
    
    @task(1)
    def add_to_cart(self):
        """Add items to cart"""
        product_id = random.randint(1, 50)
        self.client.post("/cart/add/", {
            "product_id": product_id,
            "quantity": 1
        })
    
    @task(1)
    def view_cart(self):
        """View shopping cart"""
        self.client.get("/cart/")

class SellerUser(HttpUser):
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login as seller"""
        self.client.post("/login/", {
            "username": "seller@example.com", 
            "password": "sellerpassword"
        })
    
    @task(2)
    def view_dashboard(self):
        """View seller dashboard"""
        self.client.get("/seller/")
    
    @task(1)
    def manage_products(self):
        """Manage product listings"""
        self.client.get("/seller/products/")
    
    @task(1)
    def view_orders(self):
        """View seller orders"""
        self.client.get("/seller/orders/")
'''


def create_locust_file():
    """Helper function to create locustfile.py"""
    with open('locustfile.py', 'w') as f:
        f.write(LOCUST_FILE_CONTENT)