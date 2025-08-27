# marketplace/validators.py
"""
Custom field validators for Afèpanou marketplace
"""

import re
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from PIL import Image


def validate_haitian_phone_number(value):
    """Validate Haitian phone number format"""
    # Haiti phone numbers: +509 XXXX XXXX or 509 XXXX XXXX or XXXX XXXX
    patterns = [
        r'^\+509\s?\d{4}\s?\d{4}$',  # +509 XXXX XXXX
        r'^509\s?\d{4}\s?\d{4}$',    # 509 XXXX XXXX
        r'^\d{4}\s?\d{4}$',          # XXXX XXXX (local)
    ]
    
    if not any(re.match(pattern, value.replace(' ', '').replace('-', '')) for pattern in patterns):
        raise ValidationError(
            _('Enter a valid Haitian phone number (e.g., +509 1234 5678 or 1234 5678).')
        )


def validate_postal_code_haiti(value):
    """Validate Haitian postal code format"""
    # Haiti postal codes: HT followed by 4 digits
    pattern = r'^HT\d{4}$'
    
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            _('Enter a valid Haitian postal code (e.g., HT6110).')
        )


def validate_price(value):
    """Validate price is positive and has at most 2 decimal places"""
    if value <= 0:
        raise ValidationError(_('Price must be greater than zero.'))
    
    # Check decimal places
    decimal_value = Decimal(str(value))
    if decimal_value.as_tuple().exponent < -2:
        raise ValidationError(_('Price cannot have more than 2 decimal places.'))


def validate_discount_percentage(value):
    """Validate discount percentage is between 0 and 100"""
    if not (0 <= value <= 100):
        raise ValidationError(_('Discount percentage must be between 0 and 100.'))


def validate_stock_quantity(value):
    """Validate stock quantity is non-negative"""
    if value < 0:
        raise ValidationError(_('Stock quantity cannot be negative.'))


def validate_product_image(image):
    """Validate product image file"""
    # Check file size (5MB max)
    max_size = 5 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError(_('Image file size cannot exceed 5MB.'))
    
    try:
        # Check if it's a valid image
        img = Image.open(image)
        img.verify()
        
        # Check format
        allowed_formats = ['JPEG', 'PNG', 'WEBP']
        if img.format not in allowed_formats:
            raise ValidationError(
                _('Only JPEG, PNG, and WEBP images are allowed.')
            )
        
        # Check dimensions (optional - can be adjusted)
        max_width = 2000
        max_height = 2000
        if img.width > max_width or img.height > max_height:
            raise ValidationError(
                _('Image dimensions cannot exceed %(width)dx%(height)d pixels.') % {
                    'width': max_width,
                    'height': max_height
                }
            )
            
    except Exception:
        raise ValidationError(_('Invalid image file.'))


def validate_sku(value):
    """Validate SKU format"""
    # SKU should be alphanumeric with hyphens/underscores allowed
    pattern = r'^[A-Za-z0-9_-]+$'
    
    if not re.match(pattern, value):
        raise ValidationError(
            _('SKU can only contain letters, numbers, hyphens, and underscores.')
        )
    
    if len(value) > 50:
        raise ValidationError(_('SKU cannot exceed 50 characters.'))


def validate_slug(value):
    """Validate URL slug format"""
    pattern = r'^[a-z0-9-]+$'
    
    if not re.match(pattern, value):
        raise ValidationError(
            _('Slug can only contain lowercase letters, numbers, and hyphens.')
        )


def validate_hex_color(value):
    """Validate hexadecimal color code"""
    pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    
    if not re.match(pattern, value):
        raise ValidationError(
            _('Enter a valid hex color code (e.g., #FF0000 or #F00).')
        )


def validate_weight(value):
    """Validate product weight is positive"""
    if value <= 0:
        raise ValidationError(_('Weight must be greater than zero.'))


def validate_dimensions(value):
    """Validate product dimensions format (L x W x H)"""
    if not value:
        return
    
    pattern = r'^\d+(\.\d+)?\s*x\s*\d+(\.\d+)?\s*x\s*\d+(\.\d+)?$'
    
    if not re.match(pattern, value, re.IGNORECASE):
        raise ValidationError(
            _('Enter dimensions in format: Length x Width x Height (e.g., 10 x 5 x 2)')
        )


def validate_rating(value):
    """Validate rating is between 1 and 5"""
    if not (1 <= value <= 5):
        raise ValidationError(_('Rating must be between 1 and 5.'))


def validate_order_number(value):
    """Validate order number format"""
    pattern = r'^AFE-\d{8}-[A-Z0-9]{4}$'
    
    if not re.match(pattern, value):
        raise ValidationError(
            _('Invalid order number format.')
        )


def validate_moncash_transaction_id(value):
    """Validate MonCash transaction ID format"""
    # MonCash transaction IDs are typically alphanumeric
    pattern = r'^[A-Za-z0-9_-]+$'
    
    if not re.match(pattern, value):
        raise ValidationError(
            _('Invalid MonCash transaction ID format.')
        )


def validate_promo_code(value):
    """Validate promotion code format"""
    # Promo codes should be uppercase alphanumeric
    pattern = r'^[A-Z0-9]+$'
    
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            _('Promo code can only contain uppercase letters and numbers.')
        )
    
    if len(value) < 3 or len(value) > 20:
        raise ValidationError(
            _('Promo code must be between 3 and 20 characters.')
        )


def validate_business_registration_number(value):
    """Validate Haitian business registration number"""
    # This is a placeholder - adjust based on actual Haiti business number format
    pattern = r'^\d{6,12}$'
    
    if not re.match(pattern, value):
        raise ValidationError(
            _('Enter a valid business registration number.')
        )


def validate_tax_id(value):
    """Validate tax identification number"""
    # This is a placeholder - adjust based on actual Haiti tax ID format
    pattern = r'^\d{9,15}$'
    
    if not re.match(pattern, value):
        raise ValidationError(
            _('Enter a valid tax identification number.')
        )


# Common regex validators
haitian_phone_validator = RegexValidator(
    regex=r'^\+?509?\s?\d{4}\s?\d{4}$',
    message=_('Enter a valid Haitian phone number.')
)

alphanumeric_validator = RegexValidator(
    regex=r'^[A-Za-z0-9]+$',
    message=_('This field can only contain letters and numbers.')
)

slug_validator = RegexValidator(
    regex=r'^[a-z0-9-]+$',
    message=_('Slug can only contain lowercase letters, numbers, and hyphens.')
)

sku_validator = RegexValidator(
    regex=r'^[A-Za-z0-9_-]+$',
    message=_('SKU can only contain letters, numbers, hyphens, and underscores.')
)