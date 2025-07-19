from rest_framework import serializers
from django.core.validators import MinValueValidator
from decimal import Decimal
from ..models import Cart, CartItem, Product

# ============= SERIALIZERS CART ITEMS =============

class CartProductSerializer(serializers.ModelSerializer):
    """Serializer produit pour les items du panier"""
    current_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description',
            'current_price', 'stock_quantity', 'in_stock',
            'primary_image', 'is_active', 'requires_shipping'
        ]
    
    def get_current_price(self, obj):
        """Prix actuel (promotionnel si disponible)"""
        return str(obj.current_price)
    
    def get_in_stock(self, obj):
        """Disponibilité en stock"""
        return obj.in_stock
    
    def get_primary_image(self, obj):
        """Image principale du produit"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return {
                'url': primary_image.image_url,
                'alt_text': primary_image.alt_text
            }
        # Fallback sur la première image disponible
        first_image = obj.images.first()
        if first_image:
            return {
                'url': first_image.image_url,
                'alt_text': first_image.alt_text
            }
        return None

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer pour les items du panier"""
    product = CartProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'quantity', 'price', 'total_price',
            'options', 'is_available', 'stock_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'price', 'created_at', 'updated_at']
    
    def get_total_price(self, obj):
        """Prix total de l'item (quantité × prix)"""
        return str(obj.total_price)
    
    def get_is_available(self, obj):
        """Vérification si le produit est toujours disponible"""
        return obj.product.is_active and obj.product.in_stock
    
    def get_stock_status(self, obj):
        """Statut détaillé du stock"""
        product = obj.product
        if not product.is_active:
            return {
                'status': 'unavailable',
                'message': 'Produit non disponible'
            }
        
        if not product.in_stock:
            return {
                'status': 'out_of_stock',
                'message': 'Rupture de stock'
            }
        
        if product.stock_quantity < obj.quantity:
            return {
                'status': 'insufficient_stock',
                'message': f'Stock insuffisant (disponible: {product.stock_quantity})',
                'available_quantity': product.stock_quantity
            }
        
        return {
            'status': 'available',
            'message': 'Disponible'
        }

# ============= SERIALIZER CART COMPLET =============

class CartSerializer(serializers.ModelSerializer):
    """Serializer principal pour le panier"""
    items = CartItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    total_shipping = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    cart_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'items', 'items_count', 'subtotal', 
            'total_shipping', 'total_amount', 'cart_summary',
            'is_active', 'expires_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        """Nombre total d'articles dans le panier"""
        return sum(item.quantity for item in obj.items.all())
    
    def get_subtotal(self, obj):
        """Sous-total des articles (sans frais de port)"""
        subtotal = sum(item.total_price for item in obj.items.all())
        return str(subtotal)
    
    def get_total_shipping(self, obj):
        """Calcul des frais de port (logique business)"""
        # Logique simple : gratuit si > 50 HTG, sinon 10 HTG
        subtotal = sum(item.total_price for item in obj.items.all())
        requires_shipping = any(item.product.requires_shipping for item in obj.items.all())
        
        if not requires_shipping:
            return "0.00"
        
        if subtotal >= Decimal('50.00'):
            return "0.00"  # Livraison gratuite
        
        return "10.00"  # Frais de port standard
    
    def get_total_amount(self, obj):
        """Montant total (sous-total + frais de port)"""
        subtotal = Decimal(self.get_subtotal(obj))
        shipping = Decimal(self.get_total_shipping(obj))
        return str(subtotal + shipping)
    
    def get_cart_summary(self, obj):
        """Résumé détaillé du panier"""
        items = obj.items.all()
        available_items = [item for item in items if item.product.is_active and item.product.in_stock]
        unavailable_items = [item for item in items if not (item.product.is_active and item.product.in_stock)]
        
        return {
            'total_items': len(items),
            'available_items': len(available_items),
            'unavailable_items': len(unavailable_items),
            'has_shipping_items': any(item.product.requires_shipping for item in items),
            'is_valid_for_checkout': len(unavailable_items) == 0 and len(available_items) > 0
        }

# ============= SERIALIZERS POUR ACTIONS =============

class AddToCartSerializer(serializers.Serializer):
    """Serializer pour ajouter un produit au panier"""
    product_slug = serializers.CharField(max_length=200)
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)])
    options = serializers.JSONField(required=False, allow_null=True)
    
    def validate_product_slug(self, value):
        """Validation de l'existence et disponibilité du produit"""
        try:
            product = Product.objects.get(slug=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Produit non trouvé ou non disponible")
        
        if not product.in_stock:
            raise serializers.ValidationError("Produit en rupture de stock")
        
        return value
    
    def validate(self, attrs):
        """Validation croisée quantité/stock"""
        product = Product.objects.get(slug=attrs['product_slug'])
        quantity = attrs['quantity']
        
        if product.stock_quantity < quantity:
            raise serializers.ValidationError({
                'quantity': f'Stock insuffisant (disponible: {product.stock_quantity})'
            })
        
        return attrs

class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer pour modifier un item du panier"""
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)])
    options = serializers.JSONField(required=False, allow_null=True)
    
    def validate_quantity(self, value):
        """Validation de la quantité par rapport au stock"""
        cart_item = self.instance
        if cart_item and cart_item.product.stock_quantity < value:
            raise serializers.ValidationError(
                f'Stock insuffisant (disponible: {cart_item.product.stock_quantity})'
            )
        return value

class MergeCartSerializer(serializers.Serializer):
    """Serializer pour fusionner les paniers session → utilisateur"""
    session_id = serializers.CharField(max_length=255)
    
    def validate_session_id(self, value):
        """Validation de l'existence du panier session"""
        if not Cart.objects.filter(session_id=value, is_active=True).exists():
            raise serializers.ValidationError("Panier session non trouvé")
        return value

# ============= SERIALIZER LÉGER POUR HEADER =============

class CartSummarySerializer(serializers.ModelSerializer):
    """Serializer léger pour l'affichage header (nombre d'items)"""
    items_count = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items_count', 'subtotal']
    
    def get_items_count(self, obj):
        return sum(item.quantity for item in obj.items.all())
    
    def get_subtotal(self, obj):
        subtotal = sum(item.total_price for item in obj.items.all())
        return str(subtotal)