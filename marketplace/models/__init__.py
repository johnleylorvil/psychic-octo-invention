# marketplace/models/__init__.py
"""
Domain-organized models for Afèpanou marketplace
"""

from .user import User
from .product import Category, Product, ProductImage
from .order import Cart, CartItem, Order, OrderItem, OrderStatusHistory
from .payment import Transaction
from .review import Review
from .content import Banner, MediaContentSection, Page
from .newsletter import NewsletterSubscriber
from .settings import SiteSetting
from .vendor import VendorProfile
from .promotion import Promotion

__all__ = [
    # User Management
    'User',
    'VendorProfile',

    # Product Catalog
    'Category',
    'Product',
    'ProductImage',

    # E-commerce
    'Cart',
    'CartItem',
    'Order',
    'OrderItem',
    'OrderStatusHistory',

    # Payment
    'Transaction',

    # Social Features
    'Review',

    # Content Management
    'Banner',
    'MediaContentSection',
    'Page',

    # Newsletter
    'NewsletterSubscriber',

    # Site Configuration
    'SiteSetting',

    # Promotions
    'Promotion',
]
