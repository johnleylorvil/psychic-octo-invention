from django.shortcuts import render, get_object_or_404, redirect
import datetime
import requests
import json
import logging
import uuid
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q, Sum
from django.conf import settings

# Assurez-vous d'importer tous vos modèles depuis le bon endroit
from .models import (
    Banner, Product, MediaContentSection, Category, ProductImage, 
    Cart, CartItem, User, Order, OrderItem
)

# Configuration du logging
logger = logging.getLogger(__name__)

# ==========================================================================
# CONFIGURATION MONCASH
# ==========================================================================

# À configurer dans votre settings.py ou variables d'environnement
MONCASH_CLIENT_ID = getattr(settings, 'MONCASH_CLIENT_ID')
MONCASH_CLIENT_SECRET = getattr(settings, 'MONCASH_CLIENT_SECRET')
MONCASH_BASE_URL = "https://sandbox.moncashbutton.digicelgroup.com"
MONCASH_API_URL = f"{MONCASH_BASE_URL}/Api"
MONCASH_GATEWAY_URL = f"{MONCASH_BASE_URL}/Moncash-middleware"

def get_moncash_access_token():
    """Obtenir le token d'accès MonCash selon la documentation"""
    url = f"{MONCASH_API_URL}/oauth/token"
    
    # Authentification Basic avec client_id:client_secret
    auth = (MONCASH_CLIENT_ID, MONCASH_CLIENT_SECRET)
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'scope': 'read,write',
        'grant_type': 'client_credentials'
    }
    
    try:
        response = requests.post(url, auth=auth, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        return token_data.get('access_token')
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'obtention du token MonCash: {e}")
        return None

def verify_payment_by_transaction(transaction_id):
    """Vérifier un paiement par transaction ID selon la documentation"""
    try:
        access_token = get_moncash_access_token()
        if not access_token:
            return None
        
        api_url = f"{MONCASH_API_URL}/v1/RetrieveTransactionPayment"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        data = {
            'transactionId': transaction_id
        }
        
        response = requests.post(api_url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erreur lors de la vérification: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Erreur dans verify_payment_by_transaction: {str(e)}")
        return None

def create_order_from_session(request, transaction_id, payment_details):
    """Créer une commande à partir des données de session"""
    try:
        order_data = request.session.get('order_data')
        if not order_data:
            return None
        
        # Créer la commande avec les détails du paiement
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            order_id=order_data['order_id'],
            transaction_id=transaction_id,
            payment_method='moncash',
            payment_status='completed',
            total_amount=payment_details.get('cost', order_data['total_amount']),
            status='confirmed',
            payer_phone=payment_details.get('payer', ''),
            payment_reference=payment_details.get('reference', ''),
        )
        
        # Créer les items de commande à partir des données de session
        for item_data in order_data.get('cart_items', []):
            try:
                product = Product.objects.get(id=item_data['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data['quantity'],
                    price=item_data['price'],
                )
            except Product.DoesNotExist:
                logger.warning(f"Produit {item_data['product_id']} non trouvé lors de la création de commande")
                continue
        
        return order
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de la commande: {str(e)}")
        return None

# ==========================================================================
# VUES PRINCIPALES
# ==========================================================================

def homewert(request):
    """
    Affiche la page d'accueil avec :
    - Un slideshow de bannières.
    - Une section "collage" avec des images de produits aléatoires.
    - Une grille de produits vedettes sélectionnés aléatoirement.
    """

    # --- 1. Bannières pour le Slideshow ---
    banners = Banner.objects.filter(is_active=True).order_by('sort_order')

    # --- 2. Images pour la Section "Collage" (Section 3) ---
    collage_products = Product.objects.filter(
        is_active=True, 
        images__isnull=False
    ).distinct().order_by('?')[:3]

    def get_product_image_url(product):
        if not product:
            return None
        image = product.images.filter(is_primary=True).first() or product.images.first()
        return image.image_url if image else None

    collage_image_1 = get_product_image_url(collage_products[0] if len(collage_products) > 0 else None)
    collage_image_2 = get_product_image_url(collage_products[1] if len(collage_products) > 1 else None)
    collage_image_3 = get_product_image_url(collage_products[2] if len(collage_products) > 2 else None)

    # --- 3. Produits Vedettes (aléatoires) ---
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).order_by('?')[:8]

    context = {
        'banners': banners,
        'collage_image_1': collage_image_1,
        'collage_image_2': collage_image_2,
        'collage_image_3': collage_image_3,
        'featured_products': featured_products,
    }
    
    return render(request, 'pages/home.html', context)

# ===================================================================
# FONCTION HELPER POUR LE PANIER
# ===================================================================
def _get_cart(request):
    """
    Récupère le panier de l'utilisateur ou en crée un.
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_id=session_key, user=None, defaults={'is_active': True})
    return cart

# ===================================================================
# VUES POUR LA BOUTIQUE (STORE)
# ===================================================================
def store(request):
    """Affiche la page principale de la boutique avec filtres, recherche"""
    primary_image_prefetch = Prefetch('images', queryset=ProductImage.objects.filter(is_primary=True), to_attr='primary_image_list')
    products_list = Product.objects.filter(is_active=True).select_related('category', 'seller').prefetch_related(primary_image_prefetch)

    # Filtrage par Catégorie
    selected_category_slug = request.GET.get('category')
    if selected_category_slug:
        try:
            category = get_object_or_404(Category, slug=selected_category_slug)
            child_categories = category.children.all()
            category_ids = [category.id] + [child.id for child in child_categories]
            products_list = products_list.filter(category__id__in=category_ids)
        except:
            products_list = products_list.none()

    # Filtrage par Recherche
    search_query = request.GET.get('q')
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        ).distinct()

    # Tri
    sort_option = request.GET.get('sort')
    if sort_option == 'price_asc':
        products_list = products_list.order_by('price')
    elif sort_option == 'price_desc':
        products_list = products_list.order_by('-price')
    elif sort_option == 'date_desc':
        products_list = products_list.order_by('-created_at')

    # Pagination
    paginator = Paginator(products_list, 12)
    products = paginator.get_page(request.GET.get('page'))
    
    all_categories = Category.objects.filter(is_active=True)

    context = {
        'products': products,
        'categories': all_categories,
        'selected_category_slug': selected_category_slug,
        'search_query': search_query,
    }
    
    return render(request, 'pages/store.html', context)

def product_detail(request, slug):
    """Affiche les détails d'un seul produit."""
    product = get_object_or_404(Product.objects.filter(is_active=True), slug=slug)
    context = {'product': product}
    return render(request, 'pages/product_detail.html', context)

# ===================================================================
# VUES POUR LE PANIER (CART)
# ===================================================================
def cart(request):
    """Affiche la page du panier."""
    cart = _get_cart(request)
    cart_items = cart.items.select_related('product', 'product__seller').prefetch_related('product__images')
    cart_total = sum(item.total_price for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'pages/cart.html', context)

def get_cart_count(request):
    """Renvoie le nombre total d'articles dans le panier (pour AJAX)."""
    cart = _get_cart(request)
    total_items = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
    return JsonResponse({'cart_item_count': total_items})

@require_POST
def add_to_cart(request):
    """Ajoute un produit au panier ou met à jour sa quantité (pour AJAX)."""
    cart = _get_cart(request)
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    total_items = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        
    return JsonResponse({
        'status': 'ok',
        'message': f'"{product.name}" a été ajouté au panier.',
        'cart_item_count': total_items 
    })

@require_POST
def update_cart(request):
    """Met à jour la quantité d'un article sur la page panier (pour AJAX)."""
    cart = _get_cart(request)
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity'))
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    cart_total = sum(item.total_price for item in cart.items.all())
    total_items = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        
    return JsonResponse({
        'status': 'ok',
        'item_subtotal': f'{cart_item.total_price:.2f} HTG',
        'cart_total': f'{cart_total:.2f} HTG',
        'cart_item_count': total_items
    })

@require_POST
def remove_from_cart(request):
    """Supprime un article du panier sur la page panier (pour AJAX)."""
    cart = _get_cart(request)
    product_id = request.POST.get('product_id')
    get_object_or_404(CartItem, cart=cart, product_id=product_id).delete()

    cart_total = sum(item.total_price for item in cart.items.all())
    total_items = cart.items.aggregate(total=Sum('quantity'))['total'] or 0

    return JsonResponse({
        'status': 'ok',
        'cart_total': f'{cart_total:.2f} HTG',
        'cart_item_count': total_items
    })

# ==========================================================================
# VUES POUR LE CHECKOUT ET MONCASH
# ==========================================================================

def checkout(request):
    """Vue pour la page de paiement."""
    cart = _get_cart(request)
    cart_items = cart.items.select_related('product').prefetch_related('product__images').all()
    cart_total = sum(item.total_price for item in cart_items)
    
    if not cart_items:
        return redirect('cart')
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'pages/checkout.html', context)

@require_POST
def process_payment(request):
    """Traite le paiement MonCash (AJAX)"""
    try:
        # Récupération des données du panier
        cart = _get_cart(request)
        cart_items = cart.items.select_related('product').all()
        
        if not cart_items:
            return JsonResponse({'success': False, 'error': 'Panier vide'})
        
        total_amount = sum(item.total_price for item in cart_items)
        
        if total_amount <= 0:
            return JsonResponse({'success': False, 'error': 'Montant invalide'})
        
        # Obtenir le token d'accès
        access_token = get_moncash_access_token()
        if not access_token:
            return JsonResponse({'success': False, 'error': 'Erreur d\'authentification MonCash'})
        
        # Génération d'un orderId unique
        order_id = str(uuid.uuid4())
        
        # Préparation de la requête selon la documentation
        api_url = f"{MONCASH_API_URL}/v1/CreatePayment"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        payment_data = {
            'amount': int(total_amount),  # MonCash attend un entier
            'orderId': order_id
        }
        
        # Envoi de la requête
        response = requests.post(api_url, headers=headers, json=payment_data)
        
        if response.status_code == 202:  # Succès selon la doc
            response_data = response.json()
            payment_token = response_data.get('payment_token', {}).get('token')
            
            if payment_token:
                # Sauvegarde des informations de commande en session
                cart_items_data = []
                for item in cart_items:
                    cart_items_data.append({
                        'product_id': item.product.id,
                        'quantity': item.quantity,
                        'price': float(item.product.price),
                        'name': item.product.name
                    })
                
                request.session['order_data'] = {
                    'order_id': order_id,
                    'total_amount': float(total_amount),
                    'payment_token': payment_token,
                    'cart_items': cart_items_data
                }
                
                # URL de redirection selon la documentation
                redirect_url = f"{MONCASH_GATEWAY_URL}/Payment/Redirect?token={payment_token}"
                
                return JsonResponse({
                    'success': True,
                    'redirect_url': redirect_url,
                    'order_id': order_id
                })
            else:
                logger.error(f"Token de paiement manquant dans la réponse: {response_data}")
                return JsonResponse({'success': False, 'error': 'Token de paiement non reçu'})
        else:
            logger.error(f"Erreur API MonCash: {response.status_code} - {response.text}")
            return JsonResponse({'success': False, 'error': 'Erreur lors de la création du paiement'})
            
    except Exception as e:
        logger.error(f"Erreur dans process_payment: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Erreur interne du serveur'})

def moncash_return(request):
    """Gestion du retour après paiement MonCash"""
    try:
        # Récupération des paramètres de retour
        transaction_id = request.GET.get('transactionId')
        order_data = request.session.get('order_data')
        
        if not transaction_id or not order_data:
            logger.warning("Données manquantes lors du retour MonCash")
            return redirect('checkout')
        
        # Vérification du paiement via l'API
        payment_verified = verify_payment_by_transaction(transaction_id)
        
        if payment_verified and payment_verified.get('status') == 200:
            payment_details = payment_verified.get('payment', {})
            
            if payment_details.get('message') == 'successful':
                # Création de la commande
                order = create_order_from_session(request, transaction_id, payment_details)
                
                if order:
                    # Nettoyage du panier et de la session
                    cart = _get_cart(request)
                    cart.items.all().delete()
                    request.session.pop('order_data', None)
                    
                    # Sauvegarde de l'ID de commande pour la page de succès
                    request.session['last_order_id'] = order.order_id
                    
                    return redirect('success')
                else:
                    logger.error("Erreur lors de la création de la commande")
                    return redirect('checkout')
            else:
                logger.warning(f"Paiement non réussi: {payment_details}")
                return redirect('checkout')
        else:
            logger.error(f"Échec de la vérification du paiement: {payment_verified}")
            return redirect('checkout')
            
    except Exception as e:
        logger.error(f"Erreur dans moncash_return: {str(e)}")
        return redirect('checkout')

@csrf_exempt
def moncash_notify(request):
    """Gestion des notifications MonCash (webhook)"""
    if request.method == 'POST':
        try:
            # Log de la notification reçue
            logger.info(f"Notification MonCash reçue: {request.body}")
            
            # Traitement de la notification si nécessaire
            # (validation supplémentaire, mise à jour du statut, etc.)
            
            return HttpResponse("OK", status=200)
            
        except Exception as e:
            logger.error(f"Erreur dans moncash_notify: {str(e)}")
            return HttpResponse("Error", status=500)
    
    return HttpResponse("Method not allowed", status=405)

def success(request):
    """Vue pour la page de succès de commande."""
    order_id = request.session.get('last_order_id')
    context = {
        'order': {'id': order_id or 'AF-12345'}
    }
    # Nettoyage de la session
    request.session.pop('last_order_id', None)
    return render(request, 'pages/success.html', context)

# ==========================================================================
# VUES POUR LES COMBOS (si applicable)
# ==========================================================================

def combo_detail(request, combo_id):
    """Vue pour les détails d'un combo"""
    # Implémentation selon vos besoins
    pass

@require_POST
def add_combo_to_cart(request):
    """Ajouter un combo au panier"""
    # Implémentation selon vos besoins
    pass

@require_POST
def update_combo_cart(request):
    """Mettre à jour un combo dans le panier"""
    # Implémentation selon vos besoins
    pass

@require_POST
def remove_combo_from_cart(request):
    """Supprimer un combo du panier"""
    # Implémentation selon vos besoins
    pass

# ==========================================================================
# VUES UTILISATEUR
# ==========================================================================

def orders(request):
    """Vue pour la page d'historique des commandes."""
    # Si l'utilisateur est connecté, récupérer ses vraies commandes
    if request.user.is_authenticated:
        user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    else:
        user_orders = []
    
    context = {
        'user_orders': user_orders,
        'user': request.user if request.user.is_authenticated else {'username': 'Invité', 'first_name': 'Invité'}
    }
    return render(request, 'pages/user/orders.html', context)

def track_order(request, order_id):
    """Vue pour la page de suivi de commande."""
    try:
        if request.user.is_authenticated:
            order = get_object_or_404(Order, order_id=order_id, user=request.user)
        else:
            order = get_object_or_404(Order, order_id=order_id)
        
        context = {
            'order': order,
            'user': request.user if request.user.is_authenticated else {'username': 'Invité', 'first_name': 'Invité'}
        }
    except Order.DoesNotExist:
        # Données d'exemple si la commande n'existe pas
        context = {
            'order': {
                'id': order_id,
                'created_at': datetime.datetime.now(),
                'status': 'not_found',
                'items': {'all': []}
            },
            'user': {'username': 'Invité', 'first_name': 'Invité'}
        }
    
    return render(request, 'pages/user/track_order.html', context)