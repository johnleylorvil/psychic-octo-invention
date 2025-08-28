# marketplace/views/pages.py
"""
Core template views for Afèpanou marketplace
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Avg
from django.http import Http404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from ..models import (
    Product, Category, Review, Banner, Order, 
    Cart, Wishlist, NewsletterSubscriber
)
from ..forms import (
    ProductSearchForm, ProductReviewForm, 
    NewsletterSubscriptionForm, ContactForm
)
from ..services import ProductService, CartService


class HomePageView(TemplateView):
    """Homepage view with featured products and categories"""
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured products
        context['featured_products'] = Product.objects.featured()[:8]
        
        # Get popular categories
        context['featured_categories'] = Category.objects.featured()[:6]
        
        # Get active banners
        context['banners'] = Banner.objects.filter(is_active=True).order_by('display_order')[:5]
        
        # Get latest products
        context['latest_products'] = Product.objects.available().order_by('-created_at')[:8]
        
        # Newsletter subscription form
        context['newsletter_form'] = NewsletterSubscriptionForm()
        
        # Statistics
        context['stats'] = {
            'total_products': Product.objects.available().count(),
            'total_categories': Category.objects.active().count(),
            'total_sellers': Product.objects.available().values('seller').distinct().count(),
        }
        
        return context


class ProductDetailView(DetailView):
    """Product detail view with reviews and related products"""
    model = Product
    template_name = 'pages/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_active:
            raise Http404(_("Product not found"))
        
        # Increment view count
        obj.increment_view_count()
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Get approved reviews
        reviews = Review.objects.approved().filter(product=product).select_related('user')
        context['reviews'] = reviews
        context['reviews_count'] = reviews.count()
        
        # Review statistics
        if reviews.exists():
            context['average_rating'] = reviews.aggregate(Avg('rating'))['rating__avg']
            context['rating_breakdown'] = {
                i: reviews.filter(rating=i).count() 
                for i in range(1, 6)
            }
        
        # Check if user can review
        if self.request.user.is_authenticated:
            context['can_review'] = not reviews.filter(user=self.request.user).exists()
            context['review_form'] = ProductReviewForm()
            
            # Check if in wishlist
            try:
                wishlist = Wishlist.objects.get(user=self.request.user)
                context['in_wishlist'] = wishlist.has_product(product)
            except Wishlist.DoesNotExist:
                context['in_wishlist'] = False
        
        # Related products
        context['related_products'] = ProductService.get_related_products(product, limit=4)
        
        # Product images
        context['product_images'] = product.images.all().order_by('sort_order')
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle review submission"""
        if not request.user.is_authenticated:
            messages.error(request, _('You must be logged in to submit a review.'))
            return redirect('login')
        
        product = self.get_object()
        
        # Check if user already reviewed
        if Review.objects.filter(user=request.user, product=product).exists():
            messages.error(request, _('You have already reviewed this product.'))
            return redirect('product_detail', slug=product.slug)
        
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            
            # Check if user has purchased this product
            has_purchased = Order.objects.filter(
                user=request.user,
                items__product=product,
                status='delivered'
            ).exists()
            review.is_verified_purchase = has_purchased
            
            review.save()
            messages.success(request, _('Your review has been submitted and will be published after moderation.'))
        else:
            messages.error(request, _('Please correct the errors in your review.'))
        
        return redirect('product_detail', slug=product.slug)


class CategoryListView(ListView):
    """Category listing with products"""
    template_name = 'pages/category_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        if not self.category.is_active:
            raise Http404(_("Category not found"))
        
        queryset = Product.objects.by_category(self.category)
        
        # Apply filters from search form
        form = ProductSearchForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data['query']:
                queryset = queryset.filter(
                    Q(name__icontains=form.cleaned_data['query']) |
                    Q(description__icontains=form.cleaned_data['query']) |
                    Q(tags__icontains=form.cleaned_data['query'])
                )
            
            if form.cleaned_data['min_price']:
                queryset = queryset.filter(price__gte=form.cleaned_data['min_price'])
            
            if form.cleaned_data['max_price']:
                queryset = queryset.filter(price__lte=form.cleaned_data['max_price'])
            
            if form.cleaned_data['brand']:
                queryset = queryset.filter(brand__icontains=form.cleaned_data['brand'])
            
            if form.cleaned_data['in_stock']:
                queryset = queryset.filter(stock_quantity__gt=0)
            
            if form.cleaned_data['on_sale']:
                queryset = queryset.filter(promotional_price__isnull=False)
            
            # Apply sorting
            sort_by = form.cleaned_data.get('sort_by', 'relevance')
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
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['search_form'] = ProductSearchForm(self.request.GET)
        
        # Subcategories
        context['subcategories'] = self.category.children.active()
        
        # Category breadcrumb
        breadcrumbs = []
        current = self.category
        while current:
            breadcrumbs.insert(0, current)
            current = current.parent
        context['breadcrumbs'] = breadcrumbs
        
        return context


class ProductSearchView(ListView):
    """Product search view with advanced filtering"""
    template_name = 'pages/search_results.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        form = ProductSearchForm(self.request.GET)
        queryset = Product.objects.available()
        
        if form.is_valid():
            # Search filters
            if form.cleaned_data['query']:
                filters = ProductService.search_products(
                    form.cleaned_data['query'],
                    {
                        'category': form.cleaned_data.get('category'),
                        'min_price': form.cleaned_data.get('min_price'),
                        'max_price': form.cleaned_data.get('max_price'),
                        'brand': form.cleaned_data.get('brand')
                    }
                )
                queryset = filters
            
            # Additional filters
            if form.cleaned_data['in_stock']:
                queryset = queryset.filter(stock_quantity__gt=0)
            
            if form.cleaned_data['on_sale']:
                queryset = queryset.filter(promotional_price__isnull=False)
            
            # Sorting
            sort_by = form.cleaned_data.get('sort_by', 'relevance')
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
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ProductSearchForm(self.request.GET)
        context['query'] = self.request.GET.get('query', '')
        
        return context


class UserProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'account/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Recent orders
        context['recent_orders'] = Order.objects.filter(user=user).order_by('-created_at')[:5]
        
        # User statistics
        context['user_stats'] = {
            'total_orders': Order.objects.filter(user=user).count(),
            'completed_orders': Order.objects.filter(user=user, status='delivered').count(),
            'total_spent': sum(
                order.total_amount 
                for order in Order.objects.filter(user=user, status='delivered')
            ),
            'wishlist_items': 0
        }
        
        # Wishlist count
        try:
            wishlist = Wishlist.objects.get(user=user)
            context['user_stats']['wishlist_items'] = wishlist.item_count
        except Wishlist.DoesNotExist:
            pass
        
        # User addresses
        context['addresses'] = user.addresses.filter(is_active=True)
        
        return context


@login_required
def toggle_wishlist(request, product_slug):
    """Toggle product in user's wishlist"""
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if wishlist.has_product(product):
        wishlist.remove_product(product)
        messages.success(request, _('Product removed from your wishlist.'))
        action = 'removed'
    else:
        wishlist.add_product(product)
        messages.success(request, _('Product added to your wishlist.'))
        action = 'added'
    
    # Return to previous page or product detail
    next_url = request.GET.get('next') or product.get_absolute_url()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'action': action,
            'message': str(messages.get_messages(request)[-1])
        })
    
    return redirect(next_url)


def newsletter_signup(request):
    """Newsletter signup view"""
    if request.method == 'POST':
        form = NewsletterSubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save()
            messages.success(request, _('Thank you for subscribing to our newsletter!'))
        else:
            messages.error(request, _('Please enter a valid email address.'))
    
    return redirect('home')


def contact_view(request):
    """Contact form view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process contact form (send email, save to database, etc.)
            # Implementation depends on requirements
            messages.success(request, _('Your message has been sent. We will get back to you soon!'))
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'pages/contact.html', {'form': form})


class AboutView(TemplateView):
    """About page view"""
    template_name = 'pages/about.html'


@login_required
def cart_view(request):
    """Shopping cart view"""
    from ..models import Cart
    
    cart, created = Cart.objects.get_or_create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key if not request.user.is_authenticated else None
    )
    
    cart_items = cart.items.select_related('product').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'title': _('Shopping Cart')
    }
    
    return render(request, 'pages/cart.html', context)


def add_to_cart(request):
    """Add product to cart"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id)
            cart_service = CartService(request)
            cart_service.add_to_cart(product, quantity)
            
            messages.success(request, _('Product added to cart successfully!'))
        except Product.DoesNotExist:
            messages.error(request, _('Product not found.'))
        except Exception as e:
            messages.error(request, _('Error adding product to cart.'))
    
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:home'))


@login_required
def update_cart_item(request):
    """Update cart item quantity"""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            from ..models import CartItem
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, _('Cart updated successfully!'))
            else:
                cart_item.delete()
                messages.success(request, _('Item removed from cart!'))
                
        except CartItem.DoesNotExist:
            messages.error(request, _('Cart item not found.'))
    
    return redirect('marketplace:cart')


@login_required
def remove_from_cart(request):
    """Remove item from cart"""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        
        try:
            from ..models import CartItem
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
            messages.success(request, _('Item removed from cart!'))
        except CartItem.DoesNotExist:
            messages.error(request, _('Cart item not found.'))
    
    return redirect('marketplace:cart')


@login_required
def clear_cart(request):
    """Clear all items from cart"""
    if request.method == 'POST':
        from ..models import Cart
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            messages.success(request, _('Cart cleared successfully!'))
        except Cart.DoesNotExist:
            pass
    
    return redirect('marketplace:cart')


@login_required
def wishlist_view(request):
    """User wishlist view"""
    from ..models.wishlist import Wishlist
    
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    return render(request, 'pages/wishlist.html', {
        'wishlist_items': wishlist_items,
        'title': _('My Wishlist')
    })


def order_invoice(request, order_id):
    """Generate order invoice"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user owns this order or is a seller
    if not (order.user == request.user or 
            (request.user.is_authenticated and request.user.is_seller and 
             order.items.filter(product__seller=request.user.vendorprofile).exists())):
        messages.error(request, _('Access denied.'))
        return redirect('marketplace:home')
    
    return render(request, 'pages/order_invoice.html', {
        'order': order,
        'title': f'Invoice #{order.order_number}'
    })


def order_tracking(request, order_id):
    """Order tracking view"""
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user owns this order
    if order.user != request.user:
        messages.error(request, _('Access denied.'))
        return redirect('marketplace:home')
    
    return render(request, 'pages/order_tracking.html', {
        'order': order,
        'title': f'Track Order #{order.order_number}'
    })


@login_required
def cancel_order(request, order_id):
    """Cancel order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.can_be_cancelled():
        if request.method == 'POST':
            order.status = 'cancelled'
            order.save()
            messages.success(request, _('Order cancelled successfully.'))
            return redirect('marketplace:order_detail', order_id=order.id)
    else:
        messages.error(request, _('This order cannot be cancelled.'))
    
    return render(request, 'pages/cancel_order.html', {
        'order': order,
        'title': f'Cancel Order #{order.order_number}'
    })


def edit_review(request, review_id):
    """Edit product review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ProductReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, _('Review updated successfully!'))
            return redirect('marketplace:product_detail', slug=review.product.slug)
    else:
        form = ProductReviewForm(instance=review)
    
    return render(request, 'pages/edit_review.html', {
        'form': form,
        'review': review,
        'title': f'Edit Review for {review.product.name}'
    })


@login_required
def delete_review(request, review_id):
    """Delete product review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        product_slug = review.product.slug
        review.delete()
        messages.success(request, _('Review deleted successfully!'))
        return redirect('marketplace:product_detail', slug=product_slug)
    
    return render(request, 'pages/delete_review.html', {
        'review': review,
        'title': 'Delete Review'
    })


def product_reviews(request, product_id):
    """Product reviews page"""
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).select_related('user').order_by('-created_at')
    
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pages/product_reviews.html', {
        'product': product,
        'reviews': page_obj,
        'title': f'Reviews for {product.name}'
    })


def vendor_profile(request, vendor_slug):
    """Public vendor profile view"""
    from ..models.vendor import VendorProfile
    
    vendor = get_object_or_404(VendorProfile, slug=vendor_slug, is_active=True)
    featured_products = Product.objects.filter(seller=vendor).available()[:6]
    
    return render(request, 'pages/vendor_profile.html', {
        'vendor': vendor,
        'featured_products': featured_products,
        'title': vendor.business_name
    })


def vendor_products(request, vendor_slug):
    """Vendor products listing"""
    from ..models.vendor import VendorProfile
    
    vendor = get_object_or_404(VendorProfile, slug=vendor_slug, is_active=True)
    products = Product.objects.filter(seller=vendor).available()
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pages/vendor_products.html', {
        'vendor': vendor,
        'products': page_obj,
        'title': f'Products by {vendor.business_name}'
    })


def city_products(request, city):
    """Location-specific products"""
    city_names = {
        'port-au-prince': 'Port-au-Prince',
        'cap-haitien': 'Cap-Haïtien',
        'gonaives': 'Gonaïves',
        'les-cayes': 'Les Cayes'
    }
    
    city_name = city_names.get(city, city.title())
    products = Product.objects.available().filter(seller__city__icontains=city_name)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pages/city_products.html', {
        'products': page_obj,
        'city': city_name,
        'title': f'Products in {city_name}'
    })


def new_products(request):
    """New products listing"""
    products = Product.objects.available().order_by('-created_at')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pages/new_products.html', {
        'products': page_obj,
        'title': _('New Products')
    })


def featured_promotions(request):
    """Featured promotions listing"""
    from ..models.promotion import Promotion
    
    promotions = Promotion.objects.filter(is_active=True).order_by('-created_at')
    
    return render(request, 'pages/promotions.html', {
        'promotions': promotions,
        'title': _('Current Promotions')
    })


def brand_products(request, brand_slug):
    """Brand products listing"""
    products = Product.objects.available().filter(brand__slug=brand_slug)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pages/brand_products.html', {
        'products': page_obj,
        'brand_slug': brand_slug,
        'title': f'Products by {brand_slug.replace("-", " ").title()}'
    })
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any about page specific context
        context['stats'] = {
            'total_products': Product.objects.available().count(),
            'total_sellers': Product.objects.available().values('seller').distinct().count(),
            'total_categories': Category.objects.active().count(),
        }
        return context