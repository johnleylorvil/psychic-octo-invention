# ======================================
# apps/orders/services.py
# ======================================

import uuid
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product


class CartService:
    @staticmethod
    def get_or_create_cart(user=None, session_id=None):
        """Récupère ou crée un panier"""
        if user:
            cart, created = Cart.objects.get_or_create(
                user=user, 
                is_active=True,
                defaults={'expires_at': timezone.now() + timezone.timedelta(days=30)}
            )
        else:
            cart, created = Cart.objects.get_or_create(
                session_id=session_id,
                is_active=True,
                defaults={'expires_at': timezone.now() + timezone.timedelta(days=7)}
            )
        return cart
    
    @staticmethod
    def add_to_cart(cart, product_id, quantity=1, options=None):
        """Ajoute un produit au panier"""
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            # Vérifier le stock
            if product.stock_quantity < quantity:
                raise ValueError("Stock insuffisant")
            
            # Chercher un item existant avec les mêmes options
            existing_item = CartItem.objects.filter(
                cart=cart,
                product=product,
                options=options or {}
            ).first()
            
            if existing_item:
                # Mettre à jour la quantité
                new_quantity = existing_item.quantity + quantity
                if product.stock_quantity < new_quantity:
                    raise ValueError("Stock insuffisant")
                
                existing_item.quantity = new_quantity
                existing_item.save()
                return existing_item
            else:
                # Créer un nouvel item
                price = product.promotional_price or product.price
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity,
                    price=price,
                    options=options or {}
                )
                return cart_item
                
        except Product.DoesNotExist:
            raise ValueError("Produit non trouvé")


class OrderService:
    @staticmethod
    def create_order_from_cart(cart, order_data):
        """Crée une commande à partir d'un panier"""
        with transaction.atomic():
            if not cart.cartitem_set.exists():
                raise ValueError("Le panier est vide")
            
            # Générer numéro de commande
            order_number = f"AF{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
            
            # Calculer les totaux
            subtotal = sum(item.quantity * item.price for item in cart.cartitem_set.all())
            shipping_cost = Decimal('0.00')  # À configurer selon vos règles
            tax_amount = Decimal('0.00')     # À configurer selon vos règles
            total_amount = subtotal + shipping_cost + tax_amount
            
            # Créer la commande
            order = Order.objects.create(
                order_number=order_number,
                user=cart.user,
                customer_name=order_data['customer_name'],
                customer_email=order_data['customer_email'],
                customer_phone=order_data['customer_phone'],
                shipping_address=order_data['shipping_address'],
                shipping_city=order_data.get('shipping_city', 'Port-au-Prince'),
                shipping_country=order_data.get('shipping_country', 'Haïti'),
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax_amount=tax_amount,
                total_amount=total_amount,
                notes=order_data.get('notes', ''),
                coupon_code=order_data.get('coupon_code', ''),
            )
            
            # Créer les items de commande
            for cart_item in cart.cartitem_set.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.price,
                    total_price=cart_item.quantity * cart_item.price,
                    product_name=cart_item.product.name,
                    product_sku=cart_item.product.sku or '',
                    product_image=cart_item.product.images.filter(is_primary=True).first().image_url if cart_item.product.images.filter(is_primary=True).exists() else '',
                    product_options=cart_item.options or {}
                )
                
                # Décrémenter le stock
                cart_item.product.stock_quantity -= cart_item.quantity
                cart_item.product.save()
            
            # Vider le panier
            cart.is_active = False
            cart.save()
            
            return order