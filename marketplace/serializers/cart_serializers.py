# marketplace/serializers/cart_serializers.py

from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from ..models import Cart, CartItem, Product
from ..services.stock_service import StockService


class CartItemProductSerializer(serializers.ModelSerializer):
    """Serializer pour les données produit dans les items du panier"""
    current_price = serializers.ReadOnlyField()
    primary_image = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'slug', 'name', 'short_description', 'current_price',
            'primary_image', 'is_digital', 'stock_quantity', 'stock_status'
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
    
    def get_stock_status(self, obj):
        """Obtenir le statut du stock du produit"""
        if obj.is_digital:
            return 'digital'
        
        stock_qty = obj.stock_quantity or 0
        if stock_qty == 0:
            return 'out_of_stock'
        elif stock_qty <= obj.min_stock_alert:
            return 'low_stock'
        else:
            return 'in_stock'


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer pour les items du panier"""
    product = CartItemProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True, required=False)
    total_price = serializers.ReadOnlyField()
    availability = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'quantity', 'price', 
            'total_price', 'options', 'availability', 'created_at'
        ]
        read_only_fields = ['price', 'created_at']
    
    def get_availability(self, obj):
        """Vérifier la disponibilité actuelle du produit"""
        try:
            availability = StockService.check_availability(obj.product, obj.quantity)
            return {
                'available': availability['available'],
                'available_quantity': availability['available_quantity'],
                'message': availability['message']
            }
        except Exception:
            return {
                'available': False,
                'available_quantity': 0,
                'message': 'Erreur vérification stock'
            }
    
    def validate_quantity(self, value):
        """Valider la quantité demandée"""
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être supérieure à 0")
        
        if value > 100:  # Limite raisonnable
            raise serializers.ValidationError("Quantité maximale : 100 articles")
        
        return value


class CartSerializer(serializers.ModelSerializer):
    """Serializer pour le panier complet"""
    items = CartItemSerializer(many=True, read_only=True)
    summary = serializers.SerializerMethodField()
    expiration_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'items', 'summary', 'expiration_info', 
            'created_at', 'updated_at', 'expires_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'expires_at']
    
    def get_summary(self, obj):
        """Calculer le résumé du panier"""
        items = obj.items.all()
        
        if not items:
            return {
                'total_items': 0,
                'total_quantity': 0,
                'subtotal': Decimal('0.00'),
                'estimated_shipping': Decimal('0.00'),
                'estimated_total': Decimal('0.00'),
                'currency': 'HTG'
            }
        
        total_quantity = sum(item.quantity for item in items)
        subtotal = sum(item.total_price for item in items)
        
        # Estimation frais de livraison (logique simple)
        has_digital_only = all(item.product.is_digital for item in items)
        estimated_shipping = Decimal('0.00') if has_digital_only else Decimal('50.00')
        
        return {
            'total_items': items.count(),
            'total_quantity': total_quantity,
            'subtotal': subtotal,
            'estimated_shipping': estimated_shipping,
            'estimated_total': subtotal + estimated_shipping,
            'currency': 'HTG',
            'has_digital_only': has_digital_only
        }
    
    def get_expiration_info(self, obj):
        """Informations sur l'expiration du panier"""
        if not obj.expires_at:
            return None
        
        now = timezone.now()
        time_remaining = obj.expires_at - now
        
        return {
            'expires_at': obj.expires_at,
            'is_expired': time_remaining.total_seconds() <= 0,
            'minutes_remaining': max(0, int(time_remaining.total_seconds() / 60)),
            'warning': time_remaining.total_seconds() <= 300  # Warning si moins de 5 min
        }


class AddToCartSerializer(serializers.Serializer):
    """Serializer pour ajouter un produit au panier"""
    product_slug = serializers.CharField(max_length=200)
    quantity = serializers.IntegerField(min_value=1, max_value=100)
    options = serializers.JSONField(required=False, allow_null=True)
    
    def validate_product_slug(self, value):
        """Valider que le produit existe et est actif"""
        try:
            product = Product.objects.get(slug=value, is_active=True)
            self.context['product'] = product  # Stocker pour réutilisation
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Produit non trouvé ou inactif")
    
    def validate(self, attrs):
        """Validation globale avec vérification stock"""
        product = self.context.get('product')
        quantity = attrs['quantity']
        
        if product:
            # Vérifier stock disponible
            availability = StockService.check_availability(product, quantity)
            if not availability['available']:
                raise serializers.ValidationError({
                    'quantity': f"Stock insuffisant. Disponible: {availability['available_quantity']}"
                })
        
        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer pour modifier un item du panier"""
    quantity = serializers.IntegerField(min_value=1, max_value=100)
    options = serializers.JSONField(required=False, allow_null=True)
    
    def validate(self, attrs):
        """Validation avec vérification stock"""
        cart_item = self.context.get('cart_item')
        quantity = attrs['quantity']
        
        if cart_item:
            # Vérifier stock pour la nouvelle quantité
            availability = StockService.check_availability(cart_item.product, quantity)
            if not availability['available']:
                raise serializers.ValidationError({
                    'quantity': f"Stock insuffisant. Disponible: {availability['available_quantity']}"
                })
        
        return attrs


class CartSummarySerializer(serializers.Serializer):
    """Serializer pour le résumé simple du panier (header, etc.)"""
    total_items = serializers.IntegerField()
    total_quantity = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3)
    
    def to_representation(self, cart):
        """Convertir un Cart en résumé simple"""
        if not cart or not hasattr(cart, 'items') or not cart.items.exists():
            return {
                'total_items': 0,
                'total_quantity': 0,
                'subtotal': Decimal('0.00'),
                'currency': 'HTG'
            }
        
        items = cart.items.all()
        return {
            'total_items': items.count(),
            'total_quantity': sum(item.quantity for item in items),
            'subtotal': sum(item.total_price for item in items),
            'currency': 'HTG'
        }


class BulkCartOperationSerializer(serializers.Serializer):
    """Serializer pour opérations en lot sur le panier"""
    items = serializers.ListField(
        child=serializers.DictField(),
        max_length=50  # Limite raisonnable
    )
    
    def validate_items(self, value):
        """Valider la liste d'items pour opération en lot"""
        if not value:
            raise serializers.ValidationError("Liste d'items requise")
        
        validated_items = []
        
        for item_data in value:
            # Valider structure de chaque item
            if 'product_slug' not in item_data:
                raise serializers.ValidationError("product_slug requis pour chaque item")
            
            if 'quantity' not in item_data:
                raise serializers.ValidationError("quantity requise pour chaque item")
            
            try:
                quantity = int(item_data['quantity'])
                if quantity <= 0:
                    raise serializers.ValidationError("Quantité doit être > 0")
            except (ValueError, TypeError):
                raise serializers.ValidationError("Quantité doit être un nombre entier")
            
            # Vérifier que le produit existe
            try:
                product = Product.objects.get(
                    slug=item_data['product_slug'], 
                    is_active=True
                )
                
                validated_items.append({
                    'product': product,
                    'product_slug': item_data['product_slug'],
                    'quantity': quantity,
                    'options': item_data.get('options', {})
                })
                
            except Product.DoesNotExist:
                raise serializers.ValidationError(
                    f"Produit non trouvé: {item_data['product_slug']}"
                )
        
        return validated_items