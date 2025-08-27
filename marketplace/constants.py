# marketplace/constants.py
"""
Application constants for Afèpanou marketplace
"""

from django.utils.translation import gettext_lazy as _

# Order Status Choices
ORDER_STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('confirmed', _('Confirmed')),
    ('processing', _('Processing')),
    ('shipped', _('Shipped')),
    ('delivered', _('Delivered')),
    ('cancelled', _('Cancelled')),
    ('refunded', _('Refunded')),
]

# Payment Status Choices
PAYMENT_STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('paid', _('Paid')),
    ('failed', _('Failed')),
    ('refunded', _('Refunded')),
]

# Payment Method Choices
PAYMENT_METHOD_CHOICES = [
    ('moncash', _('MonCash')),
    ('cash_on_delivery', _('Cash on Delivery')),
    ('bank_transfer', _('Bank Transfer')),
]

# Transaction Status Choices
TRANSACTION_STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('processing', _('Processing')),
    ('completed', _('Completed')),
    ('failed', _('Failed')),
    ('cancelled', _('Cancelled')),
    ('refunded', _('Refunded')),
]

# Product Weight Units
WEIGHT_UNIT_CHOICES = [
    ('g', _('Grams')),
    ('kg', _('Kilograms')),
    ('lb', _('Pounds')),
    ('oz', _('Ounces')),
]

# Currency Choices
CURRENCY_CHOICES = [
    ('HTG', _('Haitian Gourde')),
    ('USD', _('US Dollar')),
]

# Country Choices (Haiti focus)
COUNTRY_CHOICES = [
    ('HT', _('Haiti')),
    ('US', _('United States')),
    ('CA', _('Canada')),
    ('FR', _('France')),
]

# Haiti Departments/States
HAITI_DEPARTMENTS = [
    ('artibonite', _('Artibonite')),
    ('centre', _('Centre')),
    ('grande_anse', _('Grande-Anse')),
    ('nippes', _('Nippes')),
    ('nord', _('Nord')),
    ('nord_est', _('Nord-Est')),
    ('nord_ouest', _('Nord-Ouest')),
    ('ouest', _('Ouest')),
    ('sud', _('Sud')),
    ('sud_est', _('Sud-Est')),
]

# Major Haitian Cities
HAITI_CITIES = [
    ('port-au-prince', _('Port-au-Prince')),
    ('cap-haitien', _('Cap-Haïtien')),
    ('carrefour', _('Carrefour')),
    ('delmas', _('Delmas')),
    ('petion-ville', _('Pétion-Ville')),
    ('gonaives', _('Gonaïves')),
    ('saint-marc', _('Saint-Marc')),
    ('jacmel', _('Jacmel')),
    ('les-cayes', _('Les Cayes')),
    ('hinche', _('Hinche')),
]

# Review Rating Choices
RATING_CHOICES = [
    (1, _('1 Star - Poor')),
    (2, _('2 Stars - Fair')),
    (3, _('3 Stars - Good')),
    (4, _('4 Stars - Very Good')),
    (5, _('5 Stars - Excellent')),
]

# Promotion Types
PROMOTION_TYPE_CHOICES = [
    ('percentage', _('Percentage Discount')),
    ('fixed_amount', _('Fixed Amount Discount')),
    ('buy_one_get_one', _('Buy One Get One')),
    ('free_shipping', _('Free Shipping')),
]

# Business Settings
DEFAULT_CURRENCY = 'HTG'
DEFAULT_COUNTRY = 'HT'
DEFAULT_LANGUAGE = 'fr'
DEFAULT_TIMEZONE = 'America/Port-au-Prince'

# Product Categories (Haitian Market Specific)
HAITIAN_PRODUCT_CATEGORIES = [
    'agriculture', # Pwodwi Agrikèl
    'food_beverages', # Manje ak Bweson
    'handicrafts', # Zèv Men
    'clothing', # Rad
    'electronics', # Elektwonik
    'home_garden', # Kay ak Jaden
    'beauty_health', # Bote ak Sante
    'books_education', # Liv ak Edikasyon
    'music_art', # Mizik ak A
    'services', # Sèvis
]

# File Upload Settings
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG', 'WEBP']
IMAGE_UPLOAD_PATH = 'products/'

# Cache Keys
CACHE_KEYS = {
    'featured_products': 'featured_products',
    'categories': 'active_categories',
    'banners': 'active_banners',
    'site_settings': 'site_settings',
    'product_count': 'product_count_{category_id}',
    'cart_count': 'cart_count_{user_id}',
}

# Cache Timeouts (in seconds)
CACHE_TIMEOUTS = {
    'short': 300,     # 5 minutes
    'medium': 1800,   # 30 minutes
    'long': 3600,     # 1 hour
    'daily': 86400,   # 24 hours
}

# Email Templates
EMAIL_TEMPLATES = {
    'welcome': 'emails/welcome.html',
    'order_confirmation': 'emails/order_confirmation.html',
    'order_status_update': 'emails/order_status_update.html',
    'payment_confirmation': 'emails/payment_confirmation.html',
    'password_reset': 'emails/password_reset.html',
    'low_stock_alert': 'emails/low_stock_alert.html',
    'newsletter': 'emails/newsletter.html',
}

# Pagination Settings
PAGINATION_SETTINGS = {
    'products_per_page': 20,
    'orders_per_page': 15,
    'reviews_per_page': 10,
    'admin_list_per_page': 25,
}

# Search Settings
SEARCH_SETTINGS = {
    'min_query_length': 2,
    'max_results': 100,
    'boost_featured': True,
}

# Stock Management
STOCK_SETTINGS = {
    'low_stock_threshold': 5,
    'out_of_stock_threshold': 0,
    'enable_backorder': False,
}

# MonCash Settings
MONCASH_SETTINGS = {
    'sandbox_url': 'https://sandbox.digicelgroup.com',
    'production_url': 'https://moncashbutton.digicelgroup.com',
    'timeout': 30,  # seconds
    'retry_attempts': 3,
}