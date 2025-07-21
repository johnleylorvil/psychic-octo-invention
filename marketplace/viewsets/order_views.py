# marketplace/viewsets/order_viewsets.py

import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from ..models import Order, OrderItem, OrderStatusHistory, Cart, User
from ..serializers.order_serializers import (
    OrderSerializer,
    OrderListSerializer,
    CreateOrderFromCartSerializer,
    OrderCancelSerializer,
    OrderStatusUpdateSerializer,
    OrderSummarySerializer
)
from ..services.order_service import OrderService, OrderError, CartEmptyError
from ..services.stock_service import StockService, InsufficientStockError, StockError

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion complète des commandes
    
    Fonctionnalités :
    - Création commande depuis panier avec validation stock
    - Historique commandes utilisateur paginé
    - Détail commande complet avec timeline
    - Annulation commande avec libération stock
    - Mise à jour statuts (admin)
    - Résumé commandes utilisateur
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_number'  # Utiliser order_number au lieu de pk
    
    def get_queryset(self):
        """Récupérer les commandes de l'utilisateur connecté"""
        if self.request.user.is_staff:
            # Admins peuvent voir toutes les commandes
            return Order.objects.all().prefetch_related(
                'items__product__images',
                'items__product__category',
                'status_history__changed_by'
            ).select_related('user')
        else:
            # Utilisateurs voient seulement leurs commandes
            return Order.objects.filter(
                user=self.request.user
            ).prefetch_related(
                'items__product__images',
                'items__product__category',
                'status_history__changed_by'
            )
    
    def get_serializer_class(self):
        """Choisir le serializer selon l'action"""
        if self.action == 'list':
            return OrderListSerializer
        elif self.action == 'create_from_cart':
            return CreateOrderFromCartSerializer
        elif self.action == 'cancel':
            return OrderCancelSerializer
        elif self.action == 'update_status':
            return OrderStatusUpdateSerializer
        return OrderSerializer
    
    def list(self, request):
        """
        Liste des commandes avec pagination et filtres
        
        GET /api/orders/?page=1&status=pending&search=AF12345
        """
        try:
            queryset = self.get_queryset()
            
            # Filtres optionnels
            status_filter = request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            payment_status_filter = request.query_params.get('payment_status')
            if payment_status_filter:
                queryset = queryset.filter(payment_status=payment_status_filter)
            
            search = request.query_params.get('search')
            if search:
                queryset = queryset.filter(
                    order_number__icontains=search
                )
            
            # Tri par défaut (plus récent en premier)
            queryset = queryset.order_by('-created_at')
            
            # Pagination
            page_size = int(request.query_params.get('page_size', 10))
            page_size = min(page_size, 50)  # Limite max
            
            paginator = Paginator(queryset, page_size)
            page = request.query_params.get('page', 1)
            
            try:
                orders = paginator.page(page)
            except PageNotAnInteger:
                orders = paginator.page(1)
            except EmptyPage:
                orders = paginator.page(paginator.num_pages)
            
            # Serializer les commandes
            serializer = self.get_serializer(orders, many=True)
            
            return Response({
                'results': serializer.data,
                'pagination': {
                    'page': orders.number,
                    'page_size': page_size,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': orders.has_next(),
                    'has_previous': orders.has_previous(),
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Erreur liste commandes pour {request.user.username}: {exc}")
            return Response({
                'error': 'Erreur récupération commandes',
                'details': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, order_number=None):
        """
        Détail d'une commande
        
        GET /api/orders/AF12345678/
        """
        try:
            order = get_object_or_404(
                self.get_queryset(),
                order_number=order_number
            )
            
            serializer = self.get_serializer(order)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Erreur détail commande {order_number}: {exc}")
            return Response({
                'error': 'Erreur récupération commande',
                'details': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def create_from_cart(self, request):
        """
        Créer une commande depuis le panier actuel
        
        POST /api/orders/create_from_cart/
        {
            "shipping_address": "123 Rue Test, Port-au-Prince",
            "shipping_city": "Port-au-Prince",
            "customer_phone": "+509 1234-5678",
            "notes": "Livraison rapide SVP"
        }
        """
        try:
            # Récupérer panier actif
            cart = Cart.objects.filter(
                user=request.user,
                is_active=True
            ).prefetch_related('items__product').first()
            
            if not cart or not cart.items.exists():
                return Response({
                    'error': 'Panier vide',
                    'message': 'Impossible de créer une commande avec un panier vide'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validation des données de livraison
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Données de livraison invalides',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            shipping_data = serializer.validated_data
            
            # Validation supplémentaire avec OrderService
            validation_result = OrderService.validate_shipping_data(shipping_data)
            if not validation_result['valid']:
                return Response({
                    'error': 'Données de livraison invalides',
                    'details': validation_result['errors']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Créer la commande via OrderService
            with transaction.atomic():
                order_result = OrderService.create_order_from_cart(
                    cart=cart,
                    shipping_data=validation_result['cleaned_data'],
                    user=request.user
                )
            
            if order_result['success']:
                # Récupérer la commande créée pour réponse complète
                order = order_result['order']
                order_serializer = OrderSerializer(order)
                
                logger.info(
                    f"Order created from cart - User: {request.user.username}, "
                    f"Order: {order.order_number}, "
                    f"Amount: {order.total_amount} HTG"
                )
                
                return Response({
                    'success': True,
                    'message': 'Commande créée avec succès',
                    'order': order_serializer.data,
                    'order_number': order.order_number,
                    'total_amount': order.total_amount,
                    'next_step': 'payment',
                    'payment_url': f"/api/payments/initiate/?order_number={order.order_number}"
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': 'Erreur création commande',
                    'details': order_result.get('message', 'Erreur inconnue')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except CartEmptyError:
            return Response({
                'error': 'Panier vide',
                'message': 'Impossible de créer une commande avec un panier vide'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except InsufficientStockError as exc:
            return Response({
                'error': 'Stock insuffisant',
                'message': str(exc),
                'action_required': 'Veuillez ajuster les quantités dans votre panier'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except OrderError as exc:
            return Response({
                'error': 'Erreur commande',
                'details': str(exc)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as exc:
            logger.error(f"Erreur création commande depuis panier: {exc}")
            return Response({
                'error': 'Erreur création commande',
                'details': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['put'])
    def cancel(self, request, order_number=None):
        """
        Annuler une commande
        
        PUT /api/orders/AF12345678/cancel/
        {
            "reason": "customer_request",
            "comment": "Client a changé d'avis"
        }
        """
        try:
            order = get_object_or_404(
                self.get_queryset(),
                order_number=order_number
            )
            
            # Validation des données d'annulation
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Données d\'annulation invalides',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            cancel_data = serializer.validated_data
            reason = cancel_data.get('reason', 'customer_request')
            comment = cancel_data.get('comment', '')
            
            # Vérifier si la commande peut être annulée
            if order.status not in ['pending', 'confirmed']:
                return Response({
                    'error': 'Commande ne peut pas être annulée',
                    'message': f'Statut actuel: {order.status}',
                    'current_status': order.status
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if order.payment_status == 'paid':
                return Response({
                    'error': 'Commande déjà payée',
                    'message': 'Contactez le support pour un remboursement',
                    'payment_status': order.payment_status
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Annuler via OrderService
            with transaction.atomic():
                cancel_result = OrderService.cancel_order(order, reason)
                
                # Créer entrée historique
                if comment:
                    OrderStatusHistory.objects.create(
                        order=order,
                        old_status=cancel_result.get('old_status', 'pending'),
                        new_status='cancelled',
                        changed_by=request.user,
                        comment=f"Annulation: {reason}. {comment}"
                    )
            
            if cancel_result['success']:
                # Récupérer commande mise à jour
                order.refresh_from_db()
                order_serializer = OrderSerializer(order)
                
                logger.info(
                    f"Order cancelled - User: {request.user.username}, "
                    f"Order: {order.order_number}, Reason: {reason}"
                )
                
                return Response({
                    'success': True,
                    'message': cancel_result['message'],
                    'order': order_serializer.data,
                    'stock_released': cancel_result.get('stock_released', 0),
                    'reason': reason
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Erreur annulation commande',
                    'details': cancel_result.get('message', 'Erreur inconnue')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as exc:
            logger.error(f"Erreur annulation commande {order_number}: {exc}")
            return Response({
                'error': 'Erreur annulation commande',
                'details': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['put'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, order_number=None):
        """
        Mettre à jour le statut d'une commande (Admin seulement)
        
        PUT /api/orders/AF12345678/update_status/
        {
            "new_status": "shipped",
            "comment": "Expédié par DHL",
            "tracking_number": "DHL123456789"
        }
        """
        try:
            order = get_object_or_404(
                Order.objects.all(),  # Admin peut modifier toutes les commandes
                order_number=order_number
            )
            
            # Validation des données
            serializer = self.get_serializer(
                data=request.data,
                context={'instance': order}
            )
            if not serializer.is_valid():
                return Response({
                    'error': 'Données de mise à jour invalides',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            old_status = order.status
            new_status = validated_data['new_status']
            comment = validated_data.get('comment', '')
            tracking_number = validated_data.get('tracking_number', '')
            
            with transaction.atomic():
                # Mise à jour commande
                order.status = new_status
                if tracking_number:
                    order.tracking_number = tracking_number
                
                # Gestion spéciale selon le statut
                if new_status == 'delivered':
                    order.delivered_at = timezone.now()
                
                order.save()
                
                # Créer entrée historique
                OrderStatusHistory.objects.create(
                    order=order,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by=request.user,
                    comment=comment
                )
            
            # Récupérer commande mise à jour
            order.refresh_from_db()
            order_serializer = OrderSerializer(order)
            
            logger.info(
                f"Order status updated - Admin: {request.user.username}, "
                f"Order: {order.order_number}, "
                f"{old_status} -> {new_status}"
            )
            
            return Response({
                'success': True,
                'message': f'Statut mis à jour: {old_status} -> {new_status}',
                'order': order_serializer.data,
                'old_status': old_status,
                'new_status': new_status
            }, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Erreur mise à jour statut commande {order_number}: {exc}")
            return Response({
                'error': 'Erreur mise à jour statut',
                'details': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Résumé des commandes de l'utilisateur
        
        GET /api/orders/summary/
        """
        try:
            serializer = OrderSummarySerializer()
            summary_data = serializer.to_representation(request.user)
            
            return Response(summary_data, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Erreur résumé commandes pour {request.user.username}: {exc}")
            return Response({
                'total_orders': 0,
                'pending_orders': 0,
                'completed_orders': 0,
                'total_spent': '0.00',
                'currency': 'HTG',
                'last_order_date': None
            }, status=status.HTTP_200_OK)  # Retourner résumé vide en cas d'erreur
    
    @action(detail=False, methods=['get'])
    def status_options(self, request):
        """
        Options de statuts disponibles pour les filtres
        
        GET /api/orders/status_options/
        """
        try:
            return Response({
                'order_statuses': [
                    {'value': choice[0], 'label': choice[1]}
                    for choice in Order.STATUS_CHOICES
                ],
                'payment_statuses': [
                    {'value': choice[0], 'label': choice[1]}
                    for choice in Order.PAYMENT_STATUS_CHOICES
                ]
            }, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Erreur options statuts: {exc}")
            return Response({
                'error': 'Erreur récupération options',
                'details': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)