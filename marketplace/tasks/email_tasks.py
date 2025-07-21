# marketplace/tasks/email_tasks.py

import logging
from celery import shared_task
from django.core.mail import send_mail, mail_admins
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from ..models import Order, Product, User

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes entre retries
    time_limit=120,           # 2 minutes max par email
)
def send_order_confirmation_email(self, order_id):
    """
    Envoyer email de confirmation de commande
    
    Args:
        order_id: ID de la commande
        
    Returns:
        Dict avec status du traitement
    """
    try:
        # Récupérer commande avec relations
        order = Order.objects.select_related('user').prefetch_related(
            'items__product'
        ).get(id=order_id)
        
        # Préparer données email
        context = {
            'order': order,
            'customer_name': order.customer_name,
            'order_number': order.order_number,
            'total_amount': order.total_amount,
            'currency': order.currency,
            'items': order.items.all(),
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
        }
        
        # Rendu template email
        subject = f"Confirmation de commande {order.order_number} - {settings.SITE_NAME}"
        
        # Email HTML (optionnel)
        html_message = render_to_string('emails/order_confirmation.html', context)
        
        # Email texte (fallback)
        plain_message = f"""
        Bonjour {order.customer_name},
        
        Votre commande {order.order_number} a été confirmée avec succès !
        
        Détails de la commande :
        - Numéro : {order.order_number}
        - Montant total : {order.total_amount} {order.currency}
        - Statut : {order.get_status_display()}
        
        Articles commandés :
        {chr(10).join([f"- {item.product_name} x{item.quantity} = {item.total_price} {order.currency}" for item in order.items.all()])}
        
        Adresse de livraison :
        {order.shipping_address}
        {order.shipping_city}, {order.shipping_country}
        
        Nous vous tiendrons informé de l'évolution de votre commande.
        
        Merci de votre confiance !
        L'équipe {settings.SITE_NAME}
        """
        
        # Envoi email
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            fail_silently=False
        )
        
        logger.info(f"Email confirmation sent for order {order.order_number}")
        
        return {
            'status': 'success',
            'order_number': order.order_number,
            'customer_email': order.customer_email,
            'message': 'Email confirmation envoyé avec succès'
        }
        
    except Order.DoesNotExist:
        error_msg = f"Order {order_id} not found for email confirmation"
        logger.error(error_msg)
        return {
            'status': 'failed',
            'error': 'order_not_found',
            'message': error_msg
        }
        
    except Exception as exc:
        logger.error(f"Error sending order confirmation email for order {order_id}: {exc}")
        
        # Retry pour erreurs temporaires
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying email send - Attempt {self.request.retries + 1}")
            raise self.retry(exc=exc)
        
        return {
            'status': 'failed',
            'error': 'email_send_failed',
            'message': str(exc),
            'max_retries_reached': True
        }


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=600,  # 10 minutes entre retries
    time_limit=60,
)
def send_low_stock_alert_email(self, product_id, current_stock):
    """
    Envoyer alerte email pour stock bas
    
    Args:
        product_id: ID du produit
        current_stock: Stock actuel
        
    Returns:
        Dict avec status du traitement
    """
    try:
        product = Product.objects.select_related('category', 'seller').get(id=product_id)
        
        # Préparer données alerte
        context = {
            'product': product,
            'current_stock': current_stock,
            'min_stock_alert': product.min_stock_alert,
            'category': product.category.name,
            'seller': product.seller.get_full_name() or product.seller.username,
            'admin_url': f"{settings.SITE_URL}/admin/marketplace/product/{product.id}/change/",
            'site_name': settings.SITE_NAME,
        }
        
        subject = f"🚨 ALERTE STOCK BAS - {product.name}"
        
        message = f"""
        ALERTE STOCK BAS pour le produit :
        
        Produit : {product.name} ({product.slug})
        Stock actuel : {current_stock}
        Seuil d'alerte : {product.min_stock_alert}
        Catégorie : {product.category.name}
        Vendeur : {context['seller']}
        
        Action recommandée : Réapprovisionner le stock
        
        Lien admin : {context['admin_url']}
        
        Timestamp : {timezone.now()}
        """
        
        # Envoyer aux admins
        mail_admins(
            subject=subject,
            message=message,
            fail_silently=False
        )
        
        logger.warning(f"Low stock alert sent for {product.slug} - Stock: {current_stock}")
        
        return {
            'status': 'success',
            'product_slug': product.slug,
            'current_stock': current_stock,
            'message': 'Alerte stock bas envoyée aux admins'
        }
        
    except Product.DoesNotExist:
        error_msg = f"Product {product_id} not found for low stock alert"
        logger.error(error_msg)
        return {
            'status': 'failed',
            'error': 'product_not_found',
            'message': error_msg
        }
        
    except Exception as exc:
        logger.error(f"Error sending low stock alert for product {product_id}: {exc}")
        
        # Retry pour erreurs temporaires
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        return {
            'status': 'failed',
            'error': 'email_send_failed',
            'message': str(exc)
        }


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=180,  # 3 minutes entre retries
    time_limit=90,
)
def send_order_status_update_email(self, order_id, old_status, new_status):
    """
    Envoyer email de mise à jour statut commande
    
    Args:
        order_id: ID de la commande
        old_status: Ancien statut
        new_status: Nouveau statut
        
    Returns:
        Dict avec status du traitement
    """
    try:
        order = Order.objects.get(id=order_id)
        
        # Messages selon le statut
        status_messages = {
            'confirmed': 'Votre commande a été confirmée et est en cours de préparation.',
            'processing': 'Votre commande est en cours de traitement.',
            'shipped': 'Votre commande a été expédiée !',
            'delivered': 'Votre commande a été livrée avec succès.',
            'cancelled': 'Votre commande a été annulée.',
        }
        
        status_message = status_messages.get(new_status, f'Statut mis à jour vers: {new_status}')
        
        subject = f"Mise à jour commande {order.order_number} - {settings.SITE_NAME}"
        
        message = f"""
        Bonjour {order.customer_name},
        
        Le statut de votre commande {order.order_number} a été mis à jour :
        
        Ancien statut : {old_status}
        Nouveau statut : {new_status}
        
        {status_message}
        
        Détails de la commande :
        - Montant : {order.total_amount} {order.currency}
        - Date : {order.created_at.strftime('%d/%m/%Y')}
        
        {f"Numéro de suivi : {order.tracking_number}" if order.tracking_number else ""}
        {f"Livraison estimée : {order.estimated_delivery.strftime('%d/%m/%Y')}" if order.estimated_delivery else ""}
        
        Pour toute question, contactez-nous à {settings.CONTACT_EMAIL}
        
        Merci de votre confiance !
        L'équipe {settings.SITE_NAME}
        """
        
        # Envoi email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            fail_silently=False
        )
        
        logger.info(f"Status update email sent for order {order.order_number}: {old_status} → {new_status}")
        
        return {
            'status': 'success',
            'order_number': order.order_number,
            'old_status': old_status,
            'new_status': new_status,
            'message': 'Email de mise à jour envoyé'
        }
        
    except Order.DoesNotExist:
        error_msg = f"Order {order_id} not found for status update email"
        logger.error(error_msg)
        return {
            'status': 'failed',
            'error': 'order_not_found',
            'message': error_msg
        }
        
    except Exception as exc:
        logger.error(f"Error sending status update email for order {order_id}: {exc}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        return {
            'status': 'failed',
            'error': 'email_send_failed', 
            'message': str(exc)
        }


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=300,
    time_limit=60,
)
def send_welcome_email(self, user_id):
    """
    Envoyer email de bienvenue aux nouveaux utilisateurs
    
    Args:
        user_id: ID de l'utilisateur
        
    Returns:
        Dict avec status du traitement
    """
    try:
        user = User.objects.get(id=user_id)
        
        subject = f"Bienvenue sur {settings.SITE_NAME} !"
        
        message = f"""
        Bonjour {user.first_name or user.username},
        
        Bienvenue sur {settings.SITE_NAME} - {settings.SITE_TAGLINE} !
        
        Votre compte a été créé avec succès. Vous pouvez maintenant :
        - Parcourir notre catalogue de produits locaux
        - Passer des commandes en toute sécurité
        - Suivre vos commandes en temps réel
        
        Nos catégories principales :
        - Produits de Première Nécessité
        - Produits Patriotiques et Artisanaux  
        - Produits Locaux Authentiques
        
        Visitez notre site : {settings.SITE_URL}
        
        Pour toute question : {settings.CONTACT_EMAIL}
        Support : {getattr(settings, 'SUPPORT_PHONE', 'N/A')}
        
        Merci de votre confiance et bon shopping !
        L'équipe {settings.SITE_NAME}
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        logger.info(f"Welcome email sent to user {user.username} ({user.email})")
        
        return {
            'status': 'success',
            'user_id': user_id,
            'email': user.email,
            'message': 'Email de bienvenue envoyé'
        }
        
    except User.DoesNotExist:
        error_msg = f"User {user_id} not found for welcome email"
        logger.error(error_msg)
        return {
            'status': 'failed',
            'error': 'user_not_found',
            'message': error_msg
        }
        
    except Exception as exc:
        logger.error(f"Error sending welcome email to user {user_id}: {exc}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        return {
            'status': 'failed',
            'error': 'email_send_failed',
            'message': str(exc)
        }


@shared_task(
    bind=True,
    max_retries=1,
    default_retry_delay=600,
    time_limit=300,  # 5 minutes pour traitement batch
)
def send_newsletter_email(self, subject, message, recipient_list=None):
    """
    Envoyer newsletter ou email en masse
    
    Args:
        subject: Sujet de l'email
        message: Contenu du message
        recipient_list: Liste d'emails (None = tous les abonnés)
        
    Returns:
        Dict avec status du traitement
    """
    try:
        from ..models import NewsletterSubscriber
        
        # Récupérer destinataires
        if recipient_list is None:
            subscribers = NewsletterSubscriber.objects.filter(is_active=True)
            recipient_list = list(subscribers.values_list('email', flat=True))
        
        if not recipient_list:
            return {
                'status': 'success',
                'recipients_count': 0,
                'message': 'Aucun destinataire trouvé'
            }
        
        # Limiter à 100 emails par batch pour éviter spam
        if len(recipient_list) > 100:
            recipient_list = recipient_list[:100]
            logger.warning(f"Newsletter limited to 100 recipients for safety")
        
        # Envoyer email
        send_mail(
            subject=f"{subject} - {settings.SITE_NAME}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False
        )
        
        logger.info(f"Newsletter sent to {len(recipient_list)} recipients")
        
        return {
            'status': 'success',
            'recipients_count': len(recipient_list),
            'subject': subject,
            'message': 'Newsletter envoyée avec succès'
        }
        
    except Exception as exc:
        logger.error(f"Error sending newsletter: {exc}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        
        return {
            'status': 'failed',
            'error': 'newsletter_send_failed',
            'message': str(exc)
        }