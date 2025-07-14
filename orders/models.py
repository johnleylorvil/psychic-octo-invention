# ======================================
# apps/orders/models.py
# ======================================

from django.db import models
from django.conf import settings


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    session_id = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(null=True, blank=True, default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f'Cart {self.id}'


class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    options = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)

    class Meta:
        db_table = 'cart_items'

    def __str__(self):
        return f'CartItem {self.id}'


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=100)
    customer_email = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=50, blank=True, default='Port-au-Prince')
    shipping_country = models.CharField(max_length=50, blank=True, default='Haïti')
    billing_address = models.TextField(null=True, blank=True)
    billing_city = models.CharField(max_length=50, blank=True)
    billing_country = models.CharField(max_length=50, blank=True, default='Haïti')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, blank=True, default='HTG')
    status = models.CharField(max_length=20, blank=True, default='pending')
    payment_status = models.CharField(max_length=20, blank=True, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, default='moncash')
    shipping_method = models.CharField(max_length=50, blank=True, default='standard')
    tracking_number = models.CharField(max_length=100, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    admin_notes = models.TextField(null=True, blank=True)
    coupon_code = models.CharField(max_length=50, blank=True)
    source = models.CharField(max_length=50, blank=True, default='web')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f'Order {self.order_number}'


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50, blank=True)
    product_image = models.CharField(max_length=255, blank=True)
    product_options = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)

    class Meta:
        db_table = 'order_items'

    def __str__(self):
        return f'OrderItem {self.id} - {self.product_name}'


class OrderStatusHistory(models.Model):
    id = models.AutoField(primary_key=True)
    old_status = models.CharField(max_length=50, blank=True)
    new_status = models.CharField(max_length=50)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'order_status_history'

    def __str__(self):
        return f'Status change for {self.order.order_number}: {self.old_status} → {self.new_status}'
