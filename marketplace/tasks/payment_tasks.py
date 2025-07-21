# marketplace/tasks/payment_tasks.py

import logging
from celery import shared_task
from celery.exceptions import Retry
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.core.mail import mail_admins
from django.conf import settings
from datetime import timedelta
from ..models import Transaction, Order, Cart
from ..services.moncash_service import (
    MonCashService, 
    MonCashError, 
    ServiceUnavailableError,
    moncash_service
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,                    # 🚨 LIMITE STRICTE - max 3 tentatives
    default_retry_delay=60,           # 🚨 60 secondes entre retries
    retry_backoff=True,               # 🚨 Exponential backoff (60s, 120s, 240s)
    retry_backoff_max=600,            # 🚨 Max 10 minutes de délai
    retry_jitter=True,                # 🚨 Randomisation pour éviter thundering herd
    time_limit=300,                   # 🚨 Limite 5 minutes par tâche
    soft_time_limit=240               # 🚨 Warning à 4 minutes
)
def process_payment_webhook(self, webhook_data):
    """
    Traiter webhook MonCash avec protection contre boucles infinies
    
    Args:
        webhook_data: Dict avec données du webhook MonCash
        
    Returns:
        Dict avec status et détails du traitement
        
    ⚠️ SÉCURITÉ CRITIQUE :
    - Max 3 retries avec exponential backoff
    - Idempotence stricte (pas de double traitement)
    - SELECT FOR UPDATE pour éviter race conditions
    - Gestion d'erreurs différenciée (retry vs fail définitif)
    """
    task_id = self.request.id
    transaction_id = webhook_data.get('transactionId', 'unknown')
    order_id = webhook_data.get('orderId', 'unknown')
    
    logger.info(
        f"🔄 Processing payment webhook - Task: {task_id}, "
        f"Transaction: {transaction_id}, Order: {order_id}, "
        f"Retry: {self.request.retries}/{self.max_retries}"
    )
    
    try:
        # 🚨 VÉRIFICATION IDEMPOTENCE CRITIQUE
        # Empêche le double traitement même en cas de retry
        with transaction.atomic():
            existing_transaction = Transaction.objects.filter(
                moncash_order_id=transaction_id
            ).first()
            
            if existing_transaction and existing_transaction.status == 'completed':
                logger.info(
                    f"✅ Transaction {transaction_id} already processed - SKIPPING"
                )
                return {
                    'status': 'already_processed',
                    'transaction_id': transaction_id,
                    'existing_status': existing_transaction.status,
                    'skip_reason': 'idempotence_check'
                }
        
        # 🎯 VALIDATION DONNÉES WEBHOOK
        try:
            # Utiliser le service MonCash pour parser et valider
            parsed_data = MonCashService.parse_webhook_data(
                webhook_data if isinstance(webhook_data, str) else str(webhook_data)
            )
            
            if not moncash_service.validate_webhook_signature(
                str(webhook_data), 
                ""  # MonCash ne fournit pas de signature selon la doc
            ):
                logger.error(f"❌ Invalid webhook signature for transaction {transaction_id}")
                # 🚨 PAS DE RETRY pour erreurs de validation
                return {
                    'status': 'failed',
                    'error': 'invalid_webhook_signature',
                    'transaction_id': transaction_id
                }
                
        except MonCashError as exc:
            logger.error(f"❌ Webhook data validation failed: {exc}")
            # 🚨 PAS DE RETRY pour erreurs de données
            return {
                'status': 'failed',
                'error': 'invalid_webhook_data',
                'details': str(exc)
            }
        
        # 🎯 TRAITEMENT BUSINESS LOGIC ATOMIQUE
        result = _process_webhook_business_logic(parsed_data, task_id)
        
        logger.info(
            f"✅ Webhook processed successfully - Transaction: {transaction_id}, "
            f"Result: {result['status']}"
        )
        
        return result
        
    except (ConnectionError, TimeoutError, ServiceUnavailableError) as exc:
        # 🚨 RETRY SEULEMENT pour erreurs réseau/service temporaires
        logger.warning(
            f"⚠️ Network/service error processing webhook - Transaction: {transaction_id}, "
            f"Retry {self.request.retries}/{self.max_retries}: {exc}"
        )
        
        # Vérifier si on a atteint le max de retries
        if self.request.retries >= self.max_retries:
            logger.critical(
                f"💥 Payment webhook FAILED after {self.max_retries} retries - "
                f"Transaction: {transaction_id}, Error: {exc}"
            )
            
            # Alerter les admins pour intervention manuelle
            _send_admin_alert_webhook_failure(webhook_data, exc, self.max_retries)
            
            return {
                'status': 'failed_permanently',
                'error': 'max_retries_exceeded',
                'transaction_id': transaction_id,
                'final_error': str(exc)
            }
        
        # 🔄 RETRY avec exponential backoff
        raise self.retry(exc=exc)
        
    except (ValueError, TypeError, KeyError, IntegrityError) as exc:
        # 🚨 PAS DE RETRY pour erreurs de données/logique
        logger.error(
            f"❌ Data/logic error processing webhook - NO RETRY - "
            f"Transaction: {transaction_id}: {exc}"
        )
        
        return {
            'status': 'failed',
            'error': 'data_logic_error',
            'transaction_id': transaction_id,
            'details': str(exc)
        }
        
    except Exception as exc:
        # 🚨 Erreurs inattendues = retry limité puis fail
        logger.error(
            f"❌ Unexpected error processing webhook - Transaction: {transaction_id}: {exc}"
        )
        
        if self.request.retries >= self.max_retries:
            logger.critical(
                f"💥 Payment webhook FAILED with unexpected error after {self.max_retries} retries - "
                f"Transaction: {transaction_id}"
            )
            
            _send_admin_alert_webhook_failure(webhook_data, exc, self.max_retries)
            
            return {
                'status': 'failed_permanently',
                'error': 'unexpected_error',
                'transaction_id': transaction_id,
                'details': str(exc)
            }
        
        raise self.retry(exc=exc)


def _process_webhook_business_logic(parsed_data, task_id):
    """
    Logique métier pour traiter un webhook avec protection atomique
    
    Args:
        parsed_data: Données webhook parsées et validées
        task_id: ID de la tâche Celery pour logging
        
    Returns:
        Dict avec résultat du traitement
    """
    transaction_id = parsed_data['transaction_id']
    order_id = parsed_data['order_id']
    
    # 🚨 VERROU ATOMIQUE pour éviter race conditions
    with transaction.atomic():
        try:
            # SELECT FOR UPDATE pour lock exclusif
            transaction_obj = Transaction.objects.select_for_update().get(
                moncash_order_id=transaction_id
            )
            
        except Transaction.DoesNotExist:
            logger.error(f"❌ Transaction {transaction_id} not found in database")
            return {
                'status': 'transaction_not_found',
                'transaction_id': transaction_id,
                'order_id': order_id
            }
        
        # 🚨 VÉRIFICATION ÉTAT avant traitement
        if transaction_obj.status != 'pending':
            logger.info(
                f"ℹ️ Transaction {transaction_id} already in state {transaction_obj.status} - skipping"
            )
            return {
                'status': 'already_processed',
                'transaction_id': transaction_id,
                'current_status': transaction_obj.status,
                'order_number': transaction_obj.order.order_number if transaction_obj.order else None
            }
        
        # 🎯 MISE À JOUR TRANSACTION
        if parsed_data['status'] == 'successful':
            transaction_obj.status = 'completed'
            transaction_obj.verified_at = timezone.now()
            transaction_obj.reference_number = parsed_data.get('reference', '')
            
            # Sauvegarder gateway response complète pour audit
            transaction_obj.gateway_response = parsed_data['raw_data']
            transaction_obj.webhook_received_at = timezone.now()
            transaction_obj.save()
            
            # 🎯 MISE À JOUR ORDER
            if transaction_obj.order:
                order = transaction_obj.order
                order.payment_status = 'paid'
                order.status = 'confirmed'
                order.admin_notes = f"Paiement confirmé par webhook le {timezone.now()}"
                order.save()
                
                logger.info(
                    f"✅ Order {order.order_number} marked as paid - "
                    f"Amount: {transaction_obj.amount} {transaction_obj.currency}"
                )
                
                return {
                    'status': 'success',
                    'transaction_id': transaction_id,
                    'order_number': order.order_number,
                    'amount': str(transaction_obj.amount),
                    'currency': transaction_obj.currency,
                    'payment_confirmed': True
                }
            else:
                logger.warning(f"⚠️ Transaction {transaction_id} has no associated order")
                return {
                    'status': 'success_no_order',
                    'transaction_id': transaction_id,
                    'amount': str(transaction_obj.amount)
                }
        else:
            # Paiement échoué
            transaction_obj.status = 'failed'
            transaction_obj.failure_reason = parsed_data.get('message', 'Payment failed')
            transaction_obj.gateway_response = parsed_data['raw_data']
            transaction_obj.webhook_received_at = timezone.now()
            transaction_obj.save()
            
            # Marquer order comme échec paiement
            if transaction_obj.order:
                order = transaction_obj.order
                order.payment_status = 'failed'
                order.admin_notes = f"Paiement échoué le {timezone.now()}: {parsed_data.get('message', 'Unknown error')}"
                order.save()
                
                logger.warning(
                    f"⚠️ Payment failed for order {order.order_number} - "
                    f"Reason: {parsed_data.get('message', 'Unknown')}"
                )
            
            return {
                'status': 'payment_failed',
                'transaction_id': transaction_id,
                'order_number': transaction_obj.order.order_number if transaction_obj.order else None,
                'failure_reason': parsed_data.get('message', 'Payment failed')
            }


@shared_task(
    bind=True,
    max_retries=1,                    # 🚨 MAX 1 retry pour nettoyage
    default_retry_delay=300,          # 🚨 5 minutes entre retries
    time_limit=600,                   # 🚨 Max 10 minutes
)
def cleanup_expired_carts(self):
    """
    Nettoyage paniers expirés - LIMITE STRICTE pour éviter surcharge
    
    ⚠️ SÉCURITÉ :
    - Max 1000 paniers par exécution
    - Soft delete (is_active=False) au lieu de suppression
    - Limite de temps stricte
    """
    try:
        cutoff_time = timezone.now()
        
        # Trouver paniers expirés
        expired_carts = Cart.objects.filter(
            expires_at__lt=cutoff_time,
            is_active=True
        )
        
        count = expired_carts.count()
        
        if count == 0:
            logger.info("🧹 No expired carts to cleanup")
            return {'status': 'success', 'cleaned_count': 0}
        
        # 🚨 PROTECTION contre suppression massive
        if count > 1000:
            logger.warning(
                f"⚠️ Too many expired carts ({count}) - limiting to 1000 for safety"
            )
            expired_carts = expired_carts[:1000]
            count = 1000
        
        # Soft delete pour préserver historique
        updated = expired_carts.update(
            is_active=False,
            updated_at=timezone.now()
        )
        
        logger.info(f"🧹 Cleaned up {updated} expired carts")
        
        return {
            'status': 'success',
            'cleaned_count': updated,
            'cutoff_time': cutoff_time.isoformat()
        }
        
    except Exception as exc:
        logger.error(f"❌ Cart cleanup failed: {exc}")
        
        # 🚨 PAS DE RETRY automatique pour éviter surcharge
        # Les admins recevront une alerte via monitoring
        return {
            'status': 'failed',
            'error': str(exc),
            'retry_count': self.request.retries
        }


@shared_task(
    bind=True,
    max_retries=2,                    # 🚨 Max 2 retries pour monitoring
    default_retry_delay=120,          # 🚨 2 minutes entre retries
    time_limit=180,                   # 🚨 Max 3 minutes
)
def monitor_stuck_payments(self):
    """
    Monitoring des paiements bloqués - SANS RETRY automatique sur business logic
    
    Détecte :
    - Transactions pending depuis plus de 1h
    - Orders avec payment_status incohérent
    - Webhooks manqués
    """
    try:
        cutoff_time = timezone.now() - timedelta(hours=1)
        
        # Transactions bloquées en pending
        stuck_transactions = Transaction.objects.filter(
            status='pending',
            created_at__lt=cutoff_time
        ).select_related('order')
        
        stuck_count = stuck_transactions.count()
        
        if stuck_count > 0:
            logger.warning(f"⚠️ Found {stuck_count} stuck payment transactions")
            
            # Préparer détails pour alerte admin
            stuck_details = []
            for trans in stuck_transactions[:10]:  # Limite à 10 pour alerte
                stuck_details.append({
                    'transaction_id': trans.transaction_id,
                    'order_number': trans.order.order_number if trans.order else None,
                    'amount': str(trans.amount),
                    'created_at': trans.created_at.isoformat(),
                    'age_hours': (timezone.now() - trans.created_at).total_seconds() / 3600
                })
            
            # 🚨 ALERTE ADMIN sans retry automatique
            _send_admin_alert_stuck_payments(stuck_details, stuck_count)
            
            return {
                'status': 'alert_sent',
                'stuck_count': stuck_count,
                'details_sent': len(stuck_details)
            }
        else:
            logger.info("✅ No stuck payments found")
            return {
                'status': 'success',
                'stuck_count': 0,
                'message': 'No stuck payments'
            }
            
    except Exception as exc:
        logger.error(f"❌ Payment monitoring failed: {exc}")
        
        if self.request.retries < self.max_retries:
            logger.info(f"🔄 Retrying payment monitoring - Attempt {self.request.retries + 1}")
            raise self.retry(exc=exc)
        
        # Après max retries, alerter les admins
        _send_admin_alert_monitoring_failure(exc)
        
        return {
            'status': 'failed',
            'error': str(exc),
            'max_retries_reached': True
        }


def _send_admin_alert_webhook_failure(webhook_data, error, max_retries):
    """Envoyer alerte admin pour échec webhook critique"""
    try:
        subject = "🚨 CRITICAL: MonCash Webhook Processing Failed"
        
        message = f"""
        ALERTE CRITIQUE : Échec traitement webhook MonCash après {max_retries} tentatives
        
        Détails webhook :
        - Transaction ID: {webhook_data.get('transactionId', 'Unknown')}
        - Order ID: {webhook_data.get('orderId', 'Unknown')}
        - Montant: {webhook_data.get('amount', 'Unknown')}
        - Message: {webhook_data.get('message', 'Unknown')}
        
        Erreur finale : {error}
        
        ACTION REQUISE :
        1. Vérifier statut paiement dans MonCash Business Portal
        2. Réconcilier manuellement si nécessaire
        3. Contacter support MonCash si problème persiste
        
        Données complètes webhook :
        {webhook_data}
        """
        
        mail_admins(subject, message, fail_silently=False)
        logger.critical(f"Admin alert sent for webhook failure: {webhook_data.get('transactionId')}")
        
    except Exception as exc:
        logger.error(f"Failed to send admin alert for webhook failure: {exc}")


def _send_admin_alert_stuck_payments(stuck_details, total_count):
    """Envoyer alerte admin pour paiements bloqués"""
    try:
        subject = f"⚠️ WARNING: {total_count} Stuck Payment Transactions Detected"
        
        details_text = "\n".join([
            f"- Transaction {detail['transaction_id']} (Order: {detail['order_number']}) "
            f"Amount: {detail['amount']} HTG - Age: {detail['age_hours']:.1f}h"
            for detail in stuck_details
        ])
        
        message = f"""
        Détection de {total_count} transactions de paiement bloquées depuis plus d'1 heure.
        
        Détails (10 premiers) :
        {details_text}
        
        Actions recommandées :
        1. Vérifier statut dans MonCash Business Portal
        2. Relancer webhooks manqués si nécessaire
        3. Investiguer problèmes de connectivité
        
        Dashboard admin : {settings.SITE_URL}/admin/marketplace/transaction/
        """
        
        mail_admins(subject, message, fail_silently=False)
        logger.warning(f"Admin alert sent for {total_count} stuck payments")
        
    except Exception as exc:
        logger.error(f"Failed to send stuck payments alert: {exc}")


def _send_admin_alert_monitoring_failure(error):
    """Envoyer alerte admin pour échec monitoring"""
    try:
        subject = "🚨 ERROR: Payment Monitoring System Failed"
        
        message = f"""
        Le système de monitoring des paiements a échoué.
        
        Erreur : {error}
        Timestamp : {timezone.now()}
        
        Le monitoring automatique est temporairement indisponible.
        Vérification manuelle recommandée.
        """
        
        mail_admins(subject, message, fail_silently=False)
        
    except Exception as exc:
        logger.error(f"Failed to send monitoring failure alert: {exc}")