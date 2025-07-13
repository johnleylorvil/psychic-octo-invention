# ======================================
# apps/payments/serializers.py
# ======================================

from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'moncash_order_id', 'order_number',
            'amount', 'currency', 'status', 'payment_method',
            'reference_number', 'transaction_date', 'verified_at',
            'failure_reason', 'created_at'
        ]
        read_only_fields = [
            'transaction_id', 'moncash_order_id', 'status', 'payment_method',
            'reference_number', 'transaction_date', 'verified_at', 'created_at'
        ]


class CreatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    return_url = serializers.URLField(required=False)
    callback_url = serializers.URLField(required=False)
    
    def validate_order_id(self, value):
        from orders.models import Order
        try:
            order = Order.objects.get(id=value)
            if order.payment_status == 'paid':
                raise serializers.ValidationError("Cette commande est déjà payée.")
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Commande non trouvée.")


class VerifyPaymentSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(required=False)
    order_id = serializers.CharField(required=False)
    
    def validate(self, data):
        if not data.get('transaction_id') and not data.get('order_id'):
            raise serializers.ValidationError(
                "Au moins un des champs 'transaction_id' ou 'order_id' est requis."
            )
        return data
