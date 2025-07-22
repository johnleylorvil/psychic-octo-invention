# marketplace/services/moncash_service.py

import requests
import logging
from django.conf import settings
from django.core.cache import cache
from ..models import Order

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)

# Définition d'une exception personnalisée pour les erreurs de l'API MonCash
class MonCashAPIError(Exception):
    """Exception personnalisée pour les erreurs liées à l'API MonCash."""
    pass

class MonCashService:
    """
    Service encapsulant toutes les interactions avec l'API MonCash.
    """
    def __init__(self):
        """Initialise le service avec les configurations de Django."""
        self.client_id = settings.MONCASH_CLIENT_ID
        self.secret_key = settings.MONCASH_SECRET_KEY
        self.api_base_url = settings.MONCASH_API_BASE
        self.gateway_base_url = settings.MONCASH_GATEWAY_BASE
        self.session = requests.Session()  # Utilise une session pour la persistance des connexions

    def _get_auth_token(self) -> str:
        """
        Récupère un token d'authentification OAuth2 auprès de MonCash.
        Le token est mis en cache pour optimiser les appels répétés.
        """
        cache_key = 'moncash_auth_token'
        token = cache.get(cache_key)
        if token:
            return token

        auth_url = f"{self.api_base_url}/oauth/token"
        payload = {'scope': 'read,write', 'grant_type': 'client_credentials'}
        headers = {'Accept': 'application/json'}
        auth = (self.client_id, self.secret_key)

        try:
            response = self.session.post(auth_url, data=payload, headers=headers, auth=auth, timeout=10)
            response.raise_for_status()

            data = response.json()
            access_token = data['access_token']
            expires_in = data.get('expires_in', 59)

            cache.set(cache_key, access_token, timeout=max(10, expires_in - 10))
            logger.info("Nouveau token d'authentification MonCash obtenu et mis en cache.")
            return access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de connexion à l'API MonCash pour obtenir le token: {e}")
            raise MonCashAPIError(f"Impossible de se connecter à MonCash: {e}")
        except KeyError:
            logger.error(f"Réponse invalide de l'endpoint d'authentification MonCash.")
            raise MonCashAPIError("Réponse invalide de l'endpoint d'authentification.")

    def create_payment(self, order: Order) -> str:
        """
        Initie une transaction de paiement auprès de MonCash pour une commande donnée.
        Retourne l'URL de redirection pour le paiement.
        """
        token = self._get_auth_token()
        payment_url = f"{self.api_base_url}/v1/CreatePayment"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            'amount': float(order.total_amount),
            'orderId': order.order_number
        }

        try:
            response = self.session.post(payment_url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            # La doc indique un statut 202 pour une requête acceptée
            if str(data.get('status')) != '202':
                # ✅ CORRECTION: L'indentation ici est maintenant correcte.
                raise MonCashAPIError(f"MonCash n'a pas accepté le paiement. Statut: {data.get('status')}, Réponse: {data}")

            payment_token = data.get('payment_token', {}).get('token')
            if not payment_token:
                raise MonCashAPIError("Token de paiement non trouvé dans la réponse de MonCash.")

            redirect_url = f"{self.gateway_base_url}/Payment/Redirect?token={payment_token}"
            logger.info(f"Paiement MonCash créé avec succès pour la commande {order.order_number}.")
            return redirect_url

        except requests.exceptions.RequestException as e:
            logger.error(f"Échec de la création de paiement MonCash pour la commande {order.order_number}: {e}")
            raise MonCashAPIError(f"Échec de la création de paiement auprès de MonCash: {e}")
    
    def verify_payment(self, transaction_id: str) -> dict:
        """
        Vérifie le statut d'une transaction directement auprès de MonCash.
        C'est une étape de sécurité cruciale pour valider les webhooks.
        """
        token = self._get_auth_token()
        verify_url = f"{self.api_base_url}/v1/RetrieveTransactionPayment"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        payload = {'transactionId': transaction_id}

        try:
            response = self.session.post(verify_url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            payment_details = data.get('payment')
            if not payment_details:
                raise MonCashAPIError(f"Détails de paiement non trouvés pour la transaction {transaction_id}.")
            
            if payment_details.get('message') != 'successful':
                logger.warning(f"Vérification MonCash non réussie pour trans. {transaction_id}: {payment_details.get('message')}")
                return {'verified': False, 'data': payment_details}

            logger.info(f"Transaction MonCash {transaction_id} vérifiée avec succès.")
            return {'verified': True, 'data': payment_details}

        except requests.exceptions.RequestException as e:
            logger.error(f"Échec de la vérification de paiement MonCash pour trans. {transaction_id}: {e}")
            raise MonCashAPIError(f"Échec de la vérification du paiement auprès de MonCash: {e}")