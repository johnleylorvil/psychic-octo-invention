# marketplace/services/order_service.py
"""
Order service for business logic related to order processing
"""

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class OrderService:
    """Service for order-related business logic"""
    
    @staticmethod
    def create_order_from_cart(cart, customer_data: Dict[str, Any], payment_method: str = 'moncash') -> Dict[str, Any]:
        """Create order from cart with validation"""
        from ..models import Order, OrderItem
        from .cart_service import CartService
        from .product_service import ProductService
        
        # Validate cart first
        cart_validation = CartService.validate_cart_for_checkout(cart)
        if not cart_validation['valid']:
            return {
                'success': False,
                'errors': cart_validation['errors']
            }
        
        try:
            with transaction.atomic():
                # Calculate totals
                totals = CartService.calculate_cart_totals(cart)
                
                # Create order
                order = Order.objects.create(
                    user=cart.user,
                    customer_name=customer_data.get('name', ''),
                    customer_email=customer_data.get('email', ''),
                    customer_phone=customer_data.get('phone', ''),
                    shipping_address=customer_data.get('shipping_address', ''),
                    shipping_city=customer_data.get('shipping_city', 'Port-au-Prince'),
                    shipping_country=customer_data.get('shipping_country', 'Haïti'),
                    billing_address=customer_data.get('billing_address', ''),
                    billing_city=customer_data.get('billing_city', ''),
                    billing_country=customer_data.get('billing_country', 'Haïti'),
                    subtotal=totals['subtotal'],
                    shipping_cost=totals['shipping_cost'],
                    tax_amount=totals['tax_amount'],
                    discount_amount=totals['discount_amount'],
                    total_amount=totals['total'],
                    payment_method=payment_method,
                    notes=customer_data.get('notes', ''),
                )
                
                # Create order items and update stock
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.price,
                        product_options=cart_item.options
                    )
                    
                    # Update product stock for physical products
                    if not cart_item.product.is_digital:
                        ProductService.update_product_stock(
                            cart_item.product, 
                            -cart_item.quantity
                        )
                
                # Clear cart after successful order creation
                CartService.clear_cart(cart)
                
                return {
                    'success': True,
                    'order': order,
                    'total_amount': order.total_amount
                }
                
        except Exception as e:
            logger.error(f"Error creating order from cart {cart.id}: {e}")
            return {
                'success': False,
                'error': 'Une erreur est survenue lors de la création de la commande'
            }
    
    @staticmethod
    def update_order_status(order, new_status: str, user=None, comment: str = None) -> bool:
        """Update order status with history tracking"""
        from ..models import OrderStatusHistory
        
        if new_status not in dict(Order.STATUS_CHOICES):
            raise ValidationError(f"Invalid status: {new_status}")
        
        try:
            with transaction.atomic():
                old_status = order.status
                
                # Update order status
                order.status = new_status
                
                # Set delivery timestamp for delivered orders
                if new_status == 'delivered' and not order.delivered_at:
                    order.delivered_at = timezone.now()
                
                order.save()
                
                # Create status history entry
                OrderStatusHistory.objects.create(
                    order=order,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=user,
                    comment=comment
                )
                
                # Handle status-specific actions
                OrderService._handle_status_change(order, old_status, new_status)
                
                return True
                
        except Exception as e:
            logger.error(f"Error updating order {order.id} status: {e}")
            return False
    
    @staticmethod
    def cancel_order(order, reason: str = None, user=None) -> Dict[str, Any]:
        """Cancel order and restore stock"""
        if not order.can_be_cancelled:
            return {
                'success': False,
                'error': 'Cette commande ne peut pas être annulée'
            }
        
        try:
            with transaction.atomic():
                # Restore product stock
                for item in order.items.all():
                    if not item.product.is_digital:
                        ProductService.update_product_stock(
                            item.product, 
                            item.quantity
                        )
                
                # Update order status
                OrderService.update_order_status(
                    order, 
                    'cancelled', 
                    user, 
                    reason
                )
                
                return {
                    'success': True,
                    'message': 'Commande annulée avec succès'
                }
                
        except Exception as e:
            logger.error(f"Error cancelling order {order.id}: {e}")
            return {
                'success': False,
                'error': 'Une erreur est survenue lors de l\'annulation'
            }
    
    @staticmethod
    def calculate_order_analytics(date_range: Optional[tuple] = None) -> Dict[str, Any]:
        """Calculate order analytics for dashboard"""
        from ..models import Order
        from django.db.models import Sum, Count, Avg
        
        queryset = Order.objects.all()
        
        if date_range:
            start_date, end_date = date_range
            queryset = queryset.filter(
                created_at__date__range=[start_date, end_date]
            )
        
        # Basic statistics
        stats = queryset.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total_amount'),
            average_order_value=Avg('total_amount')
        )
        
        # Order status distribution
        status_distribution = {}
        for status_code, status_label in Order.STATUS_CHOICES:
            count = queryset.filter(status=status_code).count()
            status_distribution[status_code] = {
                'label': status_label,
                'count': count
            }
        
        # Payment method distribution
        payment_methods = queryset.values('payment_method').annotate(
            count=Count('id'),
            revenue=Sum('total_amount')
        ).order_by('-count')
        
        return {
            'total_orders': stats['total_orders'] or 0,
            'total_revenue': float(stats['total_revenue'] or 0),
            'average_order_value': float(stats['average_order_value'] or 0),
            'status_distribution': status_distribution,
            'payment_methods': list(payment_methods),
            'currency': 'HTG'
        }
    
    @staticmethod
    def get_order_summary(order) -> Dict[str, Any]:
        """Get comprehensive order summary"""
        return {
            'order_number': order.order_number,
            'status': order.status,
            'status_display': order.get_status_display(),
            'payment_status': order.payment_status,
            'payment_method': order.payment_method,
            'customer': {
                'name': order.customer_name,
                'email': order.customer_email,
                'phone': order.customer_phone
            },
            'shipping': {
                'address': order.shipping_address,
                'city': order.shipping_city,
                'country': order.shipping_country
            },
            'items': [
                {
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'total_price': float(item.total_price),
                    'product_image': item.product_image,
                    'options': item.product_options
                }
                for item in order.items.all()
            ],
            'totals': {
                'subtotal': float(order.subtotal),
                'shipping_cost': float(order.shipping_cost),
                'tax_amount': float(order.tax_amount),
                'discount_amount': float(order.discount_amount),
                'total_amount': float(order.total_amount),
                'currency': order.currency
            },
            'dates': {
                'created_at': order.created_at,
                'estimated_delivery': order.estimated_delivery,
                'delivered_at': order.delivered_at
            },
            'tracking': {
                'tracking_number': order.tracking_number,
                'shipping_method': order.shipping_method
            }
        }
    
    @staticmethod
    def _handle_status_change(order, old_status: str, new_status: str):
        """Handle actions when order status changes"""
        from .email_service import EmailService
        
        # Send notifications based on status change
        if new_status == 'confirmed':
            EmailService.send_order_confirmation(order)
        elif new_status == 'shipped':
            EmailService.send_shipping_notification(order)
        elif new_status == 'delivered':
            EmailService.send_delivery_confirmation(order)
        
        logger.info(f"Order {order.order_number} status changed from {old_status} to {new_status}")
    
    @staticmethod
    def generate_invoice_data(order) -> Dict[str, Any]:
        """Generate invoice data for order"""
        return {
            'order': order,
            'company': {
                'name': 'Afèpanou',
                'address': 'Port-au-Prince, Haïti',
                'email': 'contact@afepanou.com',
                'phone': '+509 XX XX XXXX'
            },
            'invoice_number': f"INV-{order.order_number}",
            'invoice_date': order.created_at.date(),
            'due_date': order.created_at.date(),  # Immediate payment
            'items': order.items.all(),
            'totals': {
                'subtotal': order.subtotal,
                'shipping': order.shipping_cost,
                'tax': order.tax_amount,
                'discount': order.discount_amount,
                'total': order.total_amount
            }
        }