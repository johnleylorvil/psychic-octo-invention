# ======================================
# apps/orders/serializers.py
# ======================================

from rest_framework import serializers
from decimal import Decimal
from .models import Cart, CartItem, Order, OrderItem
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'price', 'options', 'subtotal', 'created_at']
    
    def get_subtotal(self, obj):
        return obj.quantity * obj.price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'items_count', 'total_amount', 'created_at', 'expires_at']
    
    def get_items_count(self, obj):
        return obj.cartitem_set.count()
    
    def get_total_amount(self, obj):
        return sum(item.quantity * item.price for item in obj.cartitem_set.all())


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    options = serializers.JSONField(required=False)
    
    def validate_product_id(self, value):
        from products.models import Product
        try:
            product = Product.objects.get(id=value, is_active=True)
            if product.stock_quantity < self.initial_data.get('quantity', 1):
                raise serializers.ValidationError("Stock insuffisant.")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Produit non trouvé.")


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'unit_price', 'total_price', 'product_image', 'product_options']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer_name', 'customer_email', 
            'customer_phone', 'shipping_address', 'shipping_city', 
            'total_amount', 'currency', 'status', 'payment_status',
            'tracking_number', 'created_at', 'items'
        ]


class CreateOrderSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=100)
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(max_length=20)
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField(max_length=50, default='Port-au-Prince')
    shipping_country = serializers.CharField(max_length=50, default='Haïti')
    notes = serializers.CharField(required=False, allow_blank=True)
    coupon_code = serializers.CharField(required=False, allow_blank=True)

