# marketplace/models/managers.py
"""
Custom model managers for Afèpanou marketplace
"""

from django.db import models
from django.utils import timezone


class CategoryManager(models.Manager):
    """Custom manager for Category model"""
    
    def active(self):
        """Get all active categories"""
        return self.filter(is_active=True)
    
    def featured(self):
        """Get featured categories"""
        return self.active().filter(is_featured=True)
    
    def root_categories(self):
        """Get root categories (no parent)"""
        return self.active().filter(parent__isnull=True)
    
    def with_products(self):
        """Get categories that have active products"""
        return self.active().filter(
            products__is_active=True
        ).distinct()


class ProductManager(models.Manager):
    """Custom manager for Product model"""
    
    def active(self):
        """Get all active products"""
        return self.filter(is_active=True)
    
    def available(self):
        """Get products that are active and in stock"""
        return self.active().filter(
            models.Q(stock_quantity__gt=0) | 
            models.Q(is_digital=True)
        )
    
    def featured(self):
        """Get featured products that are available"""
        return self.available().filter(is_featured=True)
    
    def by_category(self, category):
        """Get available products by category"""
        return self.available().filter(category=category)
    
    def by_seller(self, seller):
        """Get products by seller"""
        return self.active().filter(seller=seller)
    
    def on_sale(self):
        """Get products with promotional pricing"""
        return self.available().filter(
            promotional_price__isnull=False,
            promotional_price__lt=models.F('price')
        )
    
    def low_stock(self):
        """Get products with low stock"""
        return self.active().filter(
            stock_quantity__lte=models.F('min_stock_alert'),
            stock_quantity__gt=0
        )
    
    def out_of_stock(self):
        """Get products that are out of stock"""
        return self.active().filter(
            stock_quantity=0,
            is_digital=False
        )
    
    def search(self, query):
        """Search products by name, description, or tags"""
        return self.available().filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(short_description__icontains=query) |
            models.Q(tags__icontains=query) |
            models.Q(brand__icontains=query)
        ).distinct()
    
    def price_range(self, min_price=None, max_price=None):
        """Filter products by price range"""
        queryset = self.available()
        if min_price is not None:
            queryset = queryset.filter(
                models.Q(promotional_price__gte=min_price) |
                (models.Q(promotional_price__isnull=True) & models.Q(price__gte=min_price))
            )
        if max_price is not None:
            queryset = queryset.filter(
                models.Q(promotional_price__lte=max_price) |
                (models.Q(promotional_price__isnull=True) & models.Q(price__lte=max_price))
            )
        return queryset


class CartManager(models.Manager):
    """Custom manager for Cart model"""
    
    def active(self):
        """Get active carts"""
        return self.filter(is_active=True)
    
    def for_user(self, user):
        """Get active cart for user"""
        return self.active().filter(user=user).first()
    
    def for_session(self, session_id):
        """Get active cart for session"""
        return self.active().filter(session_id=session_id).first()
    
    def expired(self):
        """Get expired carts"""
        return self.filter(
            expires_at__lt=timezone.now(),
            is_active=True
        )


class OrderManager(models.Manager):
    """Custom manager for Order model"""
    
    def for_user(self, user):
        """Get orders for user"""
        return self.filter(user=user).order_by('-created_at')
    
    def pending_payment(self):
        """Get orders pending payment"""
        return self.filter(payment_status='pending')
    
    def by_status(self, status):
        """Get orders by status"""
        return self.filter(status=status)
    
    def completed(self):
        """Get completed orders"""
        return self.filter(status='delivered', payment_status='paid')
    
    def recent(self, days=30):
        """Get recent orders within specified days"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)
    
    def by_date_range(self, start_date, end_date):
        """Get orders within date range"""
        return self.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )


class TransactionManager(models.Manager):
    """Custom manager for Transaction model"""
    
    def completed(self):
        """Get completed transactions"""
        return self.filter(status='completed')
    
    def pending(self):
        """Get pending transactions"""
        return self.filter(status='pending')
    
    def failed(self):
        """Get failed transactions"""
        return self.filter(status='failed')
    
    def by_payment_method(self, method):
        """Get transactions by payment method"""
        return self.filter(payment_method=method)
    
    def recent(self, hours=24):
        """Get recent transactions within specified hours"""
        cutoff_time = timezone.now() - timezone.timedelta(hours=hours)
        return self.filter(created_at__gte=cutoff_time)


class ReviewManager(models.Manager):
    """Custom manager for Review model"""
    
    def approved(self):
        """Get approved reviews"""
        return self.filter(is_approved=True)
    
    def pending(self):
        """Get pending reviews"""
        return self.filter(is_approved=False)
    
    def verified_purchases(self):
        """Get reviews from verified purchases"""
        return self.approved().filter(is_verified_purchase=True)
    
    def for_product(self, product):
        """Get approved reviews for a product"""
        return self.approved().filter(product=product)
    
    def by_rating(self, rating):
        """Get reviews by rating"""
        return self.approved().filter(rating=rating)
    
    def recent(self, days=7):
        """Get recent reviews"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return self.approved().filter(created_at__gte=cutoff_date)