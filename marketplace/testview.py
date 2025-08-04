from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
import requests
import uuid
from decimal import Decimal


def homewert(request):

    
    return render(request, 'pages/home.html')






# Données des produits en dur pour le MVP
PRODUCTS_DATA = {
    'necessite': [
        {
            'id': 1, 'name': 'Sac de Riz Premium', 'price': 1500, 'slug': 'sac-de-riz',
            'image': 'https://f005.backblazeb2.com/file/afepanou/produits/premiere-necessite/sac_de_riz.png',
            'description': 'Riz de qualité supérieure, idéal pour toute la famille.',
            'category': 'necessite', 'stock': 50
        },
        {
            'id': 2, 'name': 'Café Haïtien', 'price': 450, 'slug': 'cafe-haitien',
            'image': 'https://f005.backblazeb2.com/file/afepanou/produits/premiere-necessite/cafe_haitien.png',
            'description': 'Café 100% haïtien, torréfié localement.',
            'category': 'necessite', 'stock': 30
        },
        {
            'id': 3, 'name': 'Bouteille d\'Huile', 'price': 350, 'slug': 'bouteille-huile',
            'image': 'https://f005.backblazeb2.com/file/afepanou/produits/premiere-necessite/bouteille_huile.png',
            'description': 'Huile de cuisson de qualité premium.',
            'category': 'necessite', 'stock': 25
        },
        {
            'id': 4, 'name': 'Conserve Haricots Noirs', 'price': 125, 'slug': 'haricots-noirs',
            'image': 'https://f005.backblazeb2.com/file/afepanou/produits/premiere-necessite/conserve_haricots_noirs.png',
            'description': 'Haricots noirs en conserve, prêts à consommer.',
            'category': 'necessite', 'stock': 60
        },
        {
            'id': 15, 'name': 'Huile Végétale Soleil', 'price': 400, 'slug': 'huile-vegetale-soleil',
            'image': 'https://f005.backblazeb2.com/file/afepanou/bestproduct/huile-vegetale-soleil.jpg',
            'description': 'Huile végétale de tournesol, parfaite pour la cuisson.',
            'category': 'necessite', 'stock': 40
        }
    ],
    'patriotique': [
        {
            'id': 5, 'name': 'T-shirt Drapeau Haïti', 'price': 800, 'slug': 'tshirt-drapeau-haiti',
            'image': 'https://f005.backblazeb2.com/file/afepanou/produits/patriotiques/tshirt_drapeau_haiti.png',
            'description': 'T-shirt avec le drapeau haïtien, made in Haiti.',
            'category': 'patriotique', 'stock': 20
        },
        {
            'id': 6, 'name': 'Bracelet Haïti', 'price': 250, 'slug': 'bracelet-haiti',
            'image': 'https://f005.backblazeb2.com/file/afepanou/produits/patriotiques/bracelet_haiti.png',
            'description': 'Bracelet aux couleurs d\'Haïti, fait main.',
            'category': 'patriotique', 'stock': 35
        },
        {
            'id': 16, 'name': 'Art Haïtien', 'price': 2500, 'slug': 'art-haitien',
            'image': 'https://f005.backblazeb2.com/file/afepanou/featured/artistehaitien.png',
            'description': 'Œuvre d\'art authentique d\'un artiste haïtien.',
            'category': 'patriotique', 'stock': 5
        }
    ],
    'artisanat': [
        {
            'id': 7, 'name': 'Sac Paille Tressée', 'price': 750, 'slug': 'sac-paille-tressee',
            'image': 'https://f005.backblazeb2.com/file/afepanou/produits/locaux/artisanat/sac_paille_tressee.png',
            'description': 'Sac artisanal en paille tressée, fait main par nos artisans.',
            'category': 'artisanat', 'stock': 15
        },
        {
            'id': 8, 'name': 'Vase Céramique Peint', 'price': 1200, 'slug': 'vase-ceramique-peint',
            'image': 'https://f005.backblazeb2.com/file/afepanou/produits/locaux/artisanat/vase_ceramique_peint.png',
            'description': 'Vase en céramique peint à la main, pièce unique.',
            'category': 'artisanat', 'stock': 8
        }
    ],
    'industrie': [
        {
            'id': 9, 'name': 'Huile Vétiver', 'price': 950, 'slug': 'huile-vetiver',
            'image': 'https://f005.backblazeb2.com/file/afepanou/produits/locaux/petite-industrie/huile_vetiver.png',
            'description': 'Huile essentielle de vétiver, production locale.',
            'category': 'industrie', 'stock': 12
        },
        {
            'id': 10, 'name': 'Savon Palma Christi', 'price': 175, 'slug': 'savon-palma-christi',
            'image': 'https://f005.backblazeb2.com/file/afepanou/produits/locaux/petite-industrie/savon_palma_christi.png',
            'description': 'Savon naturel à base d\'huile de ricin, fait localement.',
            'category': 'industrie', 'stock': 25
        }
    ],
    'agricole': [
        {
            'id': 11, 'name': 'Pot de Miel', 'price': 650, 'slug': 'pot-de-miel',
            'image': 'https://f005.backblazeb2.com/file/afepanou/produits/locaux/agricole/pot_de_miel.png',
            'description': 'Miel pur d\'abeilles, récolté dans nos montagnes.',
            'category': 'agricole', 'stock': 18
        }
    ],
    'services': [
        {
            'id': 12, 'name': 'Cours d\'Anglais', 'price': 3000, 'slug': 'cours-anglais',
            'image': 'https://f005.backblazeb2.com/file/afepanou/Store%20Services%20Divers/coursanglais.png',
            'description': 'Cours d\'anglais privés avec professeur certifié.',
            'category': 'services', 'stock': 10
        },
        {
            'id': 13, 'name': 'Service de Ménage Privé', 'price': 1500, 'slug': 'service-menage-prive',
            'image': 'https://f005.backblazeb2.com/file/afepanou/Store%20Services%20Divers/metoyageserviceprivee.png',
            'description': 'Service de ménage professionnel à domicile.',
            'category': 'services', 'stock': 20
        }
    ]
}

# Configuration MonCash pour le MVP
# Configuration MonCash pour le MVP
MONCASH_CONFIG = {
    'client_id': 'c3f63f2c606c95b19c5ae016c6c19a51',  # À remplacer
    'client_secret': 'K005ijmj/3GKsMRYdBDvFBiQgKuNhJc',  # À remplacer
    'sandbox_base_url': 'https://sandbox.moncashbutton.digicelgroup.com',
    'live_base_url': 'https://moncashbutton.digicelgroup.com',
    'is_sandbox': True  # Changer en False pour la production
}

def get_all_products():
    """Retourne tous les produits avec leurs catégories"""
    all_products = []
    for category, products in PRODUCTS_DATA.items():
        for product in products:
            product['category_name'] = category
            all_products.append(product)
    return all_products

def get_product_by_id(product_id):
    """Trouve un produit par son ID"""
    for category, products in PRODUCTS_DATA.items():
        for product in products:
            if product['id'] == product_id:
                return product
    return None

def get_product_by_slug(slug):
    """Trouve un produit par son slug"""
    for category, products in PRODUCTS_DATA.items():
        for product in products:
            if product['slug'] == slug:
                return product
    return None

def get_products_by_category(category):
    """Retourne les produits d'une catégorie"""
    if category == 'locaux':
        # Pour la catégorie "locaux", on combine artisanat, industrie et agricole
        products = []
        products.extend(PRODUCTS_DATA.get('artisanat', []))
        products.extend(PRODUCTS_DATA.get('industrie', []))
        products.extend(PRODUCTS_DATA.get('agricole', []))
        return products
    return PRODUCTS_DATA.get(category, [])

def get_cart_from_session(request):
    """Récupère le panier de la session"""
    cart = request.session.get('cart', {})
    return cart

def get_cart_count(request):
    """Retourne le nombre total d'articles dans le panier"""
    cart = get_cart_from_session(request)
    return sum(cart.values())

def get_cart_items(request):
    """Retourne les items du panier avec les détails des produits"""
    cart = get_cart_from_session(request)
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        product = get_product_by_id(int(product_id))
        if product:
            item_total = product['price'] * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': item_total
            })
            total += item_total
    
    return cart_items, total

def get_moncash_token():
    """Obtient le token MonCash pour l'authentification"""
    base_url = MONCASH_CONFIG['sandbox_base_url'] if MONCASH_CONFIG['is_sandbox'] else MONCASH_CONFIG['live_base_url']
    url = f"{base_url}/Api/oauth/token"
    
    auth = (MONCASH_CONFIG['client_id'], MONCASH_CONFIG['client_secret'])
    data = {
        'scope': 'read,write',
        'grant_type': 'client_credentials'
    }
    
    try:
        response = requests.post(url, auth=auth, data=data, timeout=10)
        if response.status_code == 200:
            return response.json().get('access_token')
    except requests.RequestException:
        pass
    return None

def create_moncash_payment(order_id, amount):
    """Crée un paiement MonCash"""
    token = get_moncash_token()
    if not token:
        return None
    
    base_url = MONCASH_CONFIG['sandbox_base_url'] if MONCASH_CONFIG['is_sandbox'] else MONCASH_CONFIG['live_base_url']
    url = f"{base_url}/Api/v1/CreatePayment"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    data = {
        'amount': int(amount),
        'orderId': str(order_id)
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 202:
            return response.json()
    except requests.RequestException:
        pass
    return None

# VIEWS

def store(request):
    """Vue principale du store avec filtres"""
    category = request.GET.get('category', 'all')
    search_query = request.GET.get('q', '')
    
    # Récupération des produits selon la catégorie
    if category == 'all':
        products = get_all_products()
    else:
        products = get_products_by_category(category)
    
    # Filtrage par recherche
    if search_query:
        products = [p for p in products if search_query.lower() in p['name'].lower()]
    
    # Catégories pour les filtres
    categories = [
        {'name': 'Nécessités', 'slug': 'necessite'},
        {'name': 'Patriotique', 'slug': 'patriotique'},
        {'name': 'Artisanat', 'slug': 'artisanat'},
        {'name': 'Industrie', 'slug': 'industrie'},
        {'name': 'Agricole', 'slug': 'agricole'},
        {'name': 'Services', 'slug': 'services'},
    ]
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category_slug': category if category != 'all' else None,
        'search_query': search_query,
        'cart_item_count': get_cart_count(request)
    }
    
    return render(request, 'pages/store.html', context)

def product_detail(request, slug):
    """Vue détail d'un produit"""
    product = get_product_by_slug(slug)
    if not product:
        messages.error(request, 'Produit non trouvé.')
        return redirect('store')
    
    context = {
        'product': product,
        'cart_item_count': get_cart_count(request)
    }
    
    return render(request, 'product_detail.html', context)

@csrf_exempt
def add_to_cart(request):
    """Ajoute un produit au panier via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = int(data.get('product_id'))
            quantity = int(data.get('quantity', 1))
            
            product = get_product_by_id(product_id)
            if not product:
                return JsonResponse({'status': 'error', 'message': 'Produit non trouvé'})
            
            # Gestion du panier en session
            cart = request.session.get('cart', {})
            product_id_str = str(product_id)
            
            if product_id_str in cart:
                cart[product_id_str] += quantity
            else:
                cart[product_id_str] = quantity
            
            request.session['cart'] = cart
            
            return JsonResponse({
                'status': 'success',
                'message': 'Produit ajouté au panier',
                'cart_item_count': sum(cart.values())
            })
            
        except (ValueError, json.JSONDecodeError):
            return JsonResponse({'status': 'error', 'message': 'Données invalides'})
    
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'})

def cart(request):
    """Vue du panier"""
    cart_items, cart_total = get_cart_items(request)
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_item_count': get_cart_count(request)
    }
    
    return render(request, 'pages/cart.html', context)

@csrf_exempt
def update_cart(request):
    """Met à jour la quantité d'un produit dans le panier"""
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            
            if quantity < 1:
                return JsonResponse({'status': 'error', 'message': 'Quantité invalide'})
            
            cart = request.session.get('cart', {})
            if product_id in cart:
                cart[product_id] = quantity
                request.session['cart'] = cart
                
                # Recalcul des totaux
                product = get_product_by_id(int(product_id))
                item_subtotal = f"{product['price'] * quantity} HTG"
                
                cart_items, cart_total = get_cart_items(request)
                
                return JsonResponse({
                    'status': 'ok',
                    'item_subtotal': item_subtotal,
                    'cart_total': f"{cart_total} HTG",
                    'cart_item_count': sum(cart.values())
                })
            
        except (ValueError, TypeError):
            pass
    
    return JsonResponse({'status': 'error', 'message': 'Erreur lors de la mise à jour'})

@csrf_exempt
def remove_from_cart(request):
    """Supprime un produit du panier"""
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product_id')
            
            cart = request.session.get('cart', {})
            if product_id in cart:
                del cart[product_id]
                request.session['cart'] = cart
                
                cart_items, cart_total = get_cart_items(request)
                
                return JsonResponse({
                    'status': 'ok',
                    'cart_total': f"{cart_total} HTG",
                    'cart_item_count': sum(cart.values())
                })
            
        except Exception:
            pass
    
    return JsonResponse({'status': 'error', 'message': 'Erreur lors de la suppression'})

def checkout(request):
    """Vue de finalisation de commande"""
    cart_items, cart_total = get_cart_items(request)
    
    if not cart_items:
        messages.error(request, 'Votre panier est vide.')
        return redirect('cart')
    
    if request.method == 'POST':
        # Récupération des données du formulaire
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        commune = request.POST.get('commune')
        department = request.POST.get('department')
        phone = request.POST.get('phone')
        payment_method = request.POST.get('payment_method')
        
        if not all([full_name, address, commune, department, phone, payment_method]):
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'pages/checkout.html', {
                'cart_items': cart_items,
                'cart_total': cart_total,
                'cart_item_count': get_cart_count(request)
            })
        
        if payment_method == 'moncash':
            # Génération d'un order_id unique
            order_id = str(uuid.uuid4())[:8].upper()
            
            # Création du paiement MonCash
            payment_response = create_moncash_payment(order_id, cart_total)
            
            if payment_response and 'payment_token' in payment_response:
                # Sauvegarde de la commande en session
                request.session['pending_order'] = {
                    'order_id': order_id,
                    'full_name': full_name,
                    'address': address,
                    'commune': commune,
                    'department': department,
                    'phone': phone,
                    'cart_items': cart_items,
                    'total': cart_total,
                    'payment_token': payment_response['payment_token']['token']
                }
                
                # Redirection vers MonCash
                base_url = MONCASH_CONFIG['sandbox_base_url'] if MONCASH_CONFIG['is_sandbox'] else MONCASH_CONFIG['live_base_url']
                payment_url = f"{base_url}/Moncash-middleware/Payment/Redirect?token={payment_response['payment_token']['token']}"
                
                return redirect(payment_url)
            else:
                messages.error(request, 'Erreur lors de l\'initialisation du paiement MonCash.')
        else:
            messages.error(request, 'Méthode de paiement non supportée pour le moment.')
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_item_count': get_cart_count(request)
    }
    
    return render(request, 'pages/checkout.html', context)

def success(request):
    """Page de succès après paiement"""
    # Récupération de la commande en attente
    pending_order = request.session.get('pending_order')
    
    if not pending_order:
        messages.error(request, 'Aucune commande en cours.')
        return redirect('store')
    
    # Simulation de la validation du paiement
    # Dans un vrai système, il faudrait vérifier le paiement avec l'API MonCash
    
    # Création de l'objet order pour l'affichage
    order = {
        'id': pending_order['order_id'],
        'total': pending_order['total'],
        'status': 'completed'
    }
    
    # Vider le panier et la commande en attente
    request.session['cart'] = {}
    del request.session['pending_order']
    
    context = {
        'order': order,
        'cart_item_count': 0
    }
    
    return render(request, 'pages/success.html', context)

def home(request):
    """Page d'accueil - redirection vers le store"""
    return redirect('store')

# Vue pour les orders (mentionnée dans success.html)
def orders(request):
    """Liste des commandes utilisateur"""
    # Pour le MVP, redirection vers le store
    messages.info(request, 'Fonctionnalité des commandes en développement.')
    return redirect('store')

# ENDPOINTS MONCASH REQUIS

@csrf_exempt
def moncash_return(request):
    """Endpoint de retour MonCash après paiement (succès ou échec)"""
    # MonCash redirige ici après le paiement
    transaction_id = request.GET.get('transactionId')
    
    if transaction_id:
        # Paiement réussi - vérifier le statut
        token = get_moncash_token()
        if token:
            # Vérification du paiement avec l'API MonCash
            base_url = MONCASH_CONFIG['sandbox_base_url'] if MONCASH_CONFIG['is_sandbox'] else MONCASH_CONFIG['live_base_url']
            url = f"{base_url}/Api/v1/RetrieveTransactionPayment"
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            data = {'transactionId': transaction_id}
            
            try:
                response = requests.post(url, headers=headers, json=data, timeout=10)
                if response.status_code == 200:
                    payment_data = response.json()
                    if payment_data.get('payment', {}).get('message') == 'successful':
                        # Paiement confirmé - rediriger vers success
                        return redirect('success')
            except requests.RequestException:
                pass
    
    # En cas d'erreur ou paiement échoué
    messages.error(request, 'Le paiement a échoué ou a été annulé.')
    return redirect('checkout')

@csrf_exempt
def moncash_notify(request):
    """Endpoint de notification MonCash (webhook)"""
    if request.method == 'POST':
        try:
            # MonCash envoie les données de notification ici
            data = json.loads(request.body)
            
            transaction_id = data.get('transactionId')
            order_id = data.get('reference')  # Votre order_id
            status = data.get('message')
            
            # Log des données reçues (pour debug)
            print(f"MonCash Notification: Transaction {transaction_id}, Order {order_id}, Status: {status}")
            
            # Ici vous pouvez mettre à jour le statut de la commande dans votre base
            # Pour le MVP, on fait juste un log
            
            # Répondre OK à MonCash
            return JsonResponse({'status': 'received'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)