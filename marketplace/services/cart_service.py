# marketplace/services/cart_service.py
"""
Cart service for business logic related to shopping cart operations
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CartService:
    """Service for cart-related business logic"""
    
    @staticmethod
    def get_or_create_cart(user=None, session_id=None):
        """Get existing cart or create new one"""
        from ..models import Cart
        
        if user and user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                user=user,
                is_active=True,
                defaults={'expires_at': None}
            )
        elif session_id:
            cart, created = Cart.objects.get_or_create(
                session_id=session_id,
                is_active=True,
                defaults={
                    'expires_at': timezone.now() + timezone.timedelta(hours=24)
                }
            )
        else:
            raise ValidationError("Either user or session_id must be provided")
        
        return cart, created
    
    @staticmethod
    def add_to_cart(cart, product, quantity: int = 1, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add product to cart with validation"""
        from ..models import CartItem
        
        try:
            with transaction.atomic():
                # Validate product availability
                if not product.is_active:
                    return {
                        'success': False,
                        'error': 'Ce produit n\'est plus disponible'
                    }
                
                # Check stock for physical products
                if not product.is_digital and product.stock_quantity < quantity:
                    return {
                        'success': False,
                        'error': f'Stock insuffisant. Disponible: {product.stock_quantity}'
                    }
                
                # Get or create cart item
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={
                        'quantity': quantity,
                        'price': product.current_price,
                        'options': options or {}
                    }
                )
                
                if not created:
                    # Update existing item
                    new_quantity = cart_item.quantity + quantity
                    
                    # Check stock again for updated quantity
                    if not product.is_digital and product.stock_quantity < new_quantity:
                        return {
                            'success': False,
                            'error': f'Stock insuffisant pour cette quantité. Maximum: {product.stock_quantity}'
                        }
                    
                    cart_item.quantity = new_quantity
                    cart_item.price = product.current_price  # Update with current price
                    cart_item.options = options or cart_item.options
                    cart_item.save()
                
                # Update cart timestamp
                cart.save(update_fields=['updated_at'])
                
                return {
                    'success': True,
                    'cart_item': cart_item,
                    'cart_total': cart.subtotal,
                    'cart_items_count': cart.total_items
                }
                
        except Exception as e:
            logger.error(f"Error adding product {product.id} to cart {cart.id}: {e}")
            return {
                'success': False,
                'error': 'Une erreur est survenue lors de l\'ajout au panier'
            }
    
    @staticmethod
    def update_cart_item(cart_item, quantity: int) -> Dict[str, Any]:
        """Update cart item quantity with validation"""
        try:
            with transaction.atomic():
                if quantity <= 0:
                    cart_item.delete()
                    return {
                        'success': True,
                        'action': 'removed',
                        'cart_total': cart_item.cart.subtotal,
                        'cart_items_count': cart_item.cart.total_items
                    }
                
                # Check stock for physical products
                product = cart_item.product
                if not product.is_digital and product.stock_quantity < quantity:
                    return {
                        'success': False,
                        'error': f'Stock insuffisant. Maximum: {product.stock_quantity}'
                    }
                
                cart_item.quantity = quantity
                cart_item.price = product.current_price  # Update with current price
                cart_item.save()
                
                # Update cart timestamp
                cart_item.cart.save(update_fields=['updated_at'])
                
                return {
                    'success': True,
                    'action': 'updated',
                    'cart_item': cart_item,
                    'cart_total': cart_item.cart.subtotal,
                    'cart_items_count': cart_item.cart.total_items
                }
                
        except Exception as e:
            logger.error(f"Error updating cart item {cart_item.id}: {e}")
            return {
                'success': False,
                'error': 'Une erreur est survenue lors de la mise à jour'
            }
    
    @staticmethod
    def remove_from_cart(cart, product) -> Dict[str, Any]:
        """Remove product from cart"""
        try:
            cart_item = cart.items.filter(product=product).first()
            if cart_item:
                cart_item.delete()
                cart.save(update_fields=['updated_at'])
                
                return {
                    'success': True,
                    'cart_total': cart.subtotal,
                    'cart_items_count': cart.total_items
                }
            else:
                return {
                    'success': False,
                    'error': 'Produit non trouvé dans le panier'
                }
                
        except Exception as e:
            logger.error(f"Error removing product {product.id} from cart {cart.id}: {e}")
            return {
                'success': False,
                'error': 'Une erreur est survenue lors de la suppression'
            }
    
    @staticmethod
    def clear_cart(cart) -> bool:
        """Clear all items from cart"""
        try:
            cart.items.all().delete()
            cart.save(update_fields=['updated_at'])
            return True
        except Exception as e:
            logger.error(f"Error clearing cart {cart.id}: {e}")
            return False
    
    @staticmethod
    def merge_carts(user_cart, session_cart) -> bool:
        """Merge session cart into user cart when user logs in"""
        if not session_cart or not session_cart.items.exists():
            return True
        
        try:
            with transaction.atomic():
                for session_item in session_cart.items.all():
                    # Try to find existing item in user cart
                    user_item = user_cart.items.filter(
                        product=session_item.product
                    ).first()
                    
                    if user_item:
                        # Merge quantities
                        user_item.quantity += session_item.quantity
                        user_item.save()
                    else:
                        # Move item to user cart
                        session_item.cart = user_cart
                        session_item.save()
                
                # Clear and deactivate session cart
                session_cart.is_active = False
                session_cart.save()
                
                return True
                
        except Exception as e:
            logger.error(f"Error merging carts: {e}")
            return False
    
    @staticmethod
    def validate_cart_for_checkout(cart) -> Dict[str, Any]:
        """Validate cart items before checkout"""
        if cart.is_empty:
            return {
                'valid': False,
                'errors': ['Le panier est vide']
            }
        
        errors = []
        updated_items = []
        
        for item in cart.items.all():
            product = item.product
            
            # Check if product is still active
            if not product.is_active:
                errors.append(f'{product.name} n\'est plus disponible')
                continue
            
            # Check stock for physical products
            if not product.is_digital and product.stock_quantity < item.quantity:
                if product.stock_quantity > 0:
                    # Update quantity to available stock
                    item.quantity = product.stock_quantity
                    item.save()
                    updated_items.append({
                        'product': product.name,
                        'new_quantity': product.stock_quantity
                    })
                else:
                    errors.append(f'{product.name} est en rupture de stock')
            
            # Check if price has changed significantly
            current_price = product.current_price
            if abs(current_price - item.price) / item.price > 0.1:  # 10% change
                item.price = current_price
                item.save()
                updated_items.append({
                    'product': product.name,
                    'new_price': current_price
                })
        
        result = {
            'valid': len(errors) == 0,
            'errors': errors,
            'updated_items': updated_items
        }
        
        if updated_items:
            result['message'] = 'Certains articles ont été mis à jour'
        
        return result
    
    @staticmethod
    def calculate_cart_totals(cart) -> Dict[str, Any]:
        """Calculate comprehensive cart totals"""
        subtotal = cart.subtotal
        
        # Calculate shipping (simplified logic)
        shipping_cost = CartService._calculate_shipping(cart)
        
        # Calculate tax (if applicable)
        tax_amount = CartService._calculate_tax(subtotal)
        
        # Calculate any discounts
        discount_amount = CartService._calculate_discounts(cart)
        
        total = subtotal + shipping_cost + tax_amount - discount_amount
        
        return {
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'tax_amount': tax_amount,
            'discount_amount': discount_amount,
            'total': total,
            'currency': 'HTG'
        }
    
    @staticmethod
    def _calculate_shipping(cart) -> float:
        """Calculate shipping cost for cart"""
        # Simplified shipping logic
        # In a real application, this would consider weight, location, etc.
        
        # Check for digital-only cart
        if all(item.product.is_digital for item in cart.items.all()):
            return 0.0
        
        # Free shipping threshold
        from ..models import SiteSetting
        free_shipping_threshold = float(
            SiteSetting.objects.get_value('free_shipping_threshold', 1000.0)
        )
        
        if cart.subtotal >= free_shipping_threshold:
            return 0.0
        
        # Standard shipping cost
        return float(SiteSetting.objects.get_value('shipping_cost', 50.0))
    
    @staticmethod
    def _calculate_tax(subtotal: float) -> float:
        """Calculate tax amount"""
        from ..models import SiteSetting
        tax_rate = float(SiteSetting.objects.get_value('tax_rate', 0.0))
        return subtotal * (tax_rate / 100)
    
    @staticmethod
    def _calculate_discounts(cart) -> float:
        """Calculate discount amount"""
        # Placeholder for discount logic (coupons, promotions, etc.)
        return 0.0
    
    @staticmethod
    def cleanup_expired_carts():
        """Clean up expired session carts"""
        from ..models import Cart
        
        try:
            expired_carts = Cart.objects.filter(
                expires_at__lt=timezone.now(),
                is_active=True,
                user__isnull=True  # Session carts only
            )
            
            count = expired_carts.count()
            expired_carts.delete()
            
            logger.info(f"Cleaned up {count} expired carts")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired carts: {e}")
            return 0