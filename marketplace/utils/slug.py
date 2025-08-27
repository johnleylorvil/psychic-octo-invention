# marketplace/utils/slug.py
"""
Slug generation utilities
"""

import re
from django.utils.text import slugify


def generate_unique_slug(model_class, title, slug_field='slug', max_length=50):
    """Generate a unique slug for a model instance"""
    base_slug = slugify(title)[:max_length]
    
    if not base_slug:
        base_slug = 'item'
    
    slug = base_slug
    counter = 1
    
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
        
        # Ensure we don't exceed max_length
        if len(slug) > max_length:
            base_slug = base_slug[:max_length - len(f"-{counter}")]
            slug = f"{base_slug}-{counter}"
    
    return slug