# marketplace/services/cart_service.py
"""
Shopping cart business logic service
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from marketplace.models import Cart, CartItem, Product
from marketplace.services.product_service import ProductService

User = get_user_model()


class CartService:
    """Service for shopping cart operations"""
    
    @staticmethod
    def get_or_create_cart(user: User = None, session_id: str = None) -> Cart:
        """Get or create cart for user or session"""
        if user and user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                user=user,
                is_active=True,
                defaults={
                    'expires_at': timezone.now() + timezone.timedelta(days=30)
                }
            )
        elif session_id:
            cart, created = Cart.objects.get_or_create(
                session_id=session_id,
                is_active=True,
                defaults={
                    'expires_at': timezone.now() + timezone.timedelta(days=7)
                }
            )
        else:
            raise ValueError("Either user or session_id must be provided")
        
        return cart
    
    @staticmethod
    def add_to_cart(cart: Cart, product: Product, quantity: int = 1, 
                   product_variant: str = None) -> CartItem:
        """Add product to cart or update quantity if already exists"""
        with transaction.atomic():
            # Check product availability
            if not ProductService.check_availability(product, quantity):
                raise ValidationError("Product is not available in requested quantity")
            
            # Check if item already exists in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                product_variant=product_variant,
                defaults={
                    'quantity': quantity,
                    'unit_price': ProductService.get_effective_price(product)
                }
            )
            
            if not created:
                # Update quantity for existing item
                new_quantity = cart_item.quantity + quantity
                
                # Check availability for new quantity
                if not ProductService.check_availability(product, new_quantity):
                    raise ValidationError("Product is not available in requested quantity")
                
                cart_item.quantity = new_quantity
                cart_item.unit_price = ProductService.get_effective_price(product)
                cart_item.save()
            
            # Update cart timestamp
            cart.updated_at = timezone.now()
            cart.save(update_fields=['updated_at'])
            
            return cart_item
    
    @staticmethod
    def update_cart_item(cart_item: CartItem, quantity: int) -> CartItem:
        """Update cart item quantity"""
        with transaction.atomic():
            if quantity <= 0:
                cart_item.delete()
                return None
            
            # Check product availability
            if not ProductService.check_availability(cart_item.product, quantity):
                raise ValidationError("Product is not available in requested quantity")
            
            cart_item.quantity = quantity
            cart_item.unit_price = ProductService.get_effective_price(cart_item.product)
            cart_item.save()
            
            # Update cart timestamp
            cart_item.cart.updated_at = timezone.now()
            cart_item.cart.save(update_fields=['updated_at'])
            
            return cart_item
    
    @staticmethod
    def remove_from_cart(cart: Cart, product: Product, product_variant: str = None) -> bool:
        """Remove product from cart"""
        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                product=product,
                product_variant=product_variant
            )
            cart_item.delete()
            
            # Update cart timestamp
            cart.updated_at = timezone.now()
            cart.save(update_fields=['updated_at'])
            
            return True
        except CartItem.DoesNotExist:
            return False
    
    @staticmethod
    def clear_cart(cart: Cart) -> bool:
        """Remove all items from cart"""
        deleted_count = CartItem.objects.filter(cart=cart).delete()[0]
        
        # Update cart timestamp
        cart.updated_at = timezone.now()
        cart.save(update_fields=['updated_at'])
        
        return deleted_count > 0
    
    @staticmethod
    def calculate_cart_totals(cart: Cart) -> Dict[str, Decimal]:
        """Calculate cart totals"""
        items = CartItem.objects.filter(cart=cart)
        
        subtotal = Decimal('0.00')
        total_items = 0
        
        for item in items:
            line_total = item.unit_price * item.quantity
            subtotal += line_total
            total_items += item.quantity
        
        # Calculate shipping (placeholder logic)
        shipping_cost = CartService._calculate_shipping_cost(cart, subtotal)
        
        # Calculate tax (placeholder logic)
        tax_amount = CartService._calculate_tax(cart, subtotal)
        
        # Calculate total
        total = subtotal + shipping_cost + tax_amount
        
        return {
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'tax_amount': tax_amount,
            'total': total,
            'total_items': total_items
        }
    
    @staticmethod
    def _calculate_shipping_cost(cart: Cart, subtotal: Decimal) -> Decimal:
        """Calculate shipping cost (placeholder implementation)"""
        # Free shipping over 1000 HTG
        if subtotal >= Decimal('1000.00'):
            return Decimal('0.00')
        
        # Flat rate shipping
        return Decimal('50.00')
    
    @staticmethod
    def _calculate_tax(cart: Cart, subtotal: Decimal) -> Decimal:
        """Calculate tax amount (placeholder implementation)"""
        # No tax for now in Haiti context
        return Decimal('0.00')
    
    @staticmethod
    def validate_cart_items(cart: Cart) -> List[Dict[str, Any]]:
        """Validate cart items availability and pricing"""
        issues = []
        
        for item in CartItem.objects.filter(cart=cart):
            # Check if product is still available
            if not item.product.is_active:
                issues.append({
                    'item': item,
                    'issue': 'product_unavailable',
                    'message': f'{item.product.name} is no longer available'
                })
                continue
            
            # Check stock availability
            if not ProductService.check_availability(item.product, item.quantity):
                available_stock = item.product.stock_quantity
                issues.append({
                    'item': item,
                    'issue': 'insufficient_stock',
                    'message': f'Only {available_stock} units of {item.product.name} are available',
                    'available_quantity': available_stock
                })
            
            # Check if price has changed
            current_price = ProductService.get_effective_price(item.product)
            if item.unit_price != current_price:
                issues.append({
                    'item': item,
                    'issue': 'price_changed',
                    'message': f'Price for {item.product.name} has changed',
                    'old_price': item.unit_price,
                    'new_price': current_price
                })
        
        return issues
    
    @staticmethod
    def merge_carts(source_cart: Cart, target_cart: Cart) -> Cart:
        """Merge items from source cart to target cart (for user login)"""
        with transaction.atomic():
            for item in CartItem.objects.filter(cart=source_cart):
                try:
                    CartService.add_to_cart(
                        cart=target_cart,
                        product=item.product,
                        quantity=item.quantity,
                        product_variant=item.product_variant
                    )
                except ValidationError:
                    # Skip items that can't be added (out of stock, etc.)
                    pass
            
            # Deactivate source cart
            source_cart.is_active = False
            source_cart.save()
            
            return target_cart
    
    @staticmethod
    def get_cart_summary(cart: Cart) -> Dict[str, Any]:
        """Get comprehensive cart summary"""
        items = CartItem.objects.filter(cart=cart).select_related('product')
        totals = CartService.calculate_cart_totals(cart)
        issues = CartService.validate_cart_items(cart)
        
        return {
            'cart': cart,
            'items': list(items),
            'totals': totals,
            'issues': issues,
            'item_count': items.count(),
            'is_valid': len(issues) == 0
        }
    
    @staticmethod
    def cleanup_expired_carts() -> int:
        """Remove expired carts (run as scheduled task)"""
        expired_carts = Cart.objects.expired()
        count = expired_carts.count()
        
        # Delete cart items first
        CartItem.objects.filter(cart__in=expired_carts).delete()
        
        # Delete expired carts
        expired_carts.delete()
        
        return count