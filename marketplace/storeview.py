# storeview.py - Mise à jour complète
from datetime import timezone
import requests
import json
import uuid
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings
from django.db import transaction
from django.db.models import F
from .models import (
    Category, Product, Cart, CartItem, Order, OrderItem, Transaction
)
from django.db import models

class StoreView(View):
    # Liste statique et prédéfinie des catégories/slugs à afficher
    STORE_SLUGS = [
        'agricole',
        'patriotiques',
        'petite-industrie',
        'services',
        'store-produits-de-premiere-necessite'
    ]
    # Configuration MonCash
    MONCASH_MODE = getattr(settings, 'MONCASH_ENV', 'sandbox')  # 'sandbox' ou 'live'
    MONCASH_CLIENT_ID = settings.MONCASH_CLIENT_ID
    MONCASH_CLIENT_SECRET = settings.MONCASH_CLIENT_SECRET

    def get_moncash_base_url(self):
        """Retourne l'URL de base selon l'environnement"""
        if self.MONCASH_MODE == 'live':
            return "https://moncashbutton.digicelgroup.com"
        return "https://sandbox.moncashbutton.digicelgroup.com"

    def get_moncash_api_url(self):
        """Retourne l'URL de l'API selon l'environnement"""
        base = self.get_moncash_base_url()
        return f"{base}/Api"

    def get_access_token(self):
        """Obtient le token d'accès MonCash"""
        api_url = self.get_moncash_api_url()
        auth = (self.MONCASH_CLIENT_ID, self.MONCASH_CLIENT_SECRET)
        response = requests.post(
            f"{api_url}/oauth/token",
            auth=auth,
            data={
                "scope": "read,write",
                "grant_type": "client_credentials"
            },
            headers={"Accept": "application/json"}
        )
        if response.status_code == 200:
            return response.json().get('access_token')
        return None

    def create_moncash_payment(self, order, amount):
        """Crée un paiement MonCash et retourne l'URL de redirection"""
        access_token = self.get_access_token()
        if not access_token:
            return None

        api_url = self.get_moncash_api_url()
        response = requests.post(
            f"{api_url}/v1/CreatePayment",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            data=json.dumps({
                "amount": float(amount),
                "orderId": order.order_number
            })
        )
        if response.status_code == 202:
            payment_data = response.json()
            payment_token = payment_data.get('payment_token', {}).get('token')
            if payment_token:
                gateway_base = self.get_moncash_base_url() + "/Moncash-middleware"
                return f"{gateway_base}/Payment/Redirect?token={payment_token}"
        return None

    def get(self, request, store_name=None, *args, **kwargs):
        """Gère les requêtes GET pour afficher le store ou un produit"""
        # Si on demande les détails d'un produit
        if 'product_id' in request.GET:
            product_id = request.GET.get('product_id')
            return self.show_product(request, product_id)
        # Si on demande le contenu du panier
        if request.GET.get('action') == 'cart':
            return self.get_cart(request)
        # Sinon, afficher le store
        return self.render_store(request, store_name)

    def post(self, request, store_name=None, *args, **kwargs):
        """Gère les requêtes POST pour le panier et le checkout"""
        action = request.POST.get('action')
        if action == 'add_to_cart':
            return self.add_to_cart(request)
        elif action == 'update_cart':
            return self.update_cart(request)
        elif action == 'remove_from_cart':
            return self.remove_from_cart(request)
        elif action == 'checkout':
            return self.process_checkout(request)
        elif action == 'moncash_payment':
            return self.process_moncash_payment(request)
        return JsonResponse({'error': 'Action non reconnue'}, status=400)

    def render_store(self, request, store_name):
        """Affiche le store avec ses produits"""
        # Vérifier si le store_name fait partie de notre liste prédéfinie
        # if store_name not in self.STORE_SLUGS:
        #      # Optionnel: Afficher une 404 ou une page par défaut
        #      # Pour l'instant, on laisse passer pour permettre l'affichage d'autres catégories
        #      # si jamais l'URL est appelée directement avec un slug non-listé.
        #      pass
        # Récupérer la catégorie par son slug
        try:
            category = Category.objects.get(slug=store_name, is_active=True)
        except Category.DoesNotExist:
            return render(request, '404.html', status=404)
        # Récupérer les produits de cette catégorie, en préchargeant les images
        # --- MISE À JOUR : prefetch_related('images') ---
        products = Product.objects.filter(category=category, is_active=True).prefetch_related('images')
        # Récupérer ou créer le panier
        cart = self.get_or_create_cart(request)
        context = {
            'store_name': store_name,
            'category': category,
            'category_name': category.name, # Le nom lisible de la catégorie
            'products': products, # Liste de produits avec images préchargées
            'cart': cart,
            'cart_items': cart.items.all() if cart else [],
            # Passer la liste statique pour le header si nécessaire ailleurs
            'main_categories': Category.objects.filter(slug__in=self.STORE_SLUGS, is_active=True)
        }
        return render(request, 'store/store.html', context)

    def show_product(self, request, product_id):
        """Affiche les détails d'un produit"""
        # --- MISE À JOUR : prefetch_related('images') ---
        product = get_object_or_404(Product.objects.prefetch_related('images'), id=product_id, is_active=True)
        # Récupérer ou créer le panier
        cart = self.get_or_create_cart(request)
        # --- MISE À JOUR : Ajout de 'category' dans le contexte ---
        context = {
            'product': product, # Objet produit avec images préchargées
            'category': product.category, # ✅ Ajout de la catégorie ici
            'cart': cart,
            'cart_items': cart.items.all() if cart else [],
            # Passer la liste statique pour le header si nécessaire ailleurs
            'main_categories': Category.objects.filter(slug__in=self.STORE_SLUGS, is_active=True)
            # Note : Vous pourriez vouloir ajouter ici les produits similaires
            # par exemple : 'related_products': Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4].prefetch_related('images')
        }
        return render(request, 'store/product_detail.html', context)

    def get_cart(self, request):
        """Retourne le contenu du panier au format JSON"""
        cart = self.get_or_create_cart(request)
        items = [{
            'id': item.id,
            'product_id': item.product.id,
            'name': item.product.name,
            'quantity': item.quantity,
            'price': float(item.price),
            'total_price': float(item.total_price),
            # --- MISE À JOUR : Utilisation de image_url ---
            'image_url': item.product.images.filter(is_primary=True).first().image_url if item.product.images.exists() else ''
        } for item in cart.items.all()]
        return JsonResponse({
            'cart_id': cart.id,
            'items': items,
            'total_items': sum(item.quantity for item in cart.items.all()),
            'total_amount': float(cart.items.aggregate(
                total=models.Sum(models.F('quantity') * models.F('price'))
            )['total'] or 0)
        })

    def get_or_create_cart(self, request):
        """Récupère ou crée un panier pour l'utilisateur ou la session"""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                user=request.user,
                is_active=True,
                defaults={'session_id': request.session.session_key}
            )
        else:
            session_id = request.session.session_key or str(uuid.uuid4())
            if not request.session.session_key:
                request.session.create()
                session_id = request.session.session_key
            cart, created = Cart.objects.get_or_create(
                session_id=session_id,
                is_active=True,
                defaults={'session_id': session_id}
            )
        return cart

    def add_to_cart(self, request):
        """Ajoute un produit au panier"""
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id, is_active=True)
        if quantity < 1:
            return JsonResponse({'error': 'Quantité invalide'}, status=400)
        cart = self.get_or_create_cart(request)
        # Vérifier si le produit est déjà dans le panier
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                'price': product.current_price
            }
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        # Retourner le nouveau contenu du panier
        return self.get_cart(request)

    def update_cart(self, request):
        """Met à jour la quantité d'un produit dans le panier"""
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            return self.remove_from_cart(request)
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__is_active=True)
            cart_item.quantity = quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Article non trouvé'}, status=404)
        return self.get_cart(request)

    def remove_from_cart(self, request):
        """Supprime un produit du panier"""
        item_id = request.POST.get('item_id')
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__is_active=True)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Article non trouvé'}, status=404)
        return self.get_cart(request)

    def process_checkout(self, request):
        """Prépare la commande et redirige vers le paiement"""
        cart = self.get_or_create_cart(request)
        if not cart.items.exists():
            return JsonResponse({'error': 'Le panier est vide'}, status=400)
        # Créer une commande
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_name=request.user.get_full_name() if request.user.is_authenticated else "Client",
                customer_email=request.user.email if request.user.is_authenticated else request.POST.get('email'),
                customer_phone=request.POST.get('phone', ''),
                shipping_address=request.POST.get('address', ''),
                shipping_city=request.POST.get('city', 'Port-au-Prince'),
                shipping_country=request.POST.get('country', 'Haïti'),
                billing_address=request.POST.get('billing_address', request.POST.get('address', '')),
                billing_city=request.POST.get('billing_city', request.POST.get('city', 'Port-au-Prince')),
                billing_country=request.POST.get('billing_country', request.POST.get('country', 'Haïti')),
                subtotal=request.POST.get('subtotal', 0),
                shipping_cost=request.POST.get('shipping_cost', 0),
                tax_amount=request.POST.get('tax_amount', 0),
                total_amount=request.POST.get('total_amount', 0),
                status='pending',
                payment_status='pending',
                payment_method='moncash'
            )
            # Créer les OrderItems
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.price,
                    product_name=item.product.name,
                    product_sku=item.product.sku,
                    # --- MISE À JOUR : Utilisation de image_url ---
                    product_image=item.product.images.filter(is_primary=True).first().image_url if item.product.images.exists() else ''
                )
                # Réduire le stock (optionnel, on peut attendre le paiement)
                # item.product.stock_quantity = F('stock_quantity') - item.quantity
                # item.product.save()
            # Créer une transaction
            transaction_obj = Transaction.objects.create(
                order=order,
                amount=order.total_amount,
                status='pending',
                payment_method='moncash',
                moncash_order_id=order.order_number,
                callback_url=request.build_absolute_uri(reverse('store:moncash_callback')),
                return_url=request.build_absolute_uri(reverse('store:moncash_return'))
            )
        # Vider le panier
        cart.is_active = False
        cart.save()
        return JsonResponse({
            'order_id': order.id,
            'order_number': order.order_number,
            'transaction_id': transaction_obj.id
        })

    def process_moncash_payment(self, request):
        """Initie le paiement avec MonCash"""
        order_number = request.POST.get('order_number')
        try:
            order = Order.objects.get(order_number=order_number)
            transaction_obj = Transaction.objects.get(order=order, status='pending')
        except (Order.DoesNotExist, Transaction.DoesNotExist):
            return JsonResponse({'error': 'Commande non trouvée'}, status=404)
        # Créer le paiement MonCash
        payment_url = self.create_moncash_payment(order, order.total_amount)
        if not payment_url:
            return JsonResponse({'error': 'Erreur lors de la création du paiement'}, status=500)
        # Mettre à jour la transaction avec l'URL de paiement
        # Note: Le token est généralement dans l'URL, mais vous pouvez l'extraire si nécessaire
        transaction_obj.payment_token = payment_url.split('token=')[-1] if 'token=' in payment_url else None
        transaction_obj.save()
        return JsonResponse({'payment_url': payment_url})

# Les vues MonCashCallbackView et MonCashReturnView restent inchangées
# (Elles sont incluses ici pour complétude mais n'ont pas été modifiées)
class MonCashCallbackView(View):
    """Endpoint pour le callback MonCash (appelé en backend)"""
    def post(self, request, *args, **kwargs):
        try:
            # Récupérer les données du callback
            data = json.loads(request.body)
            order_id = data.get('orderId')
            # Vérifier que c'est bien une notification MonCash
            if not order_id:
                return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
            # Trouver la transaction
            try:
                transaction_obj = Transaction.objects.get(moncash_order_id=order_id)
                order = transaction_obj.order
            except Transaction.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Transaction not found'}, status=404)
            # Vérifier le statut du paiement via l'API MonCash
            access_token = StoreView().get_access_token()
            if not access_token:
                return JsonResponse({'status': 'error', 'message': 'Authentication failed'}, status=500)
            api_url = StoreView().get_moncash_api_url()
            response = requests.post(
                f"{api_url}/v1/RetrieveOrderPayment",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                data=json.dumps({"orderId": order_id})
            )
            if response.status_code == 200:
                payment_data = response.json().get('payment', {})
                status = payment_data.get('message', '').lower()
                # Mettre à jour la transaction
                transaction_obj.gateway_response = payment_data
                transaction_obj.webhook_received_at = timezone.now()
                if status == 'successful':
                    transaction_obj.status = 'completed'
                    order.payment_status = 'paid'
                    order.status = 'confirmed'
                    # Mettre à jour le stock des produits
                    for item in order.items.all():
                        item.product.stock_quantity = F('stock_quantity') - item.quantity
                        item.product.save(update_fields=['stock_quantity'])
                else:
                    transaction_obj.status = 'failed'
                    order.payment_status = 'failed'
                transaction_obj.save()
                order.save()
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Payment verification failed'}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

class MonCashReturnView(View):
    """Endpoint pour le retour MonCash (où l'utilisateur est redirigé)"""
    def get(self, request, *args, **kwargs):
        order_number = request.GET.get('orderId')
        try:
            order = Order.objects.get(order_number=order_number)
            transaction_obj = Transaction.objects.get(order=order)
            # Passer les catégories statiques au template de retour aussi
            context = {
                'order': order,
                'transaction': transaction_obj,
                'success': transaction_obj.status == 'completed',
                'main_categories': Category.objects.filter(slug__in=StoreView.STORE_SLUGS, is_active=True)
            }
            return render(request, 'store/moncash_return.html', context)
        except (Order.DoesNotExist, Transaction.DoesNotExist):
            context = {
                'error': 'Commande non trouvée',
                 'main_categories': Category.objects.filter(slug__in=StoreView.STORE_SLUGS, is_active=True)
            }
            return render(request, 'store/moncash_return.html', context, status=404)
