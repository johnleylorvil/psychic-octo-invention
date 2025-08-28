# marketplace/views/checkout.py
"""
E-commerce workflow views for Afèpanou marketplace
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.urls import reverse
from django.core.exceptions import ValidationError

from ..models import Cart, Order, Address, Transaction
from ..forms import ShippingAddressForm, PaymentMethodForm
from ..services import CartService, OrderService, PaymentService, EmailService


@login_required
def cart_view(request):
    """Shopping cart view with item management"""
    cart = CartService.get_or_create_cart(user=request.user)
    cart_summary = CartService.get_cart_summary(cart)
    
    context = {
        'cart': cart_summary['cart'],
        'items': cart_summary['items'],
        'totals': cart_summary['totals'],
        'issues': cart_summary['issues'],
        'title': _('Shopping Cart')
    }
    
    return render(request, 'pages/cart.html', context)


@login_required
def checkout_view(request):
    """Multi-step checkout process"""
    cart = CartService.get_or_create_cart(user=request.user)
    cart_summary = CartService.get_cart_summary(cart)
    
    # Check if cart is empty
    if cart_summary['item_count'] == 0:
        messages.error(request, _('Your cart is empty.'))
        return redirect('cart')
    
    # Validate cart items
    if not cart_summary['is_valid']:
        messages.error(request, _('Some items in your cart are no longer available.'))
        return redirect('cart')
    
    # Get or set checkout step
    step = request.session.get('checkout_step', 1)
    
    if request.method == 'POST':
        if step == 1:
            # Step 1: Shipping Address
            return handle_shipping_step(request, cart_summary)
        elif step == 2:
            # Step 2: Payment Method
            return handle_payment_step(request, cart_summary)
        elif step == 3:
            # Step 3: Order Confirmation
            return handle_confirmation_step(request, cart_summary)
    
    # Get forms for current step
    context = get_checkout_context(request, step, cart_summary)
    
    return render(request, 'pages/checkout.html', context)


def handle_shipping_step(request, cart_summary):
    """Handle shipping address step"""
    shipping_form = ShippingAddressForm(request.POST)
    
    if shipping_form.is_valid():
        # Save address to session
        request.session['shipping_address'] = shipping_form.cleaned_data
        request.session['checkout_step'] = 2
        return redirect('checkout')
    else:
        messages.error(request, _('Please correct the errors in the shipping address.'))
        context = get_checkout_context(request, 1, cart_summary)
        context['shipping_form'] = shipping_form
        return render(request, 'pages/checkout.html', context)


def handle_payment_step(request, cart_summary):
    """Handle payment method step"""
    payment_form = PaymentMethodForm(request.POST)
    
    if payment_form.is_valid():
        # Save payment method to session
        request.session['payment_method'] = payment_form.cleaned_data
        request.session['checkout_step'] = 3
        return redirect('checkout')
    else:
        messages.error(request, _('Please select a valid payment method.'))
        context = get_checkout_context(request, 2, cart_summary)
        context['payment_form'] = payment_form
        return render(request, 'pages/checkout.html', context)


def handle_confirmation_step(request, cart_summary):
    """Handle order confirmation and creation"""
    try:
        # Get data from session
        shipping_data = request.session.get('shipping_address')
        payment_data = request.session.get('payment_method')
        
        if not shipping_data or not payment_data:
            messages.error(request, _('Checkout session expired. Please start over.'))
            request.session['checkout_step'] = 1
            return redirect('checkout')
        
        # Create order
        order = OrderService.create_order_from_cart(
            cart=cart_summary['cart'],
            shipping_address=shipping_data,
            payment_method=payment_data['payment_method']
        )
        
        # Clear checkout session
        checkout_keys = ['checkout_step', 'shipping_address', 'payment_method']
        for key in checkout_keys:
            request.session.pop(key, None)
        
        # Send confirmation email
        EmailService.send_order_confirmation(order)
        
        # Redirect to order confirmation
        return redirect('order_confirmation', order_id=order.id)
        
    except ValidationError as e:
        messages.error(request, str(e))
        return redirect('cart')
    except Exception as e:
        messages.error(request, _('An error occurred while processing your order.'))
        return redirect('checkout')


def get_checkout_context(request, step, cart_summary):
    """Get context for checkout step"""
    context = {
        'step': step,
        'cart_summary': cart_summary,
        'title': _('Checkout')
    }
    
    if step == 1:
        # Shipping step
        user_addresses = Address.objects.get_user_addresses(request.user, 'shipping')
        context.update({
            'shipping_form': ShippingAddressForm(),
            'user_addresses': user_addresses
        })
    
    elif step == 2:
        # Payment step
        context.update({
            'payment_form': PaymentMethodForm(),
            'shipping_address': request.session.get('shipping_address')
        })
    
    elif step == 3:
        # Confirmation step
        context.update({
            'shipping_address': request.session.get('shipping_address'),
            'payment_method': request.session.get('payment_method')
        })
    
    return context


class OrderConfirmationView(LoginRequiredMixin, DetailView):
    """Order confirmation view"""
    model = Order
    template_name = 'pages/order_confirmation.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Order Confirmation')
        context['order_items'] = self.object.items.all()
        
        # Payment processing
        if self.object.payment_method == 'moncash' and self.object.payment_status == 'pending':
            # Create payment
            payment_result = PaymentService.create_payment(self.object)
            if payment_result['success']:
                context['payment_url'] = payment_result['payment_url']
            else:
                messages.error(self.request, _('Payment processing error. Please try again.'))
        
        return context


class OrderHistoryView(LoginRequiredMixin, ListView):
    """Order history view for user account"""
    template_name = 'account/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.for_user(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Order History')
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    """Order detail view with tracking information"""
    model = Order
    template_name = 'account/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Order #{self.object.order_number}"
        
        # Order summary
        order_summary = OrderService.get_order_summary(self.object)
        context.update(order_summary)
        
        # Transaction history
        context['transactions'] = PaymentService.get_transaction_history(self.object)
        
        return context


@login_required
def cancel_order(request, order_id):
    """Cancel order if possible"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        try:
            OrderService.cancel_order(order, reason=reason, user=request.user)
            messages.success(request, _('Order has been cancelled successfully.'))
        except ValidationError as e:
            messages.error(request, str(e))
    
    return redirect('order_detail', order_id=order.id)


@login_required
def reorder(request, order_id):
    """Re-add items from previous order to cart"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = CartService.get_or_create_cart(user=request.user)
    
    added_count = 0
    unavailable_items = []
    
    for order_item in order.items.all():
        product = order_item.product
        
        if product.is_active and CartService.check_availability(product, order_item.quantity):
            CartService.add_to_cart(cart, product, order_item.quantity)
            added_count += 1
        else:
            unavailable_items.append(product.name)
    
    if added_count > 0:
        messages.success(request, _('Added {} items from your previous order to cart.').format(added_count))
    
    if unavailable_items:
        messages.warning(
            request,
            _('Some items are no longer available: {}').format(', '.join(unavailable_items))
        )
    
    return redirect('cart')


@login_required
def wishlist_view(request):
    """User wishlist view"""
    try:
        wishlist = request.user.wishlist
        wishlist_items = wishlist.get_available_items()
    except:
        wishlist = None
        wishlist_items = []
    
    context = {
        'wishlist': wishlist,
        'wishlist_items': wishlist_items,
        'title': _('My Wishlist')
    }
    
    return render(request, 'account/wishlist.html', context)


def payment_success(request):
    """Payment success callback"""
    transaction_id = request.GET.get('transactionId')
    
    if transaction_id:
        # Verify payment
        result = PaymentService.verify_payment(transaction_id)
        
        if result['success'] and result['payment_status'] == 'successful':
            order = result['transaction'].order
            messages.success(request, _('Payment completed successfully!'))
            
            # Send payment confirmation
            EmailService.send_payment_confirmation(order, transaction_id)
            
            return redirect('order_detail', order_id=order.id)
        else:
            messages.error(request, _('Payment verification failed.'))
    else:
        messages.error(request, _('Invalid payment response.'))
    
    return redirect('order_history')


def payment_cancel(request):
    """Payment cancellation callback"""
    messages.warning(request, _('Payment was cancelled. You can try again later.'))
    return redirect('order_history')


@login_required
def address_book(request):
    """User address book management"""
    addresses = Address.objects.get_user_addresses(request.user)
    
    context = {
        'addresses': addresses,
        'title': _('Address Book')
    }
    
    return render(request, 'account/address_book.html', context)


@login_required
def add_address(request):
    """Add new address"""
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            
            messages.success(request, _('Address added successfully.'))
            return redirect('address_book')
    else:
        form = ShippingAddressForm()
    
    return render(request, 'account/add_address.html', {
        'form': form,
        'title': _('Add Address')
    })


@login_required
def edit_address(request, address_id):
    """Edit existing address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, _('Address updated successfully.'))
            return redirect('address_book')
    else:
        form = ShippingAddressForm(instance=address)
    
    return render(request, 'account/edit_address.html', {
        'form': form,
        'address': address,
        'title': _('Edit Address')
    })


@login_required
def delete_address(request, address_id):
    """Delete address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.deactivate()
        messages.success(request, _('Address deleted successfully.'))
    
    return redirect('address_book')