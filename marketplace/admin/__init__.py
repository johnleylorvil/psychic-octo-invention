# marketplace/admin/__init__.py
"""
Enhanced admin interface for Afèpanou marketplace
"""

from .user_admin import UserAdmin
from .product_admin import CategoryAdmin, ProductAdmin, ProductImageAdmin
from .order_admin import CartAdmin, OrderAdmin, OrderItemInline
from .content_admin import BannerAdmin, PageAdmin, MediaContentSectionAdmin
from .review_admin import ReviewAdmin
from .payment_admin import TransactionAdmin
from .newsletter_admin import NewsletterSubscriberAdmin
from .settings_admin import SiteSettingAdmin

# Configure admin site
from django.contrib import admin

admin.site.site_header = "🏪 Administration Afèpanou Marketplace"
admin.site.site_title = "Afèpanou Admin"
admin.site.index_title = "Tableau de bord du Marketplace Haïtien"

__all__ = [
    'UserAdmin',
    'CategoryAdmin',
    'ProductAdmin', 
    'ProductImageAdmin',
    'CartAdmin',
    'OrderAdmin',
    'OrderItemInline',
    'BannerAdmin',
    'PageAdmin',
    'MediaContentSectionAdmin',
    'ReviewAdmin',
    'TransactionAdmin',
    'NewsletterSubscriberAdmin',
    'SiteSettingAdmin',
]