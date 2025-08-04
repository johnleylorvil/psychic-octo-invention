from django.shortcuts import render
import datetime
from .models import Banner, Product, MediaContentSection
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q, Sum

# Assurez-vous d'importer tous vos modèles depuis le bon endroit
from .models import Product, Category, ProductImage, Cart, CartItem, User
# ==========================================================================
# VUES PRINCIPALES
# ==========================================================================

def home(request):
    """
    Affiche la page d'accueil avec :
    - Un slideshow de bannières.
    - Une section "collage" avec des images de produits aléatoires.
    - Une grille de produits vedettes sélectionnés aléatoirement.
    """

    # --- 1. Bannières pour le Slideshow ---
    # On récupère toutes les bannières actives, triées par ordre d'apparition.
    banners = Banner.objects.filter(is_active=True).order_by('sort_order')


    # --- 2. Images pour la Section "Collage" (Section 3) ---
    # On sélectionne 3 produits actifs au hasard qui ont au moins une image.
    # Note : Le template a 3 emplacements, nous prenons donc 3 produits.
    collage_products = Product.objects.filter(
        is_active=True, 
        images__isnull=False
    ).distinct().order_by('?')[:3]

    # On prépare les URLs des images pour le contexte, en gérant les cas où il n'y a pas assez de produits.
    def get_product_image_url(product):
        if not product:
            return None
        # On privilégie l'image principale, sinon on prend la première disponible.
        image = product.images.filter(is_primary=True).first() or product.images.first()
        return image.image_url if image else None

    collage_image_1 = get_product_image_url(collage_products[0] if len(collage_products) > 0 else None)
    collage_image_2 = get_product_image_url(collage_products[1] if len(collage_products) > 1 else None)
    collage_image_3 = get_product_image_url(collage_products[2] if len(collage_products) > 2 else None)


    # --- 3. Produits Vedettes (aléatoires) ---
    # On récupère jusqu'à 8 produits vedettes actifs, sélectionnés au hasard.
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).order_by('?')[:8]


    # --- 4. Contexte final pour le template ---
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
    Version corrigée qui utilise correctement request.session.session_key.
    """
    if request.user.is_authenticated:
        # Pour un utilisateur connecté, on utilise son compte pour trouver le panier
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
    else:
        # Pour un visiteur anonyme, on utilise la clé de session de Django
        session_key = request.session.session_key
        if not session_key:
            # Si la session n'a pas de clé (premier visiteur), on la crée
            request.session.create()
            session_key = request.session.session_key
        
        # On trouve ou on crée le panier en utilisant cette clé de session unique
        cart, created = Cart.objects.get_or_create(session_id=session_key, user=None, defaults={'is_active': True})
    return cart


# ===================================================================
# VUES POUR LA BOUTIQUE (STORE)
# ===================================================================
def store(request):
    """
    Affiche la page principale de la boutique avec filtres, recherche,
    et gestion des catégories parent/enfant.
    """
    # 1. Requête de base optimisée pour la performance
    primary_image_prefetch = Prefetch('images', queryset=ProductImage.objects.filter(is_primary=True), to_attr='primary_image_list')
    products_list = Product.objects.filter(is_active=True).select_related('category', 'seller').prefetch_related(primary_image_prefetch)

    # 2. Filtrage par Catégorie (avec gestion des sous-catégories)
    selected_category_slug = request.GET.get('category')
    if selected_category_slug:
        try:
            category = get_object_or_404(Category, slug=selected_category_slug)
            child_categories = category.children.all()
            category_ids = [category.id] + [child.id for child in child_categories]
            products_list = products_list.filter(category__id__in=category_ids)
        except:
            products_list = products_list.none() # N'affiche aucun produit si le slug est invalide

    # 3. Filtrage par Recherche (paramètre 'q')
    search_query = request.GET.get('q')
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        ).distinct()

    # 4. Tri
    sort_option = request.GET.get('sort')
    if sort_option == 'price_asc':
        products_list = products_list.order_by('price')
    elif sort_option == 'price_desc':
        products_list = products_list.order_by('-price')
    elif sort_option == 'date_desc':
        products_list = products_list.order_by('-created_at')

    # 5. Pagination
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
def cart_detail(request):
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


def checkout(request):
    """Vue pour la page de paiement."""
    # Réutilisation des mêmes données que le panier pour le résumé
    product1 = {'id': 1, 'name': 'Café Haïtien Selecto', 'price': 500, 'image': {'url': 'https://via.placeholder.com/100x100.png/CC6B49/FFFFFF'}, 'get_absolute_url': '/product/1/'}
    product2 = {'id': 2, 'name': 'Sculpture en Fer Découpé', 'price': 3500, 'image': {'url': 'https://via.placeholder.com/100x100.png/333333/FFFFFF'}, 'get_absolute_url': '/product/2/'}
    
    cart_items = [
        {'product': product1, 'quantity': 2, 'get_total': 1000},
        {'product': product2, 'quantity': 1, 'get_total': 3500},
    ]
    cart_total = sum(item['get_total'] for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'pages/checkout.html', context)


def success(request):
    """Vue pour la page de succès de commande."""
    # Données d'exemple pour une commande
    context = {
        'order': {'id': 'AF-12345'}
    }
    return render(request, 'pages/success.html', context)


# ==========================================================================
# VUES D'AUTHENTIFICATION
# ==========================================================================

def login_view(request):
    """Vue pour la page de connexion."""
    return render(request, 'pages/auth/login.html')


def register_view(request):
    """Vue pour la page d'inscription."""
    return render(request, 'pages/auth/register.html')


# ==========================================================================
# VUES UTILISATEUR
# ==========================================================================

def account(request):
    """Vue pour la page de compte utilisateur."""
    # Faux objet utilisateur pour le rendu
    context = {
        'user': {
            'username': 'jdupont',
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'email': 'jean.dupont@example.com'
        }
    }
    return render(request, 'pages/user/account.html', context)


def orders(request):
    """Vue pour la page d'historique des commandes."""
    # Données d'exemple pour l'historique des commandes
    user_orders = [
        {'id': 'AF-12345', 'created_at': datetime.date(2025, 7, 28), 'total': 4500, 'status': 'delivered', 'get_status_display': 'Livrée', 'estimated_delivery': datetime.date(2025, 8, 1)},
        {'id': 'AF-12358', 'created_at': datetime.date(2025, 8, 1), 'total': 800, 'status': 'shipped', 'get_status_display': 'Expédiée', 'estimated_delivery': datetime.date(2025, 8, 4)},
    ]
    context = {
        'user_orders': user_orders,
        'user': {'username': 'jdupont', 'first_name': 'Jean'}
    }
    return render(request, 'pages/user/orders.html', context)


def track_order(request, order_id):
    """Vue pour la page de suivi de commande."""
    # Données d'exemple pour une commande spécifique
    product1 = {'id': 1, 'name': 'Café Haïtien Selecto', 'price': 500, 'image': {'url': 'https://via.placeholder.com/100x100.png/CC6B49/FFFFFF'}, 'quantity': 2}
    
    order_data = {
        'id': order_id,
        'created_at': datetime.datetime(2025, 8, 1, 10, 30),
        'status': 'shipped', # Statuts possibles: 'confirmed', 'processing', 'shipped', 'delivered'
        'items': { 'all': [product1] } # Simule la relation order.items.all
    }
    context = {
        'order': order_data,
        'user': {'username': 'jdupont', 'first_name': 'Jean'}
    }
    return render(request, 'pages/user/track_order.html', context)