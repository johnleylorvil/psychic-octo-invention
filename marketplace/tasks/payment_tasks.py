# marketplace/tasks/payment_tasks.py

from celery import shared_task
from django.db import transaction
import logging

from ..models import Order, Transaction
from ..services.moncash_service import MonCashService, MonCashAPIError

logger = logging.getLogger(__name__)

@shared_task(
    bind=True, 
    autoretry_for=(MonCashAPIError, Exception), 
    retry_kwargs={'max_retries': 3, 'countdown': 60}
)
def process_payment_webhook(self, payload: dict):
    """
    Tâche Celery pour traiter un webhook de paiement MonCash de manière asynchrone.
    Cette tâche est conçue pour être idempotente et robuste.
    """
    logger.info(f"Début du traitement du webhook MonCash. Payload: {payload}")
    
    # 1. Extraire les informations nécessaires du payload
    # La structure exacte du webhook n'est pas documentée, nous nous basons sur une structure probable.
    # La VRAIE validation se fera en appelant l'API MonCash.
    transaction_id = payload.get('transactionId') or payload.get('transaction_id')
    order_id_from_payload = payload.get('orderId') or payload.get('order_id')

    if not transaction_id:
        logger.error("Le payload du webhook ne contient pas de transactionId.")
        return "Échec: transactionId manquant dans le payload."

    # 2. Vérifier la transaction auprès de MonCash (source de vérité)
    try:
        moncash_service = MonCashService()
        verification_result = moncash_service.verify_payment(transaction_id)

        if not verification_result.get('verified'):
            logger.warning(f"La vérification MonCash a échoué pour la transaction {transaction_id}. Message: {verification_result.get('data', {}).get('message')}")
            # Pas de nouvelle tentative si la vérification échoue, c'est un statut final.
            return f"Échec de la vérification pour la transaction {transaction_id}."

        verified_data = verification_result['data']
        # 'reference' dans la réponse de vérification est notre 'order_number'
        order_number = verified_data.get('reference')

    except MonCashAPIError as e:
        logger.error(f"Erreur API MonCash lors du traitement du webhook pour la transaction {transaction_id}: {e}")
        # Celery tentera automatiquement de relancer la tâche
        raise self.retry(exc=e)

    # 3. Utiliser une transaction atomique pour garantir l'intégrité de la base de données
    try:
        with transaction.atomic():
            # Verrouiller la ligne de la commande pour éviter les race conditions
            order = Order.objects.select_for_update().get(order_number=order_number)

            # 4. IDEMPOTENCE : Si la commande est déjà payée, on ne fait rien.
            if order.payment_status == 'paid':
                logger.info(f"La commande {order_number} est déjà payée. Traitement du webhook ignoré (idempotence).")
                return f"Commande {order_number} déjà traitée."

            # 5. Mettre à jour le statut de la commande
            order.payment_status = 'paid'
            order.status = 'confirmed'  # La commande passe de 'en attente' à 'confirmée'
            order.save()

            # 6. Créer ou mettre à jour l'enregistrement de la transaction
            Transaction.objects.update_or_create(
                transaction_id=transaction_id,
                defaults={
                    'order': order,
                    'amount': verified_data.get('cost'),
                    'currency': order.currency,
                    'status': 'completed',
                    'payment_method': 'moncash',
                    'gateway_response': verified_data,  # Stocker la réponse complète de l'API pour audit
                    'reference_number': verified_data.get('reference')
                }
            )

        logger.info(f"Le webhook pour la commande {order_number} a été traité avec succès. Statut mis à jour.")
        return f"Commande {order_number} traitée avec succès."

    except Order.DoesNotExist:
        logger.error(f"La commande {order_number} de la transaction {transaction_id} n'a pas été trouvée dans la base de données.")
        return f"Échec: Commande {order_number} non trouvée."
    except Exception as e:
        logger.critical(f"Erreur inattendue lors de la mise à jour de la commande {order_number}: {e}")
        raise self.retry(exc=e)