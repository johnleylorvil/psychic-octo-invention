"""
URL utilities for Afèpanou marketplace
Helpers for URL generation, redirects, and SEO optimization
"""
from django.urls import reverse
from django.http import HttpResponsePermanentRedirect
from django.conf import settings
from urllib.parse import urlencode

def build_absolute_uri(relative_url, request=None):
    """Build absolute URI from relative URL"""
    if request:
        return request.build_absolute_uri(relative_url)
    
    # Fallback to settings
    domain = getattr(settings, 'SITE_DOMAIN', 'afepanou.com')
    protocol = 'https' if getattr(settings, 'SECURE_SSL_REDIRECT', False) else 'http'
    return f"{protocol}://{domain}{relative_url}"

def create_product_url(product):
    """Generate SEO-friendly product URL"""
    return reverse('marketplace:product_detail', kwargs={'slug': product.slug})

def create_category_url(category):
    """Generate SEO-friendly category URL"""
    return reverse('marketplace:category_list', kwargs={'slug': category.slug})

def create_vendor_url(vendor):
    """Generate SEO-friendly vendor profile URL"""
    return reverse('marketplace:vendor_profile', kwargs={'vendor_slug': vendor.slug})

def create_search_url(query=None, category=None, filters=None):
    """Generate search URL with parameters"""
    params = {}
    if query:
        params['q'] = query
    if category:
        params['category'] = category
    if filters:
        params.update(filters)
    
    url = reverse('marketplace:product_search')
    if params:
        url += '?' + urlencode(params)
    return url

def create_city_url(city_slug):
    """Generate location-specific URL for cities"""
    city_urls = {
        'port-au-prince': 'marketplace:products_port_au_prince',
        'cap-haitien': 'marketplace:products_cap_haitien',
        'gonaives': 'marketplace:products_gonaives',
        'les-cayes': 'marketplace:products_les_cayes',
    }
    
    if city_slug in city_urls:
        return reverse(city_urls[city_slug])
    return reverse('marketplace:home')

def create_breadcrumb_data(current_page, context=None):
    """Generate breadcrumb navigation data"""
    breadcrumbs = [
        {'title': 'Accueil', 'url': reverse('marketplace:home')}
    ]
    
    if current_page == 'category' and context:
        category = context.get('category')
        if category:
            # Add parent categories if hierarchical
            if category.parent:
                breadcrumbs.append({
                    'title': category.parent.name,
                    'url': create_category_url(category.parent)
                })
            breadcrumbs.append({
                'title': category.name,
                'url': create_category_url(category)
            })
    
    elif current_page == 'product' and context:
        product = context.get('product')
        if product and product.category:
            breadcrumbs.append({
                'title': product.category.name,
                'url': create_category_url(product.category)
            })
            breadcrumbs.append({
                'title': product.name,
                'url': create_product_url(product)
            })
    
    elif current_page == 'search':
        breadcrumbs.append({
            'title': 'Recherche',
            'url': reverse('marketplace:product_search')
        })
    
    return breadcrumbs

class LegacyURLRedirectMiddleware:
    """Middleware to handle legacy URL redirects"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define legacy URL mappings
        self.redirects = {
            '/products/': '/produits/',
            '/category/': '/categorie/',
            '/cart/': '/panier/',
            '/checkout/': '/commande/',
            '/account/': '/compte/',
            '/seller/': '/vendeur/',
        }
    
    def __call__(self, request):
        # Check for legacy URLs and redirect
        path = request.path
        for old_path, new_path in self.redirects.items():
            if path.startswith(old_path):
                new_url = path.replace(old_path, new_path, 1)
                return HttpResponsePermanentRedirect(new_url)
        
        response = self.get_response(request)
        return response

def get_canonical_url(request, obj=None):
    """Generate canonical URL for SEO"""
    if obj:
        # For model objects with get_absolute_url
        if hasattr(obj, 'get_absolute_url'):
            relative_url = obj.get_absolute_url()
        else:
            relative_url = request.path
    else:
        relative_url = request.path
    
    return build_absolute_uri(relative_url, request)

def create_share_urls(product):
    """Generate social media sharing URLs"""
    product_url = build_absolute_uri(create_product_url(product))
    
    share_data = {
        'url': product_url,
        'title': product.name,
        'description': product.description[:160] if product.description else '',
        'image': product.get_main_image_url() if hasattr(product, 'get_main_image_url') else None,
    }
    
    # Create sharing URLs for different platforms
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={share_data['url']}"
    twitter_url = f"https://twitter.com/intent/tweet?url={share_data['url']}&text={share_data['title']}"
    whatsapp_url = f"https://wa.me/?text={share_data['title']} {share_data['url']}"
    
    return {
        'facebook': facebook_url,
        'twitter': twitter_url,
        'whatsapp': whatsapp_url,
        'data': share_data,
    }

def create_pagination_urls(request, page_obj):
    """Generate pagination URLs preserving query parameters"""
    base_url = request.path
    params = request.GET.copy()
    
    urls = {
        'first': None,
        'previous': None,
        'next': None,
        'last': None,
    }
    
    if page_obj.has_previous():
        params['page'] = 1
        urls['first'] = f"{base_url}?{params.urlencode()}"
        
        params['page'] = page_obj.previous_page_number()
        urls['previous'] = f"{base_url}?{params.urlencode()}"
    
    if page_obj.has_next():
        params['page'] = page_obj.next_page_number()
        urls['next'] = f"{base_url}?{params.urlencode()}"
        
        params['page'] = page_obj.paginator.num_pages
        urls['last'] = f"{base_url}?{params.urlencode()}"
    
    return urls