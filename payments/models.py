from django.db import models


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    moncash_order_id = models.CharField(max_length=100, blank=True)
    payment_token = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, blank=True, default='HTG')
    status = models.CharField(max_length=20, blank=True, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, default='moncash')
    gateway_response = models.JSONField(null=True, blank=True)
    failure_reason = models.TextField(null=True, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    callback_url = models.CharField(max_length=255, blank=True)
    return_url = models.CharField(max_length=255, blank=True)
    webhook_received_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'transactions'

    def __str__(self):
        return f'Transaction {self.id}'

