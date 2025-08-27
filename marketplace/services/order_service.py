# marketplace/services/order_service.py
"""
Order processing business logic service
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from marketplace.models import Cart, CartItem, Order, OrderItem, OrderStatusHistory
from marketplace.services.cart_service import CartService
from marketplace.services.product_service import ProductService

User = get_user_model()


class OrderService:
    """Service for order processing operations"""
    
    ORDER_STATUSES = [
        'pending',
        'confirmed', 
        'processing',
        'shipped',
        'delivered',
        'cancelled',
        'refunded'
    ]
    
    PAYMENT_STATUSES = [
        'pending',
        'paid',
        'failed',
        'refunded'
    ]
    
    @staticmethod
    def create_order_from_cart(cart: Cart, shipping_address: Dict[str, Any],
                              billing_address: Dict[str, Any] = None,
                              payment_method: str = 'moncash',
                              special_instructions: str = '') -> Order:
        """Create order from cart items"""
        with transaction.atomic():
            # Validate cart
            cart_summary = CartService.get_cart_summary(cart)
            if not cart_summary['is_valid']:
                raise ValidationError("Cart contains invalid items")
            
            if cart_summary['item_count'] == 0:
                raise ValidationError("Cart is empty")
            
            # Use shipping address as billing if not provided
            if not billing_address:
                billing_address = shipping_address.copy()
            
            # Calculate totals
            totals = cart_summary['totals']
            
            # Create order
            order = Order.objects.create(
                user=cart.user,
                email=cart.user.email if cart.user else shipping_address.get('email'),
                phone=shipping_address.get('phone'),
                
                # Shipping address
                shipping_first_name=shipping_address.get('first_name'),
                shipping_last_name=shipping_address.get('last_name'),
                shipping_address_line1=shipping_address.get('address_line1'),
                shipping_address_line2=shipping_address.get('address_line2', ''),
                shipping_city=shipping_address.get('city'),
                shipping_state=shipping_address.get('state'),
                shipping_postal_code=shipping_address.get('postal_code'),
                shipping_country=shipping_address.get('country', 'HT'),
                
                # Billing address
                billing_first_name=billing_address.get('first_name'),
                billing_last_name=billing_address.get('last_name'),
                billing_address_line1=billing_address.get('address_line1'),
                billing_address_line2=billing_address.get('address_line2', ''),
                billing_city=billing_address.get('city'),
                billing_state=billing_address.get('state'),
                billing_postal_code=billing_address.get('postal_code'),
                billing_country=billing_address.get('country', 'HT'),
                
                # Order details
                subtotal=totals['subtotal'],
                shipping_cost=totals['shipping_cost'],
                tax_amount=totals['tax_amount'],
                total_amount=totals['total'],
                payment_method=payment_method,
                special_instructions=special_instructions,
                
                # Status
                status='pending',
                payment_status='pending'
            )
            
            # Create order items
            for cart_item in cart_summary['items']:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_sku=cart_item.product.sku,
                    product_variant=cart_item.product_variant,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    total_price=cart_item.unit_price * cart_item.quantity
                )
                
                # Update product stock
                ProductService.update_stock(
                    cart_item.product,
                    cart_item.quantity,
                    'decrease'
                )
            
            # Create initial status history
            OrderStatusHistory.objects.create(
                order=order,
                status='pending',
                notes='Order created'
            )
            
            # Clear cart
            CartService.clear_cart(cart)
            cart.is_active = False
            cart.save()
            
            return order
    
    @staticmethod
    def update_order_status(order: Order, new_status: str, notes: str = '',
                          user: User = None) -> Order:
        """Update order status with history tracking"""
        if new_status not in OrderService.ORDER_STATUSES:
            raise ValidationError(f"Invalid status: {new_status}")
        
        old_status = order.status
        
        with transaction.atomic():
            order.status = new_status
            order.save(update_fields=['status'])
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                notes=notes,
                user=user
            )
            
            # Handle status-specific logic
            OrderService._handle_status_change(order, old_status, new_status)
        
        return order
    
    @staticmethod
    def _handle_status_change(order: Order, old_status: str, new_status: str):
        """Handle status-specific business logic"""
        # If order is cancelled, restore stock
        if new_status == 'cancelled' and old_status not in ['cancelled', 'refunded']:
            for order_item in OrderItem.objects.filter(order=order):
                ProductService.update_stock(
                    order_item.product,
                    order_item.quantity,
                    'increase'
                )
        
        # If order is confirmed, send confirmation email
        elif new_status == 'confirmed':
            # TODO: Send confirmation email
            pass
        
        # If order is shipped, send tracking info
        elif new_status == 'shipped':
            # TODO: Send shipping notification
            pass
        
        # If order is delivered, allow reviews
        elif new_status == 'delivered':
            # TODO: Send delivery confirmation
            pass
    
    @staticmethod
    def cancel_order(order: Order, reason: str = '', user: User = None) -> Order:
        """Cancel an order"""
        if order.status in ['delivered', 'cancelled', 'refunded']:
            raise ValidationError("Cannot cancel order in current status")
        
        return OrderService.update_order_status(
            order=order,
            new_status='cancelled',
            notes=f"Order cancelled. Reason: {reason}",
            user=user
        )
    
    @staticmethod
    def calculate_order_totals(order_items: List[Dict[str, Any]], 
                             shipping_address: Dict[str, Any]) -> Dict[str, Decimal]:
        """Calculate order totals from items"""
        subtotal = Decimal('0.00')
        
        for item in order_items:
            line_total = Decimal(str(item['unit_price'])) * item['quantity']
            subtotal += line_total
        
        # Calculate shipping
        shipping_cost = OrderService._calculate_shipping(shipping_address, subtotal)
        
        # Calculate tax
        tax_amount = OrderService._calculate_tax(shipping_address, subtotal)
        
        total = subtotal + shipping_cost + tax_amount
        
        return {
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'tax_amount': tax_amount,
            'total': total
        }
    
    @staticmethod
    def _calculate_shipping(shipping_address: Dict[str, Any], subtotal: Decimal) -> Decimal:
        """Calculate shipping cost based on address and subtotal"""
        # Free shipping over 1000 HTG
        if subtotal >= Decimal('1000.00'):
            return Decimal('0.00')
        
        # Different rates based on location
        city = shipping_address.get('city', '').lower()
        
        if city in ['port-au-prince', 'pétion-ville', 'carrefour']:
            return Decimal('50.00')  # Metro area
        else:
            return Decimal('100.00')  # Outside metro area
    
    @staticmethod
    def _calculate_tax(shipping_address: Dict[str, Any], subtotal: Decimal) -> Decimal:
        """Calculate tax amount"""
        # No tax implementation for Haiti
        return Decimal('0.00')
    
    @staticmethod
    def get_order_summary(order: Order) -> Dict[str, Any]:
        """Get comprehensive order summary"""
        items = OrderItem.objects.filter(order=order).select_related('product')
        
        return {
            'order': order,
            'items': list(items),
            'item_count': items.count(),
            'status_history': list(
                OrderStatusHistory.objects.filter(order=order).order_by('-created_at')
            ),
            'can_cancel': order.status in ['pending', 'confirmed'],
            'can_modify': order.status == 'pending',
        }
    
    @staticmethod
    def get_user_orders(user: User, status: str = None, limit: int = None) -> List[Order]:
        """Get user orders with optional filtering"""
        orders = Order.objects.for_user(user)
        
        if status:
            orders = orders.filter(status=status)
        
        if limit:
            orders = orders[:limit]
        
        return list(orders)
    
    @staticmethod
    def search_orders(filters: Dict[str, Any]) -> List[Order]:
        """Search orders with multiple filters"""
        orders = Order.objects.all()
        
        if 'user' in filters:
            orders = orders.filter(user=filters['user'])
        
        if 'status' in filters:
            orders = orders.filter(status=filters['status'])
        
        if 'payment_status' in filters:
            orders = orders.filter(payment_status=filters['payment_status'])
        
        if 'date_from' in filters:
            orders = orders.filter(created_at__date__gte=filters['date_from'])
        
        if 'date_to' in filters:
            orders = orders.filter(created_at__date__lte=filters['date_to'])
        
        if 'min_amount' in filters:
            orders = orders.filter(total_amount__gte=filters['min_amount'])
        
        if 'max_amount' in filters:
            orders = orders.filter(total_amount__lte=filters['max_amount'])
        
        return list(orders.order_by('-created_at'))
    
    @staticmethod
    def get_sales_analytics(seller: User = None, date_from: str = None, 
                          date_to: str = None) -> Dict[str, Any]:
        """Get sales analytics for seller or overall"""
        orders = Order.objects.all()
        
        if seller:
            orders = orders.filter(items__product__seller=seller).distinct()
        
        if date_from:
            orders = orders.filter(created_at__date__gte=date_from)
        
        if date_to:
            orders = orders.filter(created_at__date__lte=date_to)
        
        total_orders = orders.count()
        completed_orders = orders.filter(status='delivered', payment_status='paid')
        
        analytics = {
            'total_orders': total_orders,
            'completed_orders': completed_orders.count(),
            'pending_orders': orders.filter(status='pending').count(),
            'cancelled_orders': orders.filter(status='cancelled').count(),
            'total_revenue': sum(order.total_amount for order in completed_orders),
            'average_order_value': (
                sum(order.total_amount for order in completed_orders) / completed_orders.count()
                if completed_orders.count() > 0 else 0
            ),
        }
        
        return analytics