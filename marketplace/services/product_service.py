# marketplace/services/product_service.py
"""
Product-related business logic service
"""

from typing import List, Dict, Any, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from marketplace.models import Product, Category, ProductImage
from marketplace.utils.slug import generate_unique_slug

User = get_user_model()


class ProductService:
    """Service for product-related business operations"""
    
    @staticmethod
    def create_product(seller: User, product_data: Dict[str, Any], images: List = None) -> Product:
        """Create a new product with images"""
        with transaction.atomic():
            # Generate slug if not provided
            if 'slug' not in product_data or not product_data['slug']:
                product_data['slug'] = generate_unique_slug(
                    Product, 
                    product_data['name']
                )
            
            # Set seller
            product_data['seller'] = seller
            
            # Validate price
            if 'promotional_price' in product_data and product_data['promotional_price']:
                if product_data['promotional_price'] >= product_data['price']:
                    raise ValidationError("Promotional price must be less than regular price")
            
            # Create product
            product = Product.objects.create(**product_data)
            
            # Add images if provided
            if images:
                ProductService.add_product_images(product, images)
            
            return product
    
    @staticmethod
    def update_product(product: Product, product_data: Dict[str, Any]) -> Product:
        """Update existing product"""
        with transaction.atomic():
            # Validate promotional price
            if 'promotional_price' in product_data and product_data['promotional_price']:
                price = product_data.get('price', product.price)
                if product_data['promotional_price'] >= price:
                    raise ValidationError("Promotional price must be less than regular price")
            
            # Update fields
            for field, value in product_data.items():
                if hasattr(product, field):
                    setattr(product, field, value)
            
            product.full_clean()
            product.save()
            
            return product
    
    @staticmethod
    def add_product_images(product: Product, images: List) -> List[ProductImage]:
        """Add multiple images to a product"""
        image_objects = []
        
        for i, image_data in enumerate(images):
            if isinstance(image_data, dict):
                image_data['product'] = product
                image_data['display_order'] = i + 1
                image_obj = ProductImage.objects.create(**image_data)
            else:
                # Assume it's an image file
                image_obj = ProductImage.objects.create(
                    product=product,
                    image=image_data,
                    display_order=i + 1
                )
            
            image_objects.append(image_obj)
        
        return image_objects
    
    @staticmethod
    def update_stock(product: Product, quantity: int, operation: str = 'set') -> Product:
        """Update product stock quantity"""
        if operation == 'set':
            product.stock_quantity = quantity
        elif operation == 'increase':
            product.stock_quantity += quantity
        elif operation == 'decrease':
            if product.stock_quantity < quantity:
                raise ValidationError("Insufficient stock")
            product.stock_quantity -= quantity
        else:
            raise ValueError("Invalid operation. Use 'set', 'increase', or 'decrease'")
        
        product.save(update_fields=['stock_quantity'])
        return product
    
    @staticmethod
    def check_availability(product: Product, quantity: int = 1) -> bool:
        """Check if product is available in requested quantity"""
        if not product.is_active:
            return False
        
        if product.is_digital:
            return True
        
        return product.stock_quantity >= quantity
    
    @staticmethod
    def get_effective_price(product: Product) -> float:
        """Get the effective selling price (promotional or regular)"""
        if product.promotional_price and product.promotional_price < product.price:
            return product.promotional_price
        return product.price
    
    @staticmethod
    def calculate_discount_percentage(product: Product) -> Optional[float]:
        """Calculate discount percentage if promotional price exists"""
        if not product.promotional_price or product.promotional_price >= product.price:
            return None
        
        discount = product.price - product.promotional_price
        return round((discount / product.price) * 100, 2)
    
    @staticmethod
    def get_related_products(product: Product, limit: int = 4) -> List[Product]:
        """Get related products based on category and tags"""
        related = Product.objects.available().filter(
            category=product.category
        ).exclude(id=product.id)
        
        # If the product has tags, prioritize products with similar tags
        if product.tags:
            tag_list = [tag.strip() for tag in product.tags.split(',')]
            for tag in tag_list:
                related = related.filter(tags__icontains=tag)
        
        return list(related[:limit])
    
    @staticmethod
    def search_products(query: str, filters: Dict[str, Any] = None) -> List[Product]:
        """Advanced product search with filters"""
        products = Product.objects.search(query)
        
        if filters:
            # Category filter
            if 'category' in filters and filters['category']:
                products = products.filter(category=filters['category'])
            
            # Price range filter
            if 'min_price' in filters or 'max_price' in filters:
                products = products.price_range(
                    min_price=filters.get('min_price'),
                    max_price=filters.get('max_price')
                )
            
            # Brand filter
            if 'brand' in filters and filters['brand']:
                products = products.filter(brand__icontains=filters['brand'])
            
            # Seller filter
            if 'seller' in filters and filters['seller']:
                products = products.filter(seller=filters['seller'])
            
            # Rating filter
            if 'min_rating' in filters and filters['min_rating']:
                products = products.filter(
                    average_rating__gte=filters['min_rating']
                )
        
        return products
    
    @staticmethod
    def bulk_update_status(product_ids: List[int], is_active: bool) -> int:
        """Bulk update product active status"""
        return Product.objects.filter(
            id__in=product_ids
        ).update(is_active=is_active)
    
    @staticmethod
    def get_low_stock_products(seller: User = None, threshold: int = None) -> List[Product]:
        """Get products with low stock"""
        queryset = Product.objects.low_stock()
        
        if seller:
            queryset = queryset.filter(seller=seller)
        
        if threshold:
            queryset = queryset.filter(stock_quantity__lte=threshold)
        
        return list(queryset)
    
    @staticmethod
    def get_seller_analytics(seller: User) -> Dict[str, Any]:
        """Get analytics data for seller's products"""
        products = Product.objects.by_seller(seller)
        
        analytics = {
            'total_products': products.count(),
            'active_products': products.filter(is_active=True).count(),
            'featured_products': products.filter(is_featured=True).count(),
            'out_of_stock': products.filter(stock_quantity=0, is_digital=False).count(),
            'low_stock': products.filter(
                stock_quantity__lte=5,
                stock_quantity__gt=0,
                is_digital=False
            ).count(),
        }
        
        return analytics