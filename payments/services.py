# ======================================
# apps/payments/services.py
# ======================================

import requests
import base64
import uuid
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from .models import Transaction


class MonCashService:
    """Service pour l'intégration MonCash"""
    
    def __init__(self):
        self.client_id = settings.MONCASH_CLIENT_ID
        self.client_secret = settings.MONCASH_SECRET_KEY
        self.mode = settings.MONCASH_MODE  # 'sandbox' ou 'live'
        
        if self.mode == 'sandbox':
            self.api_base = 'https://sandbox.moncashbutton.digicelgroup.com/Api'
            self.gateway_base = 'https://sandbox.moncashbutton.digicelgroup.com/Moncash-middleware'
        else:
            self.api_base = 'https://moncashbutton.digicelgroup.com/Api'
            self.gateway_base = 'https://moncashbutton.digicelgroup.com/Moncash-middleware'
    
    def get_access_token(self):
        """Obtenir le token d'accès MonCash"""
        try:
            # Encoder les credentials en base64
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            url = f"{self.api_base}/oauth/token"
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'scope': 'read,write',
                'grant_type': 'client_credentials'
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            return token_data.get('access_token')
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'obtention du token MonCash: {str(e)}")
    
    def create_payment(self, order, return_url=None, callback_url=None):
        """Créer un paiement MonCash"""
        try:
            access_token = self.get_access_token()
            
            # Générer un orderId unique pour MonCash
            moncash_order_id = f"AF{order.id}_{uuid.uuid4().hex[:8]}"
            
            # URLs par défaut si non fournies
            if not return_url:
                return_url = f"{settings.SITE_URL}/payment/success/"
            if not callback_url:
                callback_url = f"{settings.SITE_URL}/api/v1/payments/moncash/webhook/"
            
            url = f"{self.api_base}/v1/CreatePayment"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'amount': float(order.total_amount),
                'orderId': moncash_order_id
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            payment_data = response.json()
            
            # Créer la transaction dans notre DB
            transaction = Transaction.objects.create(
                order=order,
                moncash_order_id=moncash_order_id,
                payment_token=payment_data['payment_token']['token'],
                amount=order.total_amount,
                currency='HTG',
                status='pending',
                payment_method='moncash',
                gateway_response=payment_data,
                callback_url=callback_url,
                return_url=return_url,
                transaction_date=timezone.now()
            )
            
            # URL de redirection vers MonCash
            redirect_url = f"{self.gateway_base}/Payment/Redirect?token={payment_data['payment_token']['token']}"
            
            return {
                'success': True,
                'transaction_id': transaction.id,
                'payment_token': payment_data['payment_token']['token'],
                'redirect_url': redirect_url,
                'expires_at': payment_data['payment_token']['expired']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment_by_transaction_id(self, transaction_id):
        """Vérifier un paiement par transaction ID MonCash"""
        try:
            access_token = self.get_access_token()
            
            url = f"{self.api_base}/v1/RetrieveTransactionPayment"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'transactionId': transaction_id
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            raise Exception(f"Erreur lors de la vérification du paiement: {str(e)}")
    
    def verify_payment_by_order_id(self, order_id):
        """Vérifier un paiement par order ID MonCash"""
        try:
            access_token = self.get_access_token()
            
            url = f"{self.api_base}/v1/RetrieveOrderPayment"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'orderId': order_id
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            raise Exception(f"Erreur lors de la vérification du paiement: {str(e)}")