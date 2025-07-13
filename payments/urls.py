# ======================================
# apps/payments/urls.py
# ======================================

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # MonCash
    path('moncash/create/', views.create_payment, name='moncash-create'),
    path('moncash/verify/', views.verify_payment, name='moncash-verify'),
    path('moncash/webhook/', views.moncash_webhook, name='moncash-webhook'),
    
    # Transactions
    path('transactions/', views.user_transactions, name='user-transactions'),
    path('transactions/<int:transaction_id>/', views.transaction_detail, name='transaction-detail'),
]