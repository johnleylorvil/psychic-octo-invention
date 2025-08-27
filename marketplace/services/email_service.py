# marketplace/services/email_service.py
"""
Email notification service for Afèpanou marketplace
"""

from typing import Dict, Any, List, Optional
import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from marketplace.models import Order, Product, Newsletter

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailService:
    """Service for email notifications and marketing"""
    
    @staticmethod
    def send_welcome_email(user: User) -> bool:
        """Send welcome email to new users"""
        try:
            subject = "Byenveni nan Afèpanou! Welcome to Afèpanou!"
            
            context = {
                'user': user,
                'site_name': 'Afèpanou',
                'site_url': settings.SITE_URL,
            }
            
            # Render HTML and text versions
            html_content = render_to_string('emails/welcome.html', context)
            text_content = render_to_string('emails/welcome.txt', context)
            
            return EmailService._send_email(
                subject=subject,
                recipient_list=[user.email],
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {e}")
            return False
    
    @staticmethod
    def send_order_confirmation(order: Order) -> bool:
        """Send order confirmation email"""
        try:
            subject = f"Konfimation Kòmand ou yo #{order.order_number} - Order Confirmation"
            
            context = {
                'order': order,
                'user': order.user,
                'site_name': 'Afèpanou',
                'site_url': settings.SITE_URL,
                'order_url': f"{settings.SITE_URL}/orders/{order.id}/",
            }
            
            html_content = render_to_string('emails/order_confirmation.html', context)
            text_content = render_to_string('emails/order_confirmation.txt', context)
            
            return EmailService._send_email(
                subject=subject,
                recipient_list=[order.email],
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send order confirmation for order {order.id}: {e}")
            return False
    
    @staticmethod
    def send_order_status_update(order: Order, new_status: str, notes: str = '') -> bool:
        """Send order status update email"""
        try:
            status_messages = {
                'confirmed': 'Kòmand ou yo konfirm - Your order has been confirmed',
                'processing': 'N ap prepare kòmand ou yo - Your order is being prepared',
                'shipped': 'Kòmand ou yo voye - Your order has been shipped',
                'delivered': 'Kòmand ou yo rive - Your order has been delivered',
                'cancelled': 'Kòmand ou yo anile - Your order has been cancelled'
            }
            
            subject = f"Mizajou Kòmand #{order.order_number} - {status_messages.get(new_status, 'Order Update')}"
            
            context = {
                'order': order,
                'user': order.user,
                'new_status': new_status,
                'status_message': status_messages.get(new_status),
                'notes': notes,
                'site_name': 'Afèpanou',
                'site_url': settings.SITE_URL,
                'order_url': f"{settings.SITE_URL}/orders/{order.id}/",
            }
            
            html_content = render_to_string('emails/order_status_update.html', context)
            text_content = render_to_string('emails/order_status_update.txt', context)
            
            return EmailService._send_email(
                subject=subject,
                recipient_list=[order.email],
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send status update for order {order.id}: {e}")
            return False
    
    @staticmethod
    def send_payment_confirmation(order: Order, transaction_id: str) -> bool:
        """Send payment confirmation email"""
        try:
            subject = f"Konfimation Peman #{order.order_number} - Payment Confirmed"
            
            context = {
                'order': order,
                'user': order.user,
                'transaction_id': transaction_id,
                'site_name': 'Afèpanou',
                'site_url': settings.SITE_URL,
                'order_url': f"{settings.SITE_URL}/orders/{order.id}/",
            }
            
            html_content = render_to_string('emails/payment_confirmation.html', context)
            text_content = render_to_string('emails/payment_confirmation.txt', context)
            
            return EmailService._send_email(
                subject=subject,
                recipient_list=[order.email],
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send payment confirmation for order {order.id}: {e}")
            return False
    
    @staticmethod
    def send_low_stock_alert(product: Product, seller: User) -> bool:
        """Send low stock alert to seller"""
        try:
            subject = f"Ale Stock Alert - {product.name} Low Stock"
            
            context = {
                'product': product,
                'seller': seller,
                'site_name': 'Afèpanou',
                'site_url': settings.SITE_URL,
                'product_url': f"{settings.SITE_URL}/seller/products/{product.id}/",
            }
            
            html_content = render_to_string('emails/low_stock_alert.html', context)
            text_content = render_to_string('emails/low_stock_alert.txt', context)
            
            return EmailService._send_email(
                subject=subject,
                recipient_list=[seller.email],
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send low stock alert for product {product.id}: {e}")
            return False
    
    @staticmethod
    def send_new_seller_welcome(seller: User) -> bool:
        """Send welcome email to new sellers"""
        try:
            subject = "Byenveni nan Afèpanou Seller Program!"
            
            context = {
                'seller': seller,
                'site_name': 'Afèpanou',
                'site_url': settings.SITE_URL,
                'seller_dashboard_url': f"{settings.SITE_URL}/seller/dashboard/",
            }
            
            html_content = render_to_string('emails/seller_welcome.html', context)
            text_content = render_to_string('emails/seller_welcome.txt', context)
            
            return EmailService._send_email(
                subject=subject,
                recipient_list=[seller.email],
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send seller welcome email to {seller.email}: {e}")
            return False
    
    @staticmethod
    def send_password_reset(user: User, reset_token: str) -> bool:
        """Send password reset email"""
        try:
            subject = "Reset mo de pas ou yo - Password Reset Request"
            
            context = {
                'user': user,
                'reset_token': reset_token,
                'site_name': 'Afèpanou',
                'site_url': settings.SITE_URL,
                'reset_url': f"{settings.SITE_URL}/auth/reset-password/{reset_token}/",
            }
            
            html_content = render_to_string('emails/password_reset.html', context)
            text_content = render_to_string('emails/password_reset.txt', context)
            
            return EmailService._send_email(
                subject=subject,
                recipient_list=[user.email],
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {e}")
            return False
    
    @staticmethod
    def send_newsletter(subject: str, content: str, html_content: str = None,
                       recipient_list: List[str] = None) -> Dict[str, Any]:
        """Send newsletter to subscribers"""
        try:
            if not recipient_list:
                # Get all active newsletter subscribers
                subscribers = Newsletter.objects.filter(is_active=True)
                recipient_list = [sub.email for sub in subscribers]
            
            if not recipient_list:
                return {'success': False, 'error': 'No recipients found'}
            
            success_count = 0
            failed_count = 0
            
            # Send in batches to avoid overwhelming the email service
            batch_size = 50
            for i in range(0, len(recipient_list), batch_size):
                batch = recipient_list[i:i + batch_size]
                
                try:
                    if EmailService._send_email(
                        subject=subject,
                        recipient_list=batch,
                        html_content=html_content,
                        text_content=content,
                        bcc=True
                    ):
                        success_count += len(batch)
                    else:
                        failed_count += len(batch)
                        
                except Exception as e:
                    logger.error(f"Failed to send newsletter batch: {e}")
                    failed_count += len(batch)
            
            return {
                'success': True,
                'sent': success_count,
                'failed': failed_count,
                'total': len(recipient_list)
            }
            
        except Exception as e:
            logger.error(f"Newsletter sending failed: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def send_review_request(order: Order) -> bool:
        """Send review request email after order delivery"""
        try:
            subject = "Kite yon review - Share your experience"
            
            context = {
                'order': order,
                'user': order.user,
                'site_name': 'Afèpanou',
                'site_url': settings.SITE_URL,
                'review_url': f"{settings.SITE_URL}/orders/{order.id}/review/",
            }
            
            html_content = render_to_string('emails/review_request.html', context)
            text_content = render_to_string('emails/review_request.txt', context)
            
            return EmailService._send_email(
                subject=subject,
                recipient_list=[order.email],
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Failed to send review request for order {order.id}: {e}")
            return False
    
    @staticmethod
    def _send_email(subject: str, recipient_list: List[str], 
                   html_content: str = None, text_content: str = None,
                   from_email: str = None, bcc: bool = False) -> bool:
        """Internal method to send emails"""
        try:
            if not from_email:
                from_email = f"Afèpanou <{settings.DEFAULT_FROM_EMAIL}>"
            
            if html_content and text_content:
                # Send multipart email
                if bcc:
                    # Use BCC for newsletter-type emails
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_content,
                        from_email=from_email,
                        bcc=recipient_list
                    )
                else:
                    msg = EmailMultiAlternatives(
                        subject=subject,
                        body=text_content,
                        from_email=from_email,
                        to=recipient_list
                    )
                
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                
            else:
                # Send plain text email
                content = html_content or text_content
                if bcc:
                    send_mail(
                        subject=subject,
                        message=content,
                        from_email=from_email,
                        recipient_list=[],
                        bcc=recipient_list,
                        html_message=html_content
                    )
                else:
                    send_mail(
                        subject=subject,
                        message=content,
                        from_email=from_email,
                        recipient_list=recipient_list,
                        html_message=html_content
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    
    @staticmethod
    def subscribe_to_newsletter(email: str, user: User = None) -> Dict[str, Any]:
        """Subscribe email to newsletter"""
        try:
            subscriber, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={
                    'user': user,
                    'is_active': True
                }
            )
            
            if not created and not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save()
            
            # Send welcome newsletter email
            if created:
                EmailService._send_email(
                    subject="Byenveni nan Newsletter Afèpanou!",
                    recipient_list=[email],
                    text_content="Thank you for subscribing to our newsletter!"
                )
            
            return {
                'success': True,
                'created': created,
                'message': 'Successfully subscribed to newsletter'
            }
            
        except Exception as e:
            logger.error(f"Newsletter subscription failed: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def unsubscribe_from_newsletter(email: str) -> bool:
        """Unsubscribe email from newsletter"""
        try:
            Newsletter.objects.filter(email=email).update(is_active=False)
            return True
        except Exception as e:
            logger.error(f"Newsletter unsubscription failed: {e}")
            return False