# ======================================
# apps/payments/views.py
# ======================================

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import logging

from orders.models import Order
from .models import Transaction
from .serializers import CreatePaymentSerializer, VerifyPaymentSerializer, TransactionSerializer
from .services import MonCashService

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """
    Créer un paiement MonCash
    POST /api/v1/payments/moncash/create/
    Body: {"order_id": 123, "return_url": "...", "callback_url": "..."}
    """
    serializer = CreatePaymentSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            order_id = serializer.validated_data['order_id']
            order = get_object_or_404(Order, id=order_id, user=request.user)
            
            # Vérifier si une transaction pending existe déjà
            existing_transaction = Transaction.objects.filter(
                order=order,
                status='pending'
            ).first()
            
            if existing_transaction:
                return Response({
                    'success': False,
                    'message': 'Une transaction est déjà en cours pour cette commande.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Créer le paiement MonCash
            moncash_service = MonCashService()
            payment_result = moncash_service.create_payment(
                order=order,
                return_url=serializer.validated_data.get('return_url'),
                callback_url=serializer.validated_data.get('callback_url')
            )
            
            if payment_result['success']:
                return Response({
                    'success': True,
                    'message': 'Paiement créé avec succès',
                    'data': {
                        'transaction_id': payment_result['transaction_id'],
                        'redirect_url': payment_result['redirect_url'],
                        'payment_token': payment_result['payment_token'],
                        'expires_at': payment_result['expires_at']
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Erreur lors de la création du paiement',
                    'error': payment_result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Erreur création paiement: {str(e)}")
            return Response({
                'success': False,
                'message': 'Erreur interne du serveur'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'message': 'Données invalides',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    """
    Vérifier un paiement MonCash
    POST /api/v1/payments/moncash/verify/
    Body: {"transaction_id": "12345"} ou {"order_id": "AF123_abcd1234"}
    """
    serializer = VerifyPaymentSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            moncash_service = MonCashService()
            
            transaction_id = serializer.validated_data.get('transaction_id')
            order_id = serializer.validated_data.get('order_id')
            
            # Vérifier avec MonCash
            if transaction_id:
                payment_info = moncash_service.verify_payment_by_transaction_id(transaction_id)
            else:
                payment_info = moncash_service.verify_payment_by_order_id(order_id)
            
            # Mettre à jour notre transaction
            if 'payment' in payment_info:
                payment_data = payment_info['payment']
                
                # Trouver la transaction correspondante
                if order_id:
                    transaction = Transaction.objects.filter(
                        moncash_order_id=order_id
                    ).first()
                else:
                    transaction = Transaction.objects.filter(
                        transaction_id=transaction_id
                    ).first()
                
                if transaction:
                    # Mettre à jour la transaction
                    transaction.transaction_id = payment_data.get('transaction_id', '')
                    transaction.reference_number = payment_data.get('reference', '')
                    
                    if payment_data.get('message') == 'successful':
                        transaction.status = 'paid'
                        transaction.verified_at = timezone.now()
                        
                        # Mettre à jour la commande
                        if transaction.order:
                            transaction.order.payment_status = 'paid'
                            transaction.order.save()
                    else:
                        transaction.status = 'failed'
                        transaction.failure_reason = payment_data.get('message', '')
                    
                    transaction.gateway_response = payment_info
                    transaction.save()
                    
                    return Response({
                        'success': True,
                        'message': 'Paiement vérifié avec succès',
                        'data': TransactionSerializer(transaction).data
                    })
                else:
                    return Response({
                        'success': False,
                        'message': 'Transaction non trouvée dans notre système'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({
                    'success': False,
                    'message': 'Aucune information de paiement retournée'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Erreur vérification paiement: {str(e)}")
            return Response({
                'success': False,
                'message': 'Erreur lors de la vérification du paiement'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'message': 'Données invalides',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def moncash_webhook(request):
    """
    Webhook MonCash pour notifications de paiement
    POST /api/v1/payments/moncash/webhook/
    """
    try:
        # Log de la réception du webhook
        logger.info(f"Webhook MonCash reçu: {request.body}")
        
        # Traiter les données du webhook
        if request.content_type == 'application/json':
            webhook_data = json.loads(request.body)
        else:
            webhook_data = request.POST.dict()
        
        # Extraire les informations importantes
        transaction_id = webhook_data.get('transactionId')
        order_id = webhook_data.get('orderId')
        status_webhook = webhook_data.get('status')
        
        if transaction_id or order_id:
            # Vérifier le paiement avec MonCash
            moncash_service = MonCashService()
            
            if transaction_id:
                payment_info = moncash_service.verify_payment_by_transaction_id(transaction_id)
            else:
                payment_info = moncash_service.verify_payment_by_order_id(order_id)
            
            # Mettre à jour la transaction
            if 'payment' in payment_info:
                payment_data = payment_info['payment']
                
                # Trouver la transaction
                transaction = None
                if order_id:
                    transaction = Transaction.objects.filter(
                        moncash_order_id=order_id
                    ).first()
                elif transaction_id:
                    transaction = Transaction.objects.filter(
                        transaction_id=transaction_id
                    ).first()
                
                if transaction:
                    transaction.webhook_received_at = timezone.now()
                    transaction.transaction_id = payment_data.get('transaction_id', '')
                    transaction.reference_number = payment_data.get('reference', '')
                    
                    if payment_data.get('message') == 'successful':
                        transaction.status = 'paid'
                        transaction.verified_at = timezone.now()
                        
                        # Mettre à jour la commande
                        if transaction.order:
                            transaction.order.payment_status = 'paid'
                            transaction.order.save()
                    
                    transaction.gateway_response = payment_info
                    transaction.save()
                    
                    logger.info(f"Transaction {transaction.id} mise à jour via webhook")
        
        return HttpResponse("OK", status=200)
        
    except Exception as e:
        logger.error(f"Erreur webhook MonCash: {str(e)}")
        return HttpResponse("Error", status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_transactions(request):
    """
    Récupère les transactions de l'utilisateur
    GET /api/v1/payments/transactions/
    """
    transactions = Transaction.objects.filter(
        order__user=request.user
    ).order_by('-created_at')
    
    serializer = TransactionSerializer(transactions, many=True)
    
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_detail(request, transaction_id):
    """
    Détail d'une transaction
    GET /api/v1/payments/transactions/{transaction_id}/
    """
    transaction = get_object_or_404(
        Transaction, 
        id=transaction_id, 
        order__user=request.user
    )
    
    serializer = TransactionSerializer(transaction)
    
    return Response({
        'success': True,
        'data': serializer.data
    })