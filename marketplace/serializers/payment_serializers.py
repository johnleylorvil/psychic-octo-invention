# marketplace/serializers/payment_serializers.py

import logging
from rest_framework import serializers
from ..models import Order, Transaction

logger = logging.getLogger(__name__)

# =================================================================
# SERIALIZER POUR L'INITIATION DU PAIEMENT
# =================================================================

class InitiatePaymentSerializer(serializers.Serializer):
    """
    Valide la requête pour initier un paiement.
    Assure que la commande existe et est prête pour le paiement.
    """
    order_number = serializers.CharField(
        max_length=50,
        required=True,
        help_text="Le numéro unique de la commande à payer."
    )

    def validate_order_number(self, value):
        """
        Vérifie l'existence et le statut de la commande.
        """
        try:
            order = Order.objects.get(order_number=value)
            
            # Vérifier si la commande est bien en attente de paiement
            if order.status != 'pending':
                raise serializers.ValidationError(
                    f"La commande {value} n'est pas en attente de paiement (statut actuel: {order.status})."
                )
            
            # Vérifier si la commande n'a pas déjà été payée
            if order.payment_status == 'paid':
                raise serializers.ValidationError(
                    f"La commande {value} a déjà été payée."
                )

        except Order.DoesNotExist:
            logger.warning(f"Tentative de paiement pour une commande inexistante: {value}")
            raise serializers.ValidationError(f"La commande avec le numéro {value} n'existe pas.")
        
        return value

# =================================================================
# SERIALIZER POUR LA RÉPONSE DE STATUT DE PAIEMENT
# =================================================================

class PaymentStatusSerializer(serializers.ModelSerializer):
    """
    Formate la réponse pour l'endpoint de vérification de statut.
    Expose les informations clés d'une transaction de manière sécurisée.
    """
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'transaction_id',
            'order_number',
            'amount',
            'currency',
            'status',
            'payment_method',
            'transaction_date',
            'failure_reason'
        ]
        help_text = "Détails d'une transaction de paiement."

# =================================================================
# SERIALIZER POUR LE PAYLOAD DU WEBHOOK (Optionnel mais recommandé)
# =================================================================

class MonCashWebhookPayloadSerializer(serializers.Serializer):
    """
    Valide la structure de base du payload envoyé par le webhook de MonCash.
    Ceci est une première couche de validation avant le traitement asynchrone.
    """
    transactionId = serializers.IntegerField(required=True)
    orderId = serializers.CharField(required=True)
    # Ajoutez d'autres champs si MonCash en envoie que vous souhaitez valider
    
    class Meta:
        fields = ['transactionId', 'orderId']