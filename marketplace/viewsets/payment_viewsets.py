# marketplace/viewsets/payment_viewsets.py

import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..models import Order, Transaction
from ..serializers.payment_serializers import InitiatePaymentSerializer, PaymentStatusSerializer
from ..services.moncash_service import MonCashService, MonCashAPIError
from ..tasks.payment_tasks import process_payment_webhook

logger = logging.getLogger(__name__)

class PaymentViewSet(viewsets.ViewSet):
    """
    ViewSet pour la gestion du processus de paiement avec MonCash.
    - `initiate`: Pour démarrer un paiement.
    - `webhook`: Pour recevoir les notifications de MonCash.
    - `status`: Pour vérifier l'état d'une transaction.
    """
    
    def get_permissions(self):
        """
        Définit les permissions requises pour chaque action.
        Le webhook doit être public pour être accessible par MonCash.
        """
        if self.action == 'process_webhook':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='initiate')
    def initiate_payment(self, request):
        """
        Endpoint pour initier un paiement pour une commande donnée.
        POST /api/payments/initiate/
        Payload: { "order_number": "AF12345678" }
        """
        serializer = InitiatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_number = serializer.validated_data['order_number']
        
        try:
            # S'assurer que la commande appartient bien à l'utilisateur connecté
            order = get_object_or_404(Order, order_number=order_number, user=request.user)
            
            # Appeler le service pour créer le paiement et obtenir l'URL de redirection
            moncash_service = MonCashService()
            redirect_url = moncash_service.create_payment(order)

            return Response({'redirect_url': redirect_url}, status=status.HTTP_200_OK)

        except MonCashAPIError as e:
            logger.error(f"Erreur API MonCash pour la commande {order_number}: {e}")
            return Response({'error': 'Erreur de la passerelle de paiement', 'details': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            logger.error(f"Erreur inattendue lors de l'initiation du paiement pour {order_number}: {e}")
            return Response({'error': 'Une erreur inattendue est survenue'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='webhook')
    def process_webhook(self, request):
        """
        Endpoint pour recevoir les notifications (webhooks) de MonCash.
        Doit être extrêmement rapide et déléguer le traitement.
        POST /api/payments/webhook/
        """
        payload = request.data
        logger.info(f"Webhook MonCash reçu: {payload}")

        if not payload:
            return Response({'status': 'error', 'message': 'Payload vide'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Déléguer le traitement lourd à notre tâche Celery
        process_payment_webhook.delay(payload)
        
        # Accuser réception immédiatement auprès de MonCash
        return Response({'status': 'received'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='status')
    def get_payment_status(self, request, pk=None):
        """
        Endpoint pour vérifier le statut d'une transaction dans notre système.
        Le 'pk' correspond au transaction_id.
        GET /api/payments/{transaction_id}/status/
        """
        transaction_id = pk

        try:
            # S'assurer que l'utilisateur ne peut vérifier que ses propres transactions
            transaction = get_object_or_404(
                Transaction,
                transaction_id=transaction_id,
                order__user=request.user
            )
            serializer = PaymentStatusSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut pour la transaction {transaction_id}: {e}")
            return Response({'error': 'Transaction non trouvée ou erreur inattendue.'}, status=status.HTTP_404_NOT_FOUND)