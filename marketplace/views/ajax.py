# marketplace/views/ajax.py
"""
AJAX-powered interactive views for Afèpanou marketplace
"""

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.db.models import Q

from ..models import Product, Cart, CartItem, Category, User, Wishlist
from ..services import CartService, ProductService


@require_POST
@login_required
def add_to_cart_ajax(request):
    """Add product to cart via AJAX"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        if quantity <= 0:
            return JsonResponse({
                'success': False,
                'error': _('Quantity must be greater than 0')
            })
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check availability
        if not ProductService.check_availability(product, quantity):
            return JsonResponse({
                'success': False,
                'error': _('Product is not available in requested quantity')
            })
        
        # Get or create cart
        cart = CartService.get_or_create_cart(user=request.user)
        
        # Add to cart
        cart_item = CartService.add_to_cart(cart, product, quantity)
        
        # Calculate cart totals
        cart_totals = CartService.calculate_cart_totals(cart)
        
        return JsonResponse({
            'success': True,
            'message': _('Product added to cart successfully'),
            'cart_count': cart_totals['total_items'],
            'cart_total': str(cart_totals['total']),
            'product_name': product.name
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_POST
@login_required
def update_cart_ajax(request):
    """Update cart item quantity via AJAX"""
    try:
        data = json.loads(request.body)
        cart_item_id = data.get('cart_item_id')
        quantity = int(data.get('quantity', 0))
        
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
        
        if quantity <= 0:
            # Remove item
            cart_item.delete()
            message = _('Item removed from cart')
        else:
            # Update quantity
            cart_item = CartService.update_cart_item(cart_item, quantity)
            message = _('Cart updated successfully')
        
        # Calculate new totals
        cart_totals = CartService.calculate_cart_totals(cart_item.cart)
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_count': cart_totals['total_items'],
            'cart_subtotal': str(cart_totals['subtotal']),
            'cart_total': str(cart_totals['total']),
            'item_total': str(cart_item.unit_price * cart_item.quantity) if cart_item else '0'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_POST
@login_required
def toggle_wishlist_ajax(request):
    """Toggle product in wishlist via AJAX"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        if wishlist.has_product(product):
            wishlist.remove_product(product)
            in_wishlist = False
            message = _('Removed from wishlist')
        else:
            wishlist.add_product(product)
            in_wishlist = True
            message = _('Added to wishlist')
        
        return JsonResponse({
            'success': True,
            'in_wishlist': in_wishlist,
            'message': message,
            'wishlist_count': wishlist.item_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_GET
def product_quick_view_ajax(request, product_id):
    """Get product quick view data via AJAX"""
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Render quick view template
        html = render_to_string('components/product_quick_view.html', {
            'product': product,
            'product_images': product.images.all()[:4],
            'user': request.user
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': html,
            'product_name': product.name,
            'product_price': str(product.current_price)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_GET
def search_autocomplete_ajax(request):
    """Product search autocomplete via AJAX"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Search products
    products = Product.objects.search(query)[:10]
    
    # Search categories
    categories = Category.objects.filter(
        name__icontains=query,
        is_active=True
    )[:5]
    
    results = []
    
    # Add product results
    for product in products:
        results.append({
            'type': 'product',
            'id': product.id,
            'name': product.name,
            'url': product.get_absolute_url(),
            'image': product.primary_image.image_url if product.primary_image else None,
            'price': str(product.current_price),
            'category': product.category.name
        })
    
    # Add category results
    for category in categories:
        results.append({
            'type': 'category',
            'id': category.id,
            'name': category.name,
            'url': category.get_absolute_url(),
            'product_count': category.product_count
        })
    
    return JsonResponse({'results': results})


@require_POST
@login_required
def remove_cart_item_ajax(request):
    """Remove item from cart via AJAX"""
    try:
        data = json.loads(request.body)
        cart_item_id = data.get('cart_item_id')
        
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
        cart = cart_item.cart
        cart_item.delete()
        
        # Calculate new totals
        cart_totals = CartService.calculate_cart_totals(cart)
        
        return JsonResponse({
            'success': True,
            'message': _('Item removed from cart'),
            'cart_count': cart_totals['total_items'],
            'cart_subtotal': str(cart_totals['subtotal']),
            'cart_total': str(cart_totals['total'])
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_GET
def product_filter_ajax(request):
    """Filter products via AJAX"""
    try:
        category_id = request.GET.get('category')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        brand = request.GET.get('brand')
        in_stock = request.GET.get('in_stock') == 'true'
        on_sale = request.GET.get('on_sale') == 'true'
        sort_by = request.GET.get('sort_by', 'relevance')
        
        # Start with available products
        queryset = Product.objects.available()
        
        # Apply filters
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            queryset = queryset.filter(category=category)
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        
        if in_stock:
            queryset = queryset.filter(stock_quantity__gt=0)
        
        if on_sale:
            queryset = queryset.filter(promotional_price__isnull=False)
        
        # Apply sorting
        if sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-average_rating')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-view_count')
        
        # Paginate results
        products = queryset[:20]  # Limit to 20 results
        
        # Render products template
        html = render_to_string('components/product_list_items.html', {
            'products': products
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': html,
            'count': queryset.count()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_GET
def get_cart_summary_ajax(request):
    """Get cart summary via AJAX"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': _('Authentication required')
        })
    
    try:
        cart = CartService.get_or_create_cart(user=request.user)
        cart_summary = CartService.get_cart_summary(cart)
        
        # Render cart summary template
        html = render_to_string('components/cart_summary.html', {
            'cart': cart_summary['cart'],
            'items': cart_summary['items'],
            'totals': cart_summary['totals']
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'html': html,
            'cart_count': cart_summary['totals']['total_items'],
            'cart_total': str(cart_summary['totals']['total'])
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_POST
def validate_form_field_ajax(request):
    """Validate individual form fields via AJAX"""
    try:
        data = json.loads(request.body)
        field_name = data.get('field_name')
        field_value = data.get('field_value')
        form_type = data.get('form_type')
        
        errors = []
        
        # Validate based on form type and field name
        if form_type == 'registration' and field_name == 'email':
            if User.objects.filter(email=field_value).exists():
                errors.append(_('This email address is already registered.'))
        
        elif form_type == 'registration' and field_name == 'username':
            if User.objects.filter(username=field_value).exists():
                errors.append(_('This username is already taken.'))
        
        # Add more field validations as needed
        
        return JsonResponse({
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_GET
def load_more_products_ajax(request):
    """Load more products for infinite scroll"""
    try:
        page = int(request.GET.get('page', 1))
        category_id = request.GET.get('category')
        query = request.GET.get('query', '')
        
        # Get products
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            products = Product.objects.by_category(category)
        elif query:
            products = ProductService.search_products(query)
        else:
            products = Product.objects.available()
        
        # Pagination
        start = (page - 1) * 20
        end = start + 20
        products = products[start:end]
        
        # Render products
        html = render_to_string('components/product_list_items.html', {
            'products': products
        }, request=request)
        
        has_more = len(products) == 20
        
        return JsonResponse({
            'success': True,
            'html': html,
            'has_more': has_more,
            'next_page': page + 1
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_POST
@login_required
def remove_from_cart_ajax(request):
    """Remove item from cart via AJAX"""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        
        # Get updated cart summary
        cart = CartService.get_or_create_cart(user=request.user)
        cart_summary = CartService.get_cart_summary(cart)
        
        return JsonResponse({
            'success': True,
            'message': _('Item removed from cart'),
            'cart_count': cart_summary['item_count'],
            'cart_total': str(cart_summary['total']),
            'cart_subtotal': str(cart_summary['subtotal'])
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_GET
def validate_address_ajax(request):
    """Validate address information via AJAX"""
    try:
        address_data = {
            'address_line_1': request.GET.get('address_line_1', ''),
            'city': request.GET.get('city', ''),
            'state': request.GET.get('state', ''),
            'postal_code': request.GET.get('postal_code', '')
        }
        
        # Basic validation for Haiti
        errors = {}
        
        if not address_data['address_line_1']:
            errors['address_line_1'] = _('Address line 1 is required')
        
        if not address_data['city']:
            errors['city'] = _('City is required')
        
        # Validate Haiti postal code format (if provided)
        if address_data['postal_code'] and not address_data['postal_code'].isdigit():
            errors['postal_code'] = _('Postal code must be numeric')
        
        # Check if city exists in Haiti
        haiti_cities = [
            'Port-au-Prince', 'Cap-Haïtien', 'Gonaïves', 'Les Cayes', 
            'Jacmel', 'Jérémie', 'Fort-de-France', 'Hinche'
        ]
        
        if address_data['city'] not in haiti_cities:
            # Still valid, but suggest corrections
            suggestions = [city for city in haiti_cities if 
                          address_data['city'].lower() in city.lower()]
            
        return JsonResponse({
            'success': True,
            'is_valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions if 'suggestions' in locals() else []
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_GET
def get_notifications_ajax(request):
    """Get user notifications via AJAX"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    try:
        # Get recent notifications (if notification model exists)
        notifications = []
        
        # For now, return empty list - can be expanded when notification system is implemented
        unread_count = 0
        
        return JsonResponse({
            'success': True,
            'notifications': notifications,
            'unread_count': unread_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_GET
def check_stock_ajax(request):
    """Check product stock availability via AJAX"""
    try:
        product_id = request.GET.get('product_id')
        quantity = int(request.GET.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # Check stock availability
        is_available = ProductService.check_availability(product, quantity)
        stock_level = product.stock_quantity
        
        # Determine stock status
        if stock_level == 0:
            stock_status = 'out_of_stock'
            stock_message = _('Out of stock')
        elif stock_level < 10:
            stock_status = 'low_stock'
            stock_message = f'{stock_level} left in stock'
        else:
            stock_status = 'in_stock'
            stock_message = _('In stock')
        
        return JsonResponse({
            'success': True,
            'is_available': is_available,
            'stock_level': stock_level,
            'stock_status': stock_status,
            'stock_message': stock_message,
            'max_quantity': min(stock_level, 10)  # Limit max quantity
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })