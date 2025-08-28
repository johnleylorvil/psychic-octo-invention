# marketplace/views/seller.py
"""
Seller management views for Afèpanou marketplace
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Avg
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from ..models import Product, Order, VendorProfile, Review, Category
from ..forms import ProductCreateForm, SellerApplicationForm
from ..services import ProductService, OrderService
from ..utils.decorators import seller_required


@method_decorator(seller_required, name='dispatch')
class SellerDashboardView(LoginRequiredMixin, DetailView):
    """Seller dashboard with analytics"""
    template_name = 'seller/dashboard.html'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get seller analytics
        analytics = ProductService.get_seller_analytics(user)
        context['analytics'] = analytics
        
        # Recent orders
        recent_orders = Order.objects.filter(
            items__product__seller=user
        ).distinct().order_by('-created_at')[:10]
        context['recent_orders'] = recent_orders
        
        # Low stock products
        low_stock_products = ProductService.get_low_stock_products(user)[:5]
        context['low_stock_products'] = low_stock_products
        
        # Recent reviews
        recent_reviews = Review.objects.filter(
            product__seller=user,
            is_approved=True
        ).order_by('-created_at')[:5]
        context['recent_reviews'] = recent_reviews
        
        # Monthly sales data for chart
        monthly_sales = OrderService.get_sales_analytics(
            seller=user,
            date_from=(timezone.now() - timedelta(days=30)).date()
        )
        context['monthly_sales'] = monthly_sales
        
        context['title'] = _('Seller Dashboard')
        
        return context


@method_decorator(seller_required, name='dispatch')
class SellerProductListView(LoginRequiredMixin, ListView):
    """Seller product inventory management"""
    template_name = 'seller/products.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Product.objects.filter(seller=self.request.user).order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        elif status == 'low_stock':
            queryset = queryset.filter(
                stock_quantity__lte=models.F('min_stock_alert'),
                is_digital=False
            )
        elif status == 'out_of_stock':
            queryset = queryset.filter(stock_quantity=0, is_digital=False)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(sku__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('My Products')
        
        # Product statistics
        all_products = Product.objects.filter(seller=self.request.user)
        context['product_stats'] = {
            'total': all_products.count(),
            'active': all_products.filter(is_active=True).count(),
            'inactive': all_products.filter(is_active=False).count(),
            'low_stock': all_products.filter(
                stock_quantity__lte=models.F('min_stock_alert'),
                is_digital=False
            ).count(),
            'out_of_stock': all_products.filter(stock_quantity=0, is_digital=False).count(),
        }
        
        context['current_status'] = self.request.GET.get('status', 'all')
        context['search_query'] = self.request.GET.get('search', '')
        
        return context


@method_decorator(seller_required, name='dispatch')
class SellerProductCreateView(LoginRequiredMixin, CreateView):
    """Create new product"""
    model = Product
    form_class = ProductCreateForm
    template_name = 'seller/product_create.html'
    
    def form_valid(self, form):
        product = form.save(commit=False)
        product.seller = self.request.user
        product.save()
        
        messages.success(self.request, _('Product created successfully!'))
        return redirect('seller_product_detail', product_id=product.id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Add New Product')
        return context


@method_decorator(seller_required, name='dispatch')
class SellerProductUpdateView(LoginRequiredMixin, UpdateView):
    """Edit existing product"""
    model = Product
    form_class = ProductCreateForm
    template_name = 'seller/product_edit.html'
    pk_url_kwarg = 'product_id'
    
    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Product updated successfully!'))
        return redirect('seller_product_detail', product_id=self.object.id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Edit Product')
        return context


@method_decorator(seller_required, name='dispatch')
class SellerProductDetailView(LoginRequiredMixin, DetailView):
    """Seller product detail view"""
    model = Product
    template_name = 'seller/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'product_id'
    
    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Product: {self.object.name}"
        
        # Product analytics
        product = self.object
        context['product_analytics'] = {
            'views': product.view_count,
            'purchases': product.purchase_count,
            'conversion_rate': product.conversion_rate,
            'reviews_count': product.reviews.approved().count(),
            'average_rating': product.average_rating,
        }
        
        # Recent orders for this product
        recent_orders = Order.objects.filter(
            items__product=product
        ).distinct().order_by('-created_at')[:10]
        context['recent_orders'] = recent_orders
        
        return context


@method_decorator(seller_required, name='dispatch')
class SellerOrderListView(LoginRequiredMixin, ListView):
    """Seller order management"""
    template_name = 'seller/orders.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Order.objects.filter(
            items__product__seller=self.request.user
        ).distinct().order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Orders')
        
        # Order statistics
        all_orders = Order.objects.filter(items__product__seller=self.request.user).distinct()
        context['order_stats'] = {
            'total': all_orders.count(),
            'pending': all_orders.filter(status='pending').count(),
            'processing': all_orders.filter(status='processing').count(),
            'shipped': all_orders.filter(status='shipped').count(),
            'delivered': all_orders.filter(status='delivered').count(),
        }
        
        context['current_status'] = self.request.GET.get('status', 'all')
        
        return context


@login_required
@seller_required
def seller_order_detail(request, order_id):
    """Seller order detail view"""
    order = get_object_or_404(
        Order.objects.filter(items__product__seller=request.user).distinct(),
        id=order_id
    )
    
    # Get only items from this seller
    seller_items = order.items.filter(product__seller=request.user)
    
    context = {
        'order': order,
        'seller_items': seller_items,
        'title': f"Order #{order.order_number}"
    }
    
    return render(request, 'seller/order_detail.html', context)


@login_required
@seller_required
def update_order_status(request, order_id):
    """Update order status"""
    order = get_object_or_404(
        Order.objects.filter(items__product__seller=request.user).distinct(),
        id=order_id
    )
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        try:
            OrderService.update_order_status(order, new_status, notes, request.user)
            messages.success(request, _('Order status updated successfully.'))
        except ValidationError as e:
            messages.error(request, str(e))
    
    return redirect('seller_order_detail', order_id=order.id)


@method_decorator(seller_required, name='dispatch')
class SellerAnalyticsView(LoginRequiredMixin, DetailView):
    """Seller analytics and performance metrics"""
    template_name = 'seller/analytics.html'
    
    def get_object(self):
        return self.request.user
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Comprehensive analytics
        context['analytics'] = {
            'products': ProductService.get_seller_analytics(user),
            'orders': OrderService.get_sales_analytics(seller=user),
            'revenue': self._get_revenue_analytics(user),
            'performance': self._get_performance_metrics(user),
        }
        
        # Chart data
        context['chart_data'] = {
            'monthly_sales': self._get_monthly_sales_data(user),
            'category_breakdown': self._get_category_breakdown(user),
            'top_products': self._get_top_products(user),
        }
        
        context['title'] = _('Analytics Dashboard')
        
        return context
    
    def _get_revenue_analytics(self, user):
        """Get revenue analytics"""
        orders = Order.objects.filter(
            items__product__seller=user,
            status='delivered',
            payment_status='paid'
        ).distinct()
        
        total_revenue = sum(
            item.total_price for order in orders 
            for item in order.items.filter(product__seller=user)
        )
        
        return {
            'total_revenue': total_revenue,
            'average_order_value': total_revenue / orders.count() if orders.count() > 0 else 0,
            'monthly_revenue': total_revenue,  # Simplified
        }
    
    def _get_performance_metrics(self, user):
        """Get performance metrics"""
        products = Product.objects.filter(seller=user)
        reviews = Review.objects.filter(product__seller=user, is_approved=True)
        
        return {
            'average_rating': reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
            'total_reviews': reviews.count(),
            'response_time': 24,  # Hours - placeholder
            'customer_satisfaction': 4.5,  # Placeholder
        }
    
    def _get_monthly_sales_data(self, user):
        """Get monthly sales data for charts"""
        from datetime import datetime, timedelta
        import calendar
        
        # Get last 12 months of data
        monthly_data = []
        for i in range(12):
            month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
            month_orders = Order.objects.filter(
                items__product__seller=user,
                created_at__year=month_start.year,
                created_at__month=month_start.month,
                status='delivered'
            ).distinct()
            
            monthly_revenue = sum(
                item.total_price for order in month_orders 
                for item in order.items.filter(product__seller=user)
            )
            
            monthly_data.append({
                'month': calendar.month_name[month_start.month],
                'revenue': float(monthly_revenue),
                'orders': month_orders.count()
            })
        
        return monthly_data[::-1]  # Reverse to chronological order
    
    def _get_category_breakdown(self, user):
        """Get sales breakdown by category"""
        categories = Category.objects.filter(
            products__seller=user
        ).annotate(
            total_sales=Count('products__orderitem')
        ).order_by('-total_sales')[:10]
        
        return [
            {
                'name': cat.name,
                'sales': cat.total_sales
            }
            for cat in categories
        ]
    
    def _get_top_products(self, user):
        """Get top performing products"""
        products = Product.objects.filter(seller=user).annotate(
            total_sold=Count('orderitem')
        ).order_by('-total_sold')[:10]
        
        return [
            {
                'name': product.name,
                'sold': product.total_sold,
                'revenue': product.total_sold * float(product.current_price)
            }
            for product in products
        ]


@login_required
@seller_required
def bulk_product_actions(request):
    """Handle bulk actions on products"""
    if request.method == 'POST':
        action = request.POST.get('action')
        product_ids = request.POST.getlist('product_ids')
        
        if not product_ids:
            messages.error(request, _('No products selected.'))
            return redirect('seller_products')
        
        # Ensure products belong to the seller
        products = Product.objects.filter(
            id__in=product_ids,
            seller=request.user
        )
        
        if action == 'activate':
            count = ProductService.bulk_update_status(product_ids, True)
            messages.success(request, _('Activated {} products.').format(count))
        
        elif action == 'deactivate':
            count = ProductService.bulk_update_status(product_ids, False)
            messages.success(request, _('Deactivated {} products.').format(count))
        
        elif action == 'delete':
            count = products.count()
            products.update(is_active=False)  # Soft delete
            messages.success(request, _('Deleted {} products.').format(count))
        
        else:
            messages.error(request, _('Invalid action.'))
    
    return redirect('seller_products')


@login_required
@seller_required
def seller_profile_settings(request):
    """Seller profile and business settings"""
    try:
        vendor_profile = VendorProfile.objects.get(user=request.user)
    except VendorProfile.DoesNotExist:
        messages.error(request, _('Vendor profile not found.'))
        return redirect('seller_dashboard')
    
    if request.method == 'POST':
        form = SellerApplicationForm(request.POST, instance=vendor_profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Business profile updated successfully.'))
            return redirect('seller_profile_settings')
    else:
        form = SellerApplicationForm(instance=vendor_profile)
    
    context = {
        'form': form,
        'vendor_profile': vendor_profile,
        'title': _('Business Settings')
    }
    
    return render(request, 'seller/profile_settings.html', context)