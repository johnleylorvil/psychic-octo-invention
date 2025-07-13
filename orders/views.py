# ======================================
# apps/orders/views.py
# ======================================

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Order
from .serializers import (
    CartSerializer, AddToCartSerializer, UpdateCartItemSerializer,
    OrderSerializer, CreateOrderSerializer
)
from .services import CartService, OrderService


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cart(request):
    """
    Récupère le panier
    GET /api/v1/orders/cart/
    """
    user = request.user if request.user.is_authenticated else None
    session_id = request.session.session_key
    
    if not session_id and not user:
        request.session.save()
        session_id = request.session.session_key
    
    cart = CartService.get_or_create_cart(user=user, session_id=session_id)
    serializer = CartSerializer(cart)
    
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def add_to_cart(request):
    """
    Ajoute un produit au panier
    POST /api/v1/orders/cart/add/
    """
    serializer = AddToCartSerializer(data=request.data)
    
    if serializer.is_valid():
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key
        
        if not session_id and not user:
            request.session.save()
            session_id = request.session.session_key
        
        try:
            cart = CartService.get_or_create_cart(user=user, session_id=session_id)
            cart_item = CartService.add_to_cart(
                cart=cart,
                product_id=serializer.validated_data['product_id'],
                quantity=serializer.validated_data['quantity'],
                options=serializer.validated_data.get('options')
            )
            
            return Response({
                'success': True,
                'message': 'Produit ajouté au panier!',
                'data': CartSerializer(cart).data
            })
            
        except ValueError as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_cart_item(request, item_id):
    """
    Met à jour un item du panier
    PUT /api/v1/orders/cart/items/{item_id}/
    """
    serializer = UpdateCartItemSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            cart_item = get_object_or_404(CartItem, id=item_id)
            quantity = serializer.validated_data['quantity']
            
            if quantity == 0:
                cart_item.delete()
                message = "Produit retiré du panier"
            else:
                # Vérifier le stock
                if cart_item.product.stock_quantity < quantity:
                    return Response({
                        'success': False,
                        'message': 'Stock insuffisant'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                cart_item.quantity = quantity
                cart_item.save()
                message = "Panier mis à jour"
            
            return Response({
                'success': True,
                'message': message,
                'data': CartSerializer(cart_item.cart).data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Erreur lors de la mise à jour'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def remove_from_cart(request, item_id):
    """
    Supprime un item du panier
    DELETE /api/v1/orders/cart/items/{item_id}/
    """
    try:
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart = cart_item.cart
        cart_item.delete()
        
        return Response({
            'success': True,
            'message': 'Produit retiré du panier',
            'data': CartSerializer(cart).data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Erreur lors de la suppression'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_order(request):
    """
    Crée une commande à partir du panier
    POST /api/v1/orders/checkout/
    """
    serializer = CreateOrderSerializer(data=request.data)
    
    if serializer.is_valid():
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key
        
        try:
            # Récupérer le panier
            if user:
                cart = Cart.objects.get(user=user, is_active=True)
            else:
                cart = Cart.objects.get(session_id=session_id, is_active=True)
            
            # Créer la commande
            order = OrderService.create_order_from_cart(cart, serializer.validated_data)
            
            return Response({
                'success': True,
                'message': 'Commande créée avec succès!',
                'data': OrderSerializer(order).data
            }, status=status.HTTP_201_CREATED)
            
        except Cart.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Panier non trouvé'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except ValueError as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders(request):
    """
    Récupère les commandes de l'utilisateur
    GET /api/v1/orders/
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """
    Détail d'une commande
    GET /api/v1/orders/{order_id}/
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    serializer = OrderSerializer(order)
    
    return Response({
        'success': True,
        'data': serializer.data
    })
