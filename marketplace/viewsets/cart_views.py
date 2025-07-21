# marketplace/viewsets/cart_viewsets.py

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from django.utils import timezone
from datetime import timedelta

from ..models import Cart, CartItem, Product
from ..serializers.cart_serializers import (
    CartSerializer,
    CartItemSerializer, 
    AddToCartSerializer,
    UpdateCartItemSerializer,
    CartSummarySerializer,
    BulkCartOperationSerializer
)
from ..services.stock_service import StockService, InsufficientStockError, StockError

logger = logging.getLogger(__name__)


class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion complète du panier
    
    Fonctionnalités :
    - Récupération panier actuel utilisateur
    - Ajout/modification/suppression d'articles
    - Validation stock en temps réel
    - Gestion expiration automatique
    """
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Récupérer les paniers de l'utilisateur connecté"""
        return Cart.objects.filter(
            user=self.request.user,
            is_active=True
        ).prefetch_related(
            'items__product__images',
            'items__product__category'
        )
    
    def retrieve(self, request, pk=None):
        """
        Récupérer le panier actuel de l'utilisateur
        
        GET /api/cart/
        
        Crée automatiquement un panier si aucun n'existe
        """
        try:
            # Récupérer ou créer panier actif
            cart, created = Cart.objects.get_or_create(
                user=request.user,
                is_active=True,
                defaults={
                    'expires_at': timezone.now() + timedelta(minutes=30)
                }
            )
            
            # Vérifier expiration
            if cart.expires_at and cart.expires_at <= timezone.now():
                # Panier expiré, en créer un nouveau
                cart.is_active = False
                cart.save()
                
                cart = Cart.objects.create(
                    user=request.user,
                    is_active=True,
                    expires_at=timezone.now() + timedelta(minutes=30)
                )
                created = True
            
            serializer = self.get_serializer(cart)
            
            response_data = serializer.data
            response_data['created'] = created
            response_data['message'] = 'Nouveau panier créé' if created else 'Panier existant récupéré'
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Erreur récupération panier pour {request.user.username}: {exc}")
            return Response({
                'error': 'Erreur récupération panier',
                'details': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request):
        """Rediriger list vers retrieve pour panier unique"""
        return self.retrieve(request)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Ajouter un produit au panier
        
        POST /api/cart/add_item/
        {
            "product_slug": "bol-ceramique",
            "quantity": 2,
            "options": {"color": "blue"} // optionnel
        }
        """
        try:
            # Validation des données
            serializer = AddToCartSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Données invalides',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            product = serializer.context['product']
            
            with transaction.atomic():
                # Récupérer ou créer panier actif
                cart, _ = Cart.objects.get_or_create(
                    user=request.user,
                    is_active=True,
                    defaults={
                        'expires_at': timezone.now() + timedelta(minutes=30)
                    }
                )
                
                # Vérifier si le produit est déjà dans le panier
                existing_item = CartItem.objects.filter(
                    cart=cart,
                    product=product
                ).first()
                
                if existing_item:
                    # Mettre à jour quantité existante
                    new_quantity = existing_item.quantity + validated_data['quantity']
                    
                    # Vérifier stock pour nouvelle quantité
                    availability = StockService.check_availability(product, new_quantity)
                    if not availability['available']:
                        return Response({
                            'error': 'Stock insuffisant',
                            'available_quantity': availability['available_quantity'],
                            'requested_quantity': new_quantity,
                            'current_in_cart': existing_item.quantity
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Réserver le stock supplémentaire
                    additional_quantity = validated_data['quantity']
                    StockService.reserve_stock(product.slug, additional_quantity)
                    
                    existing_item.quantity = new_quantity
                    existing_item.price = product.current_price  # Mise à jour prix
                    existing_item.options = validated_data.get('options', existing_item.options)
                    existing_item.save()
                    
                    cart_item = existing_item
                    action_type = 'updated'
                    
                else:
                    # Réserver stock avant création
                    StockService.reserve_stock(product.slug, validated_data['quantity'])
                    
                    # Créer nouvel item
                    cart_item = CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=validated_data['quantity'],
                        price=product.current_price,
                        options=validated_data.get('options', {})
                    )
                    action_type = 'added'
                
                # Mettre à jour expiration du panier
                cart.expires_at = timezone.now() + timedelta(minutes=30)
                cart.save()
            
            # Réponse avec item et résumé panier
            item_serializer = CartItemSerializer(cart_item)
            cart_summary_serializer = CartSummarySerializer()
            
            logger.info(
                f"Item {action_type} to cart - User: {request.user.username}, "
                f"Product: {product.slug}, Quantity: {cart_item.quantity}"
            )
            
            return Response({
                'success': True,
                'message': f'Produit {action_type} au panier',
                'action': action_type,
                'item': item_serializer.data,
                'cart_summary': cart_summary_serializer.to_representation(cart)
            }, status=status.HTTP_201_CREATED if action_type == 'added' else status.HTTP_200_OK)
            
        except InsufficientStockError as exc:
            return Response({
                'error': 'Stock insuffisant',
                'details': str(exc)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as exc:
            logger.error(f"Erreur ajout produit au panier: {exc}")
            return Response({
                'error': 'Erreur ajout produit',
                'details': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['put'])
    def update_item(self, request):
        """
        Modifier un item du panier
        
        PUT /api/cart/update_item/?item_id=123
        {
            "quantity": 3,
            "options": {"color": "red"}
        }
        """
        try:
            item_id = request.query_params.get('item_id')
            if not item_id:
                return Response({
                    'error': 'item_id requis en paramètre'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Récupérer l'item du panier de l'utilisateur
            cart_item = get_object_or_404(
                CartItem,
                id=item_id,
                cart__user=request.user,
                cart__is_active=True
            )
            
            # Validation des données
            serializer = UpdateCartItemSerializer(
                data=request.data,
                context={'cart_item': cart_item}
            )
            if not serializer.is_valid():
                return Response({
                    'error': 'Données invalides',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            old_quantity = cart_item.quantity
            new_quantity = validated_data['quantity']
            
            with transaction.atomic():
                # Ajuster le stock selon la différence
                quantity_diff = new_quantity - old_quantity
                
                if quantity_diff > 0:
                    # Plus de stock à réserver
                    StockService.reserve_stock(cart_item.product.slug, quantity_diff)
                elif quantity_diff < 0:
                    # Libérer du stock
                    StockService.release_stock(cart_item.product.slug, abs(quantity_diff))
                
                # Mettre à jour l'item
                cart_item.quantity = new_quantity
                cart_item.price = cart_item.product.current_price  # Mise à jour prix
                
                if 'options' in validated_data:
                    cart_item.options = validated_data['options']
                
                cart_item.save()
                
                # Mettre à jour expiration panier
                cart_item.cart.expires_at = timezone.now() + timedelta(minutes=30)
                cart_item.cart.save()
            
            # Réponse avec item mis à jour
            item_serializer = CartItemSerializer(cart_item)
            cart_summary_serializer = CartSummarySerializer()
            
            logger.info(
                f"Cart item updated - User: {request.user.username}, "
                f"Product: {cart_item.product.slug}, New quantity: {cart_item.quantity}"
            )
            
            return Response({
                'success': True,
                'message': 'Article mis à jour',
                'item': item_serializer.data,
                'cart_summary': cart_summary_serializer.to_representation(cart_item.cart)
            }, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Erreur mise à jour item panier: {exc}")
            return Response({
                'error': 'Erreur mise à jour article',
                'details': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """
        Supprimer un item du panier
        
        DELETE /api/cart/remove_item/?item_id=123
        """
        try:
            item_id = request.query_params.get('item_id')
            if not item_id:
                return Response({
                    'error': 'item_id requis en paramètre'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Récupérer l'item du panier de l'utilisateur
            cart_item = get_object_or_404(
                CartItem,
                id=item_id,
                cart__user=request.user,
                cart__is_active=True
            )
            
            # Sauvegarder infos pour logging et libération stock
            product_slug = cart_item.product.slug
            quantity = cart_item.quantity
            cart = cart_item.cart
            
            with transaction.atomic():
                # Libérer le stock réservé
                StockService.release_stock(product_slug, quantity)
                
                # Supprimer l'item
                cart_item.delete()
                
                # Mettre à jour expiration panier
                cart.expires_at = timezone.now() + timedelta(minutes=30)
                cart.save()
            
            # Réponse avec résumé panier mis à jour
            cart_summary_serializer = CartSummarySerializer()
            
            logger.info(
                f"Cart item removed - User: {request.user.username}, "
                f"Product: {product_slug}, Quantity: {quantity}"
            )
            
            return Response({
                'success': True,
                'message': 'Article supprimé du panier',
                'cart_summary': cart_summary_serializer.to_representation(cart)
            }, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Erreur suppression item panier: {exc}")
            return Response({
                'error': 'Erreur suppression article',
                'details': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """
        Vider complètement le panier
        
        DELETE /api/cart/clear/
        """
        try:
            # Récupérer panier actif
            cart = Cart.objects.filter(
                user=request.user,
                is_active=True
            ).first()
            
            if not cart:
                return Response({
                    'message': 'Aucun panier actif à vider'
                }, status=status.HTTP_200_OK)
            
            # Compter items et libérer stock avant suppression
            items_count = 0
            
            with transaction.atomic():
                for cart_item in cart.items.all():
                    StockService.release_stock(cart_item.product.slug, cart_item.quantity)
                    items_count += 1
                
                # Supprimer tous les items
                cart.items.all().delete()
                
                # Marquer panier comme inactif
                cart.is_active = False
                cart.save()
            
            logger.info(
                f"Cart cleared - User: {request.user.username}, "
                f"Items removed: {items_count}"
            )
            
            return Response({
                'success': True,
                'message': f'Panier vidé ({items_count} articles supprimés)',
                'items_removed': items_count
            }, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Erreur vidage panier: {exc}")
            return Response({
                'error': 'Erreur vidage panier',
                'details': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def validate_stock(self, request):
        """
        Valider le stock de tous les items du panier
        
        POST /api/cart/validate_stock/
        """
        try:
            cart = Cart.objects.filter(
                user=request.user,
                is_active=True
            ).prefetch_related('items__product').first()
            
            if not cart or not cart.items.exists():
                return Response({
                    'valid': True,
                    'message': 'Panier vide',
                    'items': []
                }, status=status.HTTP_200_OK)
            
            # Préparer données pour validation en lot
            items_to_validate = [
                {
                    'product_slug': item.product.slug,
                    'quantity': item.quantity
                }
                for item in cart.items.all()
            ]
            
            # Utiliser StockService pour validation en lot
            validation_result = StockService.bulk_check_availability(items_to_validate)
            
            # Formatter la réponse
            items_status = []
            for item_status in validation_result['items_status']:
                cart_item = cart.items.filter(product__slug=item_status['product_slug']).first()
                items_status.append({
                    'cart_item_id': cart_item.id if cart_item else None,
                    'product_slug': item_status['product_slug'],
                    'product_name': item_status['product_name'],
                    'requested_quantity': item_status['requested_quantity'],
                    'available': item_status['available'],
                    'available_quantity': item_status['available_quantity'],
                    'is_digital': item_status['is_digital']
                })
            
            return Response({
                'valid': validation_result['available'],
                'message': 'Tous les articles sont disponibles' if validation_result['available'] 
                          else f"{validation_result['unavailable_count']} articles indisponibles",
                'items': items_status,
                'unavailable_count': validation_result['unavailable_count']
            }, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Erreur validation stock panier: {exc}")
            return Response({
                'error': 'Erreur validation stock',
                'details': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Obtenir un résumé rapide du panier (pour header, etc.)
        
        GET /api/cart/summary/
        """
        try:
            cart = Cart.objects.filter(
                user=request.user,
                is_active=True
            ).prefetch_related('items').first()
            
            serializer = CartSummarySerializer()
            summary_data = serializer.to_representation(cart)
            
            return Response(summary_data, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Erreur résumé panier: {exc}")
            return Response({
                'total_items': 0,
                'total_quantity': 0,
                'subtotal': '0.00',
                'currency': 'HTG'
            }, status=status.HTTP_200_OK)  # Retourner panier vide en cas d'erreur
    
    @action(detail=False, methods=['post'])
    def bulk_add(self, request):
        """
        Ajouter plusieurs produits au panier en une fois
        
        POST /api/cart/bulk_add/
        {
            "items": [
                {"product_slug": "bol-ceramique", "quantity": 2},
                {"product_slug": "chapeau-paille", "quantity": 1}
            ]
        }
        """
        try:
            serializer = BulkCartOperationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Données invalides',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_items = serializer.validated_data['items']
            
            # Validation stock en lot
            items_for_stock_check = [
                {
                    'product_slug': item['product_slug'],
                    'quantity': item['quantity']
                }
                for item in validated_items
            ]
            
            stock_result = StockService.bulk_check_availability(items_for_stock_check)
            if not stock_result['available']:
                return Response({
                    'error': 'Stock insuffisant pour certains articles',
                    'unavailable_items': stock_result['unavailable_items']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # Récupérer ou créer panier
                cart, _ = Cart.objects.get_or_create(
                    user=request.user,
                    is_active=True,
                    defaults={
                        'expires_at': timezone.now() + timedelta(minutes=30)
                    }
                )
                
                items_added = []
                items_updated = []
                
                for item_data in validated_items:
                    product = item_data['product']
                    quantity = item_data['quantity']
                    options = item_data['options']
                    
                    # Réserver stock
                    StockService.reserve_stock(product.slug, quantity)
                    
                    # Vérifier si le produit est déjà dans le panier
                    existing_item = CartItem.objects.filter(
                        cart=cart,
                        product=product
                    ).first()
                    
                    if existing_item:
                        existing_item.quantity += quantity
                        existing_item.price = product.current_price
                        existing_item.options = options
                        existing_item.save()
                        items_updated.append(existing_item)
                    else:
                        new_item = CartItem.objects.create(
                            cart=cart,
                            product=product,
                            quantity=quantity,
                            price=product.current_price,
                            options=options
                        )
                        items_added.append(new_item)
                
                # Mettre à jour expiration panier
                cart.expires_at = timezone.now() + timedelta(minutes=30)
                cart.save()
            
            logger.info(
                f"Bulk add to cart - User: {request.user.username}, "
                f"Added: {len(items_added)}, Updated: {len(items_updated)}"
            )
            
            return Response({
                'success': True,
                'message': f'{len(items_added)} articles ajoutés, {len(items_updated)} mis à jour',
                'items_added': len(items_added),
                'items_updated': len(items_updated),
                'cart_summary': CartSummarySerializer().to_representation(cart)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as exc:
            logger.error(f"Erreur ajout en lot au panier: {exc}")
            return Response({
                'error': 'Erreur ajout en lot',
                'details': str(exc)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)