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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any about page specific context
        context['stats'] = {
            'total_products': Product.objects.available().count(),
            'total_sellers': Product.objects.available().values('seller').distinct().count(),
            'total_categories': Category.objects.active().count(),
        }
        return context