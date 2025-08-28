# marketplace/views/payment.py
"""
Payment integration views for MonCash and other payment methods
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import json
import logging

from ..models import Order, Transaction
from ..services import PaymentService, EmailService, OrderService

logger = logging.getLogger(__name__)


@login_required
def payment_initiate(request, order_id):
    """Initiate payment process"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order is in correct state for payment
    if order.payment_status != 'pending':
        messages.error(request, _('This order cannot be paid.'))
        return redirect('order_detail', order_id=order.id)
    
    payment_method = request.GET.get('method', 'moncash')
    
    if payment_method == 'moncash':
        return initiate_moncash_payment(request, order)
    elif payment_method == 'cash_on_delivery':
        return handle_cash_on_delivery(request, order)
    else:
        messages.error(request, _('Invalid payment method.'))
        return redirect('order_detail', order_id=order.id)


def initiate_moncash_payment(request, order):
    """Initiate MonCash payment"""
    try:
        # Create payment with MonCash
        payment_result = PaymentService.create_payment(order)
        
        if payment_result['success']:
            # Redirect to MonCash
            return redirect(payment_result['payment_url'])
        else:
            messages.error(request, payment_result['error'])
            return redirect('order_detail', order_id=order.id)
            
    except Exception as e:
        logger.error(f"MonCash payment initiation failed: {e}")
        messages.error(request, _('Payment service is temporarily unavailable.'))
        return redirect('order_detail', order_id=order.id)


def handle_cash_on_delivery(request, order):
    """Handle cash on delivery payment"""
    # Update order to COD
    order.payment_method = 'cash_on_delivery'
    order.payment_status = 'pending'  # Will be marked paid on delivery
    order.save()
    
    # Update order status to confirmed
    OrderService.update_order_status(
        order, 
        'confirmed', 
        'Order confirmed with Cash on Delivery payment',
        request.user
    )
    
    # Send confirmation email
    EmailService.send_order_confirmation(order)
    
    messages.success(request, _('Order confirmed! You will pay cash on delivery.'))
    return redirect('order_detail', order_id=order.id)


def payment_success(request):
    """Payment success callback from MonCash"""
    transaction_id = request.GET.get('transactionId')
    order_id = request.GET.get('orderId')
    
    if not transaction_id:
        messages.error(request, _('Invalid payment response.'))
        return redirect('order_history')
    
    try:
        # Verify payment with MonCash
        verification_result = PaymentService.verify_payment(transaction_id)
        
        if verification_result['success']:
            transaction = verification_result['transaction']
            order = transaction.order
            
            # Check if payment was successful
            if verification_result['payment_status'] == 'successful':
                # Send confirmation email
                EmailService.send_payment_confirmation(order, transaction_id)
                
                # Update order status
                OrderService.update_order_status(
                    order,
                    'confirmed',
                    'Payment received via MonCash'
                )
                
                messages.success(request, _('Payment completed successfully!'))
                return redirect('order_detail', order_id=order.id)
            else:
                messages.error(request, _('Payment was not successful.'))
        else:
            messages.error(request, _('Payment verification failed.'))
    
    except Exception as e:
        logger.error(f"Payment success handling failed: {e}")
        messages.error(request, _('An error occurred while processing your payment.'))
    
    return redirect('order_history')


def payment_cancel(request):
    """Payment cancellation callback from MonCash"""
    order_id = request.GET.get('orderId')
    
    if order_id:
        try:
            order = Order.objects.get(order_number=order_id)
            messages.warning(
                request,
                _('Payment was cancelled. Order #{} is still pending payment.').format(
                    order.order_number
                )
            )
            return redirect('order_detail', order_id=order.id)
        except Order.DoesNotExist:
            pass
    
    messages.warning(request, _('Payment was cancelled.'))
    return redirect('order_history')


@csrf_exempt
@require_POST
def payment_webhook(request):
    """Handle MonCash webhook notifications"""
    try:
        # Get webhook data
        webhook_data = json.loads(request.body)
        
        logger.info(f"MonCash webhook received: {webhook_data}")
        
        # Process webhook
        result = PaymentService.handle_webhook(webhook_data)
        
        if result['success']:
            return HttpResponse('OK', status=200)
        else:
            logger.error(f"Webhook processing failed: {result['error']}")
            return HttpResponse('ERROR', status=400)
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        return HttpResponse('INVALID_JSON', status=400)
    except Exception as e:
        logger.error(f"Webhook handling error: {e}")
        return HttpResponse('ERROR', status=500)


@login_required
def payment_history(request):
    """User payment history"""
    user_orders = Order.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(
        order__in=user_orders
    ).order_by('-created_at')
    
    context = {
        'transactions': transactions,
        'title': _('Payment History')
    }
    
    return render(request, 'account/payment_history.html', context)


@login_required
def payment_receipt(request, transaction_id):
    """Generate payment receipt"""
    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        order__user=request.user
    )
    
    if transaction.status != 'completed':
        messages.error(request, _('Receipt not available for this payment.'))
        return redirect('payment_history')
    
    context = {
        'transaction': transaction,
        'order': transaction.order,
        'title': _('Payment Receipt')
    }
    
    return render(request, 'account/payment_receipt.html', context)


@login_required
def request_refund(request, order_id):
    """Request refund for an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if refund is possible
    if order.payment_status != 'paid':
        messages.error(request, _('Refund not available for this order.'))
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        try:
            # Get the transaction
            transaction = Transaction.objects.get(
                order=order,
                status='completed'
            )
            
            # Process refund
            refund_result = PaymentService.refund_payment(
                transaction,
                reason=reason
            )
            
            if refund_result['success']:
                messages.success(request, _('Refund request has been processed.'))
            else:
                messages.error(request, refund_result['error'])
                
        except Transaction.DoesNotExist:
            messages.error(request, _('No payment record found for this order.'))
        except Exception as e:
            logger.error(f"Refund request failed: {e}")
            messages.error(request, _('Refund request failed. Please contact support.'))
    
    return redirect('order_detail', order_id=order.id)


def payment_status_check(request):
    """AJAX endpoint to check payment status"""
    transaction_id = request.GET.get('transaction_id')
    
    if not transaction_id:
        return JsonResponse({
            'success': False,
            'error': 'Missing transaction ID'
        })
    
    try:
        # Verify payment status
        result = PaymentService.verify_payment(transaction_id)
        
        return JsonResponse({
            'success': result['success'],
            'status': result.get('payment_status', 'unknown'),
            'details': result.get('details', {})
        })
        
    except Exception as e:
        logger.error(f"Payment status check failed: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Status check failed'
        })


@login_required
def payment_retry(request, order_id):
    """Retry failed payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status not in ['pending', 'failed']:
        messages.error(request, _('Payment cannot be retried for this order.'))
        return redirect('order_detail', order_id=order.id)
    
    # Reset payment status
    order.payment_status = 'pending'
    order.save()
    
    messages.info(request, _('You can now retry the payment.'))
    return redirect('payment_initiate', order_id=order.id)