# marketplace/serializers/order_serializers.py

from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models import Order, OrderItem, OrderStatusHistory, Product, Cart
from ..services.order_service import OrderService, OrderError, CartEmptyError
from ..services.stock_service import StockService

User = get_user_model()


class OrderItemProductSerializer(serializers.ModelSerializer):
    """Serializer pour les données produit dans les items de commande"""
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'slug', 'name', 'short_description', 
            'primary_image', 'is_digital', 'category'
        ]
    
    def get_primary_image(self, obj):
        """Récupérer l'image principale du produit"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return {
                'url': primary_image.image_url,
                'alt_text': primary_image.alt_text or obj.name
            }
        return None


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer pour les items de commande"""
    product = OrderItemProductSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'quantity', 'unit_price', 'total_price',
            'product_name', 'product_sku', 'product_image', 'product_options',
            'created_at'
        ]
        read_only_fields = ['total_price', 'created_at']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer pour l'historique des statuts"""
    changed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderStatusHistory
        fields = [
            'id', 'old_status', 'new_status', 'changed_by_name', 
            'comment', 'created_at'
        ]
    
    def get_changed_by_name(self, obj):
        """Nom de la personne qui a changé le statut"""
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.username
        return "Système"


class OrderSerializer(serializers.ModelSerializer):
    """Serializer complet pour les commandes"""
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    customer_info = serializers.SerializerMethodField()
    shipping_info = serializers.SerializerMethodField()
    billing_info = serializers.SerializerMethodField()
    amounts = serializers.SerializerMethodField()
    timeline = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status', 'payment_method',
            'customer_info', 'shipping_info', 'billing_info', 'amounts',
            'items', 'status_history', 'timeline', 'tracking_number',
            'estimated_delivery', 'delivered_at', 'notes', 'source',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'order_number', 'created_at', 'updated_at'
        ]
    
    def get_customer_info(self, obj):
        """Informations client"""
        return {
            'name': obj.customer_name,
            'email': obj.customer_email,
            'phone': obj.customer_phone,
        }
    
    def get_shipping_info(self, obj):
        """Informations de livraison"""
        return {
            'address': obj.shipping_address,
            'city': obj.shipping_city,
            'country': obj.shipping_country,
            'method': obj.shipping_method,
        }
    
    def get_billing_info(self, obj):
        """Informations de facturation"""
        return {
            'address': obj.billing_address or obj.shipping_address,
            'city': obj.billing_city or obj.shipping_city,
            'country': obj.billing_country or obj.shipping_country,
        }
    
    def get_amounts(self, obj):
        """Détail des montants"""
        return {
            'subtotal': obj.subtotal,
            'shipping_cost': obj.shipping_cost,
            'tax_amount': obj.tax_amount,
            'discount_amount': obj.discount_amount,
            'total_amount': obj.total_amount,
            'currency': obj.currency,
        }
    
    def get_timeline(self, obj):
        """Timeline de la commande"""
        timeline = []
        
        # Création
        timeline.append({
            'status': 'created',
            'label': 'Commande créée',
            'date': obj.created_at,
            'completed': True
        })
        
        # Paiement
        payment_completed = obj.payment_status == 'paid'
        timeline.append({
            'status': 'payment',
            'label': 'Paiement confirmé',
            'date': None,  # À déterminer depuis Transaction si besoin
            'completed': payment_completed
        })
        
        # Confirmation
        confirmed = obj.status in ['confirmed', 'processing', 'shipped', 'delivered']
        timeline.append({
            'status': 'confirmed',
            'label': 'Commande confirmée',
            'date': None,
            'completed': confirmed
        })
        
        # Expédition
        shipped = obj.status in ['shipped', 'delivered']
        timeline.append({
            'status': 'shipped',
            'label': 'Expédiée',
            'date': None,
            'completed': shipped
        })
        
        # Livraison
        delivered = obj.status == 'delivered'
        timeline.append({
            'status': 'delivered',
            'label': 'Livrée',
            'date': obj.delivered_at,
            'completed': delivered
        })
        
        return timeline


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des commandes"""
    items_count = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    payment_status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'payment_status', 'payment_status_display', 'total_amount',
            'currency', 'items_count', 'created_at', 'updated_at'
        ]
    
    def get_items_count(self, obj):
        """Nombre d'articles dans la commande"""
        return obj.items.count()
    
    def get_status_display(self, obj):
        """Libellé du statut en français"""
        status_map = {
            'pending': 'En attente',
            'confirmed': 'Confirmée',
            'processing': 'En traitement',
            'shipped': 'Expédiée',
            'delivered': 'Livrée',
            'cancelled': 'Annulée',
            'refunded': 'Remboursée',
        }
        return status_map.get(obj.status, obj.status)
    
    def get_payment_status_display(self, obj):
        """Libellé du statut de paiement en français"""
        payment_status_map = {
            'pending': 'En attente',
            'paid': 'Payée',
            'failed': 'Échec',
            'refunded': 'Remboursée',
        }
        return payment_status_map.get(obj.payment_status, obj.payment_status)


class CreateOrderFromCartSerializer(serializers.Serializer):
    """Serializer pour créer une commande depuis le panier"""
    shipping_address = serializers.CharField(max_length=500)
    shipping_city = serializers.CharField(max_length=50, default='Port-au-Prince')
    shipping_country = serializers.CharField(max_length=50, default='Haïti')
    customer_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    
    # Adresse de facturation (optionnelle, par défaut = livraison)
    billing_address = serializers.CharField(max_length=500, required=False, allow_blank=True)
    billing_city = serializers.CharField(max_length=50, required=False, allow_blank=True)
    billing_country = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    def validate_shipping_address(self, value):
        """Valider l'adresse de livraison"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Adresse de livraison trop courte (minimum 10 caractères)"
            )
        return value.strip()
    
    def validate_customer_phone(self, value):
        """Valider le numéro de téléphone"""
        if value and value.strip():
            # Format Haïti basique
            clean_phone = ''.join(c for c in value if c.isdigit() or c in ['+', '-', ' ', '(', ')'])
            if len(clean_phone) < 8:
                raise serializers.ValidationError("Numéro de téléphone invalide")
            return clean_phone
        return value
    
    def validate(self, attrs):
        """Validation globale"""
        # Si adresse facturation pas fournie, utiliser livraison
        if not attrs.get('billing_address'):
            attrs['billing_address'] = attrs['shipping_address']
            attrs['billing_city'] = attrs['shipping_city']
            attrs['billing_country'] = attrs['shipping_country']
        
        return attrs


class OrderCancelSerializer(serializers.Serializer):
    """Serializer pour annuler une commande"""
    reason = serializers.CharField(max_length=500, required=False, default="customer_request")
    comment = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    
    def validate_reason(self, value):
        """Valider la raison d'annulation"""
        allowed_reasons = [
            'customer_request', 'out_of_stock', 'payment_failed',
            'address_issue', 'duplicate_order', 'other'
        ]
        
        if value not in allowed_reasons:
            raise serializers.ValidationError(
                f"Raison invalide. Choix possibles: {', '.join(allowed_reasons)}"
            )
        
        return value


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer pour mettre à jour le statut d'une commande (admin)"""
    new_status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    comment = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    tracking_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def validate_new_status(self, value):
        """Valider le nouveau statut"""
        instance = self.context.get('instance')
        if not instance:
            return value
        
        current_status = instance.status
        
        # Règles métier pour les transitions de statut
        valid_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered'],
            'delivered': [],  # État final
            'cancelled': [],  # État final
            'refunded': [],   # État final
        }
        
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Transition invalide de '{current_status}' vers '{value}'"
            )
        
        return value


class OrderSummarySerializer(serializers.Serializer):
    """Serializer pour le résumé des commandes utilisateur"""
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3)
    last_order_date = serializers.DateTimeField()
    
    def to_representation(self, user):
        """Convertir les données utilisateur en résumé commandes"""
        if not user:
            return {
                'total_orders': 0,
                'pending_orders': 0,
                'completed_orders': 0,
                'total_spent': Decimal('0.00'),
                'currency': 'HTG',
                'last_order_date': None
            }
        
        orders = Order.objects.filter(user=user)
        
        return {
            'total_orders': orders.count(),
            'pending_orders': orders.filter(status='pending').count(),
            'completed_orders': orders.filter(status='delivered').count(),
            'total_spent': sum(order.total_amount for order in orders.filter(payment_status='paid')),
            'currency': 'HTG',
            'last_order_date': orders.order_by('-created_at').first().created_at if orders.exists() else None
        }