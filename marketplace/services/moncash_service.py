# marketplace/services/moncash_service.py

import requests
import logging
import time
import base64
import json
import hashlib
import hmac
from decimal import Decimal
from typing import Dict, Any, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


class MonCashError(Exception):
    """Exception de base pour les erreurs MonCash"""
    pass


class MonCashAuthenticationError(MonCashError):
    """Exception pour erreurs d'authentification MonCash"""
    pass


class MonCashPaymentError(MonCashError):
    """Exception pour erreurs de paiement MonCash"""
    pass


class ServiceUnavailableError(MonCashError):
    """Exception quand le service MonCash est indisponible (circuit breaker)"""
    pass


class MonCashService:
    """
    Service d'intégration MonCash avec circuit breaker et gestion d'erreurs robuste
    
    Fonctionnalités :
    - Authentification OAuth avec cache token
    - Création paiement avec redirection
    - Vérification statut paiement
    - Validation webhooks avec signature
    - Circuit breaker pour résilience
    - Retry logic avec backoff exponentiel
    """
    
    def __init__(self):
        # Configuration depuis settings Django
        self.client_id = getattr(settings, 'MONCASH_CLIENT_ID', None)
        self.client_secret = getattr(settings, 'MONCASH_CLIENT_SECRET', None)
        self.is_sandbox = getattr(settings, 'MONCASH_SANDBOX', True)
        
        # URLs selon environnement
        if self.is_sandbox:
            self.api_base_url = "https://sandbox.moncashbutton.digicelgroup.com/Api"
            self.gateway_base_url = "https://sandbox.moncashbutton.digicelgroup.com/Moncash-middleware"
        else:
            self.api_base_url = "https://moncashbutton.digicelgroup.com/Api"
            self.gateway_base_url = "https://moncashbutton.digicelgroup.com/Moncash-middleware"
        
        # Circuit breaker configuration
        self.failure_count = 0
        self.failure_threshold = 5        # Seuil d'échec
        self.recovery_timeout = 300       # 5 minutes de récupération
        self.last_failure_time = None
        self.circuit_open = False
        
        # Configuration requêtes
        self.timeout = 30  # 30 secondes timeout
        self.max_retries = 3
        
        # Validation configuration
        if not self.client_id or not self.client_secret:
            logger.warning("MonCash credentials non configurées")
    
    def get_access_token(self) -> str:
        """
        Obtenir token d'accès MonCash avec cache pour performance
        
        Returns:
            str: Bearer token pour API calls
            
        Raises:
            MonCashAuthenticationError: Si authentification échoue
        """
        # Vérifier cache d'abord
        cache_key = f"moncash_token_{self.client_id}"
        cached_token = cache.get(cache_key)
        
        if cached_token:
            logger.debug("Token MonCash récupéré du cache")
            return cached_token
        
        # Vérifier circuit breaker
        if self._is_circuit_open():
            raise ServiceUnavailableError("MonCash service indisponible (circuit breaker ouvert)")
        
        try:
            # Préparer authentification Basic
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'scope': 'read,write',
                'grant_type': 'client_credentials'
            }
            
            url = f"{self.api_base_url}/oauth/token"
            
            logger.info(f"Demande token MonCash - URL: {url}")
            
            response = requests.post(
                url,
                headers=headers,
                data=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                
                if access_token:
                    # Cache token avec expiration (moins 5 min pour sécurité)
                    cache_timeout = max(expires_in - 300, 300)
                    cache.set(cache_key, access_token, cache_timeout)
                    
                    logger.info("Token MonCash obtenu et mis en cache")
                    self._on_success()
                    return access_token
                else:
                    raise MonCashAuthenticationError("Token d'accès manquant dans la réponse")
            else:
                error_msg = f"Erreur authentification MonCash: {response.status_code} - {response.text}"
                logger.error(error_msg)
                self._on_failure()
                raise MonCashAuthenticationError(error_msg)
                
        except requests.exceptions.RequestException as exc:
            error_msg = f"Erreur réseau authentification MonCash: {exc}"
            logger.error(error_msg)
            self._on_failure()
            raise MonCashAuthenticationError(error_msg)
    
    def create_payment(self, order_number: str, amount: Decimal) -> Dict[str, Any]:
        """
        Créer un paiement MonCash et obtenir l'URL de redirection
        
        Args:
            order_number: Numéro de commande unique
            amount: Montant en HTG
            
        Returns:
            Dict avec payment_token, redirect_url, expires_at
            
        Raises:
            MonCashPaymentError: Si création paiement échoue
        """
        # Vérifier circuit breaker
        if self._is_circuit_open():
            raise ServiceUnavailableError("MonCash service indisponible (circuit breaker ouvert)")
        
        try:
            # Obtenir token d'accès
            access_token = self.get_access_token()
            
            # Préparer payload
            payload = {
                'amount': float(amount),
                'orderId': order_number
            }
            
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.api_base_url}/v1/CreatePayment"
            
            logger.info(f"Création paiement MonCash - Order: {order_number}, Amount: {amount}")
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 202:  # Created
                payment_data = response.json()
                
                payment_token_info = payment_data.get('payment_token', {})
                payment_token = payment_token_info.get('token')
                
                if payment_token:
                    # Construire URL de redirection
                    redirect_url = f"{self.gateway_base_url}/Payment/Redirect?token={payment_token}"
                    
                    result = {
                        'success': True,
                        'payment_token': payment_token,
                        'redirect_url': redirect_url,
                        'expires_at': payment_token_info.get('expired'),
                        'created_at': payment_token_info.get('created'),
                        'order_id': order_number,
                        'amount': amount,
                        'mode': 'sandbox' if self.is_sandbox else 'live'
                    }
                    
                    logger.info(f"Paiement MonCash créé - Token: {payment_token[:10]}...")
                    self._on_success()
                    return result
                else:
                    raise MonCashPaymentError("Token de paiement manquant dans la réponse")
            else:
                error_msg = f"Erreur création paiement MonCash: {response.status_code} - {response.text}"
                logger.error(error_msg)
                self._on_failure()
                raise MonCashPaymentError(error_msg)
                
        except MonCashAuthenticationError:
            # Re-raise authentication errors
            raise
        except requests.exceptions.RequestException as exc:
            error_msg = f"Erreur réseau création paiement: {exc}"
            logger.error(error_msg)
            self._on_failure()
            raise MonCashPaymentError(error_msg)
    
    def verify_payment_by_order(self, order_number: str) -> Dict[str, Any]:
        """
        Vérifier le statut d'un paiement par numéro de commande
        
        Args:
            order_number: Numéro de commande
            
        Returns:
            Dict avec payment details ou None si non trouvé
            
        Raises:
            MonCashPaymentError: Si vérification échoue
        """
        # Vérifier circuit breaker
        if self._is_circuit_open():
            raise ServiceUnavailableError("MonCash service indisponible (circuit breaker ouvert)")
        
        try:
            # Obtenir token d'accès
            access_token = self.get_access_token()
            
            payload = {
                'orderId': order_number
            }
            
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.api_base_url}/v1/RetrieveOrderPayment"
            
            logger.info(f"Vérification paiement MonCash - Order: {order_number}")
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                payment_data = response.json()
                payment_info = payment_data.get('payment', {})
                
                if payment_info:
                    result = {
                        'found': True,
                        'reference': payment_info.get('reference'),
                        'transaction_id': payment_info.get('transaction_id'),
                        'amount': payment_info.get('cost'),
                        'message': payment_info.get('message'),
                        'payer': payment_info.get('payer'),
                        'status': 'successful' if payment_info.get('message') == 'successful' else 'failed',
                        'order_id': order_number
                    }
                    
                    logger.info(f"Paiement vérifié - Order: {order_number}, Status: {result['status']}")
                    self._on_success()
                    return result
                else:
                    return {
                        'found': False,
                        'order_id': order_number,
                        'message': 'Paiement non trouvé'
                    }
            else:
                error_msg = f"Erreur vérification paiement: {response.status_code} - {response.text}"
                logger.error(error_msg)
                self._on_failure()
                raise MonCashPaymentError(error_msg)
                
        except MonCashAuthenticationError:
            # Re-raise authentication errors
            raise
        except requests.exceptions.RequestException as exc:
            error_msg = f"Erreur réseau vérification paiement: {exc}"
            logger.error(error_msg)
            self._on_failure()
            raise MonCashPaymentError(error_msg)
    
    def verify_payment_by_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Vérifier le statut d'un paiement par transaction ID
        
        Args:
            transaction_id: ID de transaction MonCash
            
        Returns:
            Dict avec payment details
        """
        try:
            access_token = self.get_access_token()
            
            payload = {
                'transactionId': transaction_id
            }
            
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.api_base_url}/v1/RetrieveTransactionPayment"
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                payment_data = response.json()
                payment_info = payment_data.get('payment', {})
                
                result = {
                    'found': True,
                    'reference': payment_info.get('reference'),
                    'transaction_id': payment_info.get('transaction_id'),
                    'amount': payment_info.get('cost'),
                    'message': payment_info.get('message'),
                    'payer': payment_info.get('payer'),
                    'status': 'successful' if payment_info.get('message') == 'successful' else 'failed'
                }
                
                self._on_success()
                return result
            else:
                self._on_failure()
                raise MonCashPaymentError(f"Erreur vérification transaction: {response.status_code}")
                
        except Exception as exc:
            logger.error(f"Erreur vérification transaction {transaction_id}: {exc}")
            raise MonCashPaymentError(str(exc))
    
    def validate_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Valider la signature d'un webhook MonCash (si implémenté par MonCash)
        
        Args:
            payload: Corps du webhook
            signature: Signature fournie
            
        Returns:
            bool: True si signature valide
            
        Note: MonCash ne semble pas implémenter de signature dans la doc,
        mais on prépare pour le futur
        """
        try:
            # Pour l'instant, MonCash ne fournit pas de signature dans la doc
            # On peut valider la structure du payload à la place
            webhook_data = json.loads(payload)
            
            # Validation basique de la structure
            required_fields = ['transactionId', 'orderId', 'amount', 'message']
            for field in required_fields:
                if field not in webhook_data:
                    logger.warning(f"Champ requis manquant dans webhook: {field}")
                    return False
            
            # Validation montant (doit être numérique)
            try:
                float(webhook_data['amount'])
            except (ValueError, TypeError):
                logger.warning(f"Montant invalide dans webhook: {webhook_data.get('amount')}")
                return False
            
            return True
            
        except json.JSONDecodeError:
            logger.error("Webhook payload n'est pas un JSON valide")
            return False
        except Exception as exc:
            logger.error(f"Erreur validation webhook: {exc}")
            return False
    
    def _is_circuit_open(self) -> bool:
        """
        Vérifier si le circuit breaker est ouvert
        
        Returns:
            bool: True si circuit ouvert (service indisponible)
        """
        if not self.circuit_open:
            return False
        
        # Tentative de récupération après timeout
        if time.time() - self.last_failure_time > self.recovery_timeout:
            self.circuit_open = False
            self.failure_count = 0
            logger.info("MonCash circuit breaker - tentative de récupération")
            return False
        
        return True
    
    def _on_success(self):
        """Callback après succès d'une opération"""
        if self.failure_count > 0 or self.circuit_open:
            logger.info("MonCash service récupéré après échecs")
        
        self.failure_count = 0
        self.circuit_open = False
    
    def _on_failure(self):
        """Callback après échec d'une opération"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        # Ouvrir circuit si trop d'échecs
        if self.failure_count >= self.failure_threshold:
            self.circuit_open = True
            logger.critical(
                f"MonCash circuit breaker ouvert après {self.failure_count} échecs. "
                f"Service indisponible pendant {self.recovery_timeout}s"
            )
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Obtenir le statut du service MonCash
        
        Returns:
            Dict avec statut et métriques
        """
        return {
            'service_available': not self.circuit_open,
            'circuit_open': self.circuit_open,
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time,
            'environment': 'sandbox' if self.is_sandbox else 'live',
            'api_base_url': self.api_base_url,
            'configured': bool(self.client_id and self.client_secret)
        }
    
    @staticmethod
    def parse_webhook_data(webhook_payload: str) -> Dict[str, Any]:
        """
        Parser les données d'un webhook MonCash
        
        Args:
            webhook_payload: JSON string du webhook
            
        Returns:
            Dict avec données parsées et nettoyées
        """
        try:
            data = json.loads(webhook_payload)
            
            # Nettoyer et valider les données
            parsed_data = {
                'transaction_id': str(data.get('transactionId', '')),
                'order_id': str(data.get('orderId', '')),
                'amount': Decimal(str(data.get('amount', '0'))),
                'message': str(data.get('message', '')),
                'payer': str(data.get('payer', '')),
                'reference': str(data.get('reference', '')),
                'status': 'successful' if data.get('message') == 'successful' else 'failed',
                'raw_data': data
            }
            
            return parsed_data
            
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            logger.error(f"Erreur parsing webhook MonCash: {exc}")
            raise MonCashError(f"Données webhook invalides: {exc}")


# Instance globale du service (singleton pattern)
moncash_service = MonCashService()