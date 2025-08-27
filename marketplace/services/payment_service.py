# marketplace/services/payment_service.py
"""
Payment processing service for MonCash integration
"""

from typing import Dict, Any, Optional
from decimal import Decimal
import requests
import logging
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from marketplace.models import Order, Transaction

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for payment processing with MonCash"""
    
    MONCASH_BASE_URL = "https://sandbox.digicelgroup.com"  # Use production URL for live
    
    TRANSACTION_STATUSES = [
        'pending',
        'processing', 
        'completed',
        'failed',
        'cancelled',
        'refunded'
    ]
    
    @staticmethod
    def get_moncash_access_token() -> Optional[str]:
        """Get MonCash OAuth2 access token"""
        try:
            url = f"{PaymentService.MONCASH_BASE_URL}/Api/oauth/token"
            
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': settings.MONCASH_CLIENT_ID,
                'client_secret': settings.MONCASH_CLIENT_SECRET,
                'scope': 'read,write'
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data.get('access_token')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get MonCash access token: {e}")
            return None
    
    @staticmethod
    def create_payment(order: Order) -> Optional[Dict[str, Any]]:
        """Create payment request with MonCash"""
        try:
            access_token = PaymentService.get_moncash_access_token()
            if not access_token:
                raise ValidationError("Failed to authenticate with MonCash")
            
            # Create transaction record
            transaction = Transaction.objects.create(
                order=order,
                amount=order.total_amount,
                currency='HTG',
                payment_method='moncash',
                status='pending',
                external_transaction_id='',  # Will be updated after MonCash response
                metadata={
                    'order_id': order.id,
                    'user_id': order.user.id if order.user else None,
                    'created_via': 'api'
                }
            )
            
            url = f"{PaymentService.MONCASH_BASE_URL}/Api/v1/CreatePayment"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            payment_data = {
                'amount': str(order.total_amount),
                'orderId': str(order.order_number),
                'returnUrl': f"{settings.SITE_URL}/payment/success/",
                'cancelUrl': f"{settings.SITE_URL}/payment/cancel/",
                'notifyUrl': f"{settings.SITE_URL}/api/v1/payments/moncash/webhook/",
                'mode': 'redirect'  # or 'direct' for API-only
            }
            
            response = requests.post(url, json=payment_data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Update transaction with MonCash response
            transaction.external_transaction_id = result.get('payment_token', '')
            transaction.gateway_response = result
            transaction.status = 'processing'
            transaction.save()
            
            return {
                'transaction': transaction,
                'payment_url': result.get('redirectUrl'),
                'payment_token': result.get('payment_token'),
                'success': True
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MonCash payment creation failed: {e}")
            if 'transaction' in locals():
                transaction.status = 'failed'
                transaction.failure_reason = str(e)
                transaction.save()
            
            return {
                'success': False,
                'error': 'Payment service temporarily unavailable'
            }
        
        except Exception as e:
            logger.error(f"Payment creation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def verify_payment(transaction_id: str) -> Dict[str, Any]:
        """Verify payment status with MonCash"""
        try:
            access_token = PaymentService.get_moncash_access_token()
            if not access_token:
                return {'success': False, 'error': 'Authentication failed'}
            
            transaction = Transaction.objects.get(
                external_transaction_id=transaction_id
            )
            
            url = f"{PaymentService.MONCASH_BASE_URL}/Api/v1/RetrieveTransactionPayment"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            data = {'transactionId': transaction_id}
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Update transaction based on MonCash response
            payment_status = result.get('status', '').lower()
            
            if payment_status == 'successful':
                transaction.status = 'completed'
                transaction.completed_at = timezone.now()
                
                # Update order payment status
                order = transaction.order
                order.payment_status = 'paid'
                order.save(update_fields=['payment_status'])
                
            elif payment_status in ['failed', 'cancelled']:
                transaction.status = 'failed'
                transaction.failure_reason = result.get('message', 'Payment failed')
                
            transaction.gateway_response = result
            transaction.save()
            
            return {
                'success': True,
                'transaction': transaction,
                'payment_status': payment_status,
                'details': result
            }
            
        except Transaction.DoesNotExist:
            return {'success': False, 'error': 'Transaction not found'}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Payment verification failed: {e}")
            return {'success': False, 'error': 'Verification service unavailable'}
        
        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def handle_webhook(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process MonCash webhook notifications"""
        try:
            transaction_id = webhook_data.get('transactionId')
            if not transaction_id:
                return {'success': False, 'error': 'Missing transaction ID'}
            
            # Verify the webhook signature (if implemented by MonCash)
            # webhook_signature = webhook_data.get('signature')
            # if not PaymentService._verify_webhook_signature(webhook_data, webhook_signature):
            #     return {'success': False, 'error': 'Invalid signature'}
            
            # Find transaction
            try:
                transaction = Transaction.objects.get(
                    external_transaction_id=transaction_id
                )
            except Transaction.DoesNotExist:
                logger.warning(f"Webhook received for unknown transaction: {transaction_id}")
                return {'success': False, 'error': 'Transaction not found'}
            
            # Update transaction status
            status = webhook_data.get('status', '').lower()
            amount = webhook_data.get('amount')
            
            with transaction.atomic():
                if status == 'successful' and amount == str(transaction.amount):
                    transaction.status = 'completed'
                    transaction.completed_at = timezone.now()
                    
                    # Update order
                    order = transaction.order
                    order.payment_status = 'paid'
                    order.save(update_fields=['payment_status'])
                    
                    # TODO: Send payment confirmation email
                    
                elif status in ['failed', 'cancelled']:
                    transaction.status = 'failed'
                    transaction.failure_reason = webhook_data.get('message', 'Payment failed')
                
                # Store webhook data
                transaction.webhook_data = webhook_data
                transaction.save()
            
            return {'success': True, 'message': 'Webhook processed successfully'}
            
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def refund_payment(transaction: Transaction, amount: Optional[Decimal] = None,
                      reason: str = '') -> Dict[str, Any]:
        """Process payment refund through MonCash"""
        try:
            if transaction.status != 'completed':
                return {'success': False, 'error': 'Cannot refund incomplete payment'}
            
            refund_amount = amount or transaction.amount
            if refund_amount > transaction.amount:
                return {'success': False, 'error': 'Refund amount exceeds original payment'}
            
            access_token = PaymentService.get_moncash_access_token()
            if not access_token:
                return {'success': False, 'error': 'Authentication failed'}
            
            # Create refund request
            url = f"{PaymentService.MONCASH_BASE_URL}/Api/v1/Refund"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            refund_data = {
                'transactionId': transaction.external_transaction_id,
                'amount': str(refund_amount),
                'reason': reason
            }
            
            response = requests.post(url, json=refund_data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Create refund transaction record
            refund_transaction = Transaction.objects.create(
                order=transaction.order,
                parent_transaction=transaction,
                amount=-refund_amount,  # Negative for refund
                currency=transaction.currency,
                payment_method='moncash',
                status='completed' if result.get('status') == 'successful' else 'failed',
                external_transaction_id=result.get('refundId', ''),
                gateway_response=result,
                metadata={
                    'refund_reason': reason,
                    'original_transaction_id': transaction.id
                }
            )
            
            # Update original transaction
            transaction.is_refunded = True
            transaction.refund_amount = refund_amount
            transaction.save()
            
            # Update order if full refund
            if refund_amount == transaction.amount:
                order = transaction.order
                order.payment_status = 'refunded'
                order.save(update_fields=['payment_status'])
            
            return {
                'success': True,
                'refund_transaction': refund_transaction,
                'refund_id': result.get('refundId'),
                'details': result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Payment refund failed: {e}")
            return {'success': False, 'error': 'Refund service unavailable'}
        
        except Exception as e:
            logger.error(f"Refund error: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_transaction_history(order: Order) -> List[Transaction]:
        """Get all transactions for an order"""
        return list(
            Transaction.objects.filter(order=order)
            .order_by('-created_at')
        )
    
    @staticmethod
    def get_payment_analytics(date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Get payment analytics"""
        transactions = Transaction.objects.all()
        
        if date_from:
            transactions = transactions.filter(created_at__date__gte=date_from)
        
        if date_to:
            transactions = transactions.filter(created_at__date__lte=date_to)
        
        completed = transactions.filter(status='completed', amount__gt=0)
        failed = transactions.filter(status='failed')
        refunds = transactions.filter(status='completed', amount__lt=0)
        
        return {
            'total_transactions': transactions.count(),
            'successful_payments': completed.count(),
            'failed_payments': failed.count(),
            'total_refunds': refunds.count(),
            'total_revenue': sum(t.amount for t in completed),
            'total_refunded': abs(sum(t.amount for t in refunds)),
            'success_rate': (
                (completed.count() / transactions.count() * 100)
                if transactions.count() > 0 else 0
            )
        }