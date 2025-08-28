# marketplace/views/auth.py
"""
User authentication system views for Afèpanou marketplace
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect
from django.conf import settings

from ..forms import (
    UserRegistrationForm, CustomLoginForm, UserProfileForm,
    SellerApplicationForm
)
from ..models import User, VendorProfile
from ..services import EmailService


class UserRegistrationView(CreateView):
    """User registration view with email verification"""
    form_class = UserRegistrationForm
    template_name = 'account/register.html'
    success_url = reverse_lazy('registration_complete')
    
    def form_valid(self, form):
        user = form.save()
        
        # Send welcome email
        EmailService.send_welcome_email(user)
        
        messages.success(
            self.request,
            _('Registration successful! Please check your email to verify your account.')
        )
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Create Account')
        return context


def user_login_view(request):
    """Custom login view with redirect handling"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Set session expiry based on remember me
                if not remember_me:
                    request.session.set_expiry(0)  # Browser session
                else:
                    request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
                
                # Update last login IP
                user.last_login_ip = get_client_ip(request)
                user.save(update_fields=['last_login_ip'])
                
                messages.success(request, _('Welcome back, {}!').format(user.get_display_name()))
                
                # Redirect to next or home
                next_url = request.GET.get('next') or 'home'
                return redirect(next_url)
            else:
                messages.error(request, _('Invalid username or password.'))
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = CustomLoginForm()
    
    return render(request, 'account/login.html', {
        'form': form,
        'title': _('Sign In')
    })


@login_required
def user_logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, _('You have been successfully logged out.'))
    return redirect('home')


@login_required
def profile_view(request):
    """User profile management view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been updated successfully.'))
            return redirect('profile')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'account/profile.html', {
        'form': form,
        'title': _('My Profile')
    })


def password_reset_request(request):
    """Password reset request view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Send reset email
            current_site = get_current_site(request)
            mail_subject = _('Reset your Afèpanou password')
            
            message = render_to_string('emails/password_reset.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
                'protocol': 'https' if request.is_secure() else 'http',
            })
            
            send_mail(
                mail_subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=message
            )
            
            messages.success(
                request,
                _('Password reset instructions have been sent to your email.')
            )
            return redirect('password_reset_done')
            
        except User.DoesNotExist:
            messages.error(request, _('No account found with this email address.'))
    
    return render(request, 'account/password_reset_request.html', {
        'title': _('Reset Password')
    })


def password_reset_confirm(request, uidb64, token):
    """Password reset confirmation view"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 and password1 == password2:
                user.set_password(password1)
                user.save()
                
                messages.success(
                    request,
                    _('Your password has been reset successfully. You can now log in with your new password.')
                )
                return redirect('login')
            else:
                messages.error(request, _('Passwords do not match.'))
        
        return render(request, 'account/password_reset_confirm.html', {
            'validlink': True,
            'title': _('Set New Password')
        })
    else:
        return render(request, 'account/password_reset_confirm.html', {
            'validlink': False,
            'title': _('Invalid Reset Link')
        })


class SellerApplicationView(LoginRequiredMixin, CreateView):
    """Seller application view"""
    form_class = SellerApplicationForm
    template_name = 'account/become_seller.html'
    success_url = reverse_lazy('seller_application_complete')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user is already a seller
        if request.user.is_seller:
            messages.info(request, _('You are already a registered seller.'))
            return redirect('seller_dashboard')
        
        # Check if user already has pending application
        if hasattr(request.user, 'vendor_profile'):
            messages.info(request, _('Your seller application is under review.'))
            return redirect('seller_application_status')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        vendor_profile = form.save(commit=False)
        vendor_profile.user = self.request.user
        vendor_profile.verification_status = 'pending'
        vendor_profile.save()
        
        # Send application confirmation email
        EmailService.send_new_seller_welcome(self.request.user)
        
        messages.success(
            self.request,
            _('Your seller application has been submitted. We will review it within 2-3 business days.')
        )
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Become a Seller')
        return context


@login_required
def seller_application_status(request):
    """View seller application status"""
    try:
        vendor_profile = VendorProfile.objects.get(user=request.user)
    except VendorProfile.DoesNotExist:
        messages.error(request, _('No seller application found.'))
        return redirect('become_seller')
    
    return render(request, 'account/seller_application_status.html', {
        'vendor_profile': vendor_profile,
        'title': _('Seller Application Status')
    })


def email_verification(request, uidb64, token):
    """Email verification view"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.email_verified = True
        user.save()
        
        # Log the user in
        login(request, user)
        
        messages.success(
            request,
            _('Your email has been verified successfully! Welcome to Afèpanou.')
        )
        return redirect('home')
    else:
        messages.error(
            request,
            _('Email verification link is invalid or has expired.')
        )
        return redirect('login')


def resend_verification_email(request):
    """Resend email verification"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, email_verified=False)
            
            # Generate verification token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Send verification email
            current_site = get_current_site(request)
            mail_subject = _('Verify your Afèpanou account')
            
            message = render_to_string('emails/email_verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
                'protocol': 'https' if request.is_secure() else 'http',
            })
            
            send_mail(
                mail_subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=message
            )
            
            messages.success(
                request,
                _('Verification email has been resent to your email address.')
            )
            
        except User.DoesNotExist:
            messages.error(
                request,
                _('No unverified account found with this email address.')
            )
    
    return render(request, 'account/resend_verification.html', {
        'title': _('Resend Verification Email')
    })


class RegistrationCompleteView(TemplateView):
    """Registration complete view"""
    template_name = 'account/registration_complete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Registration Complete')
        return context


class SellerApplicationCompleteView(TemplateView):
    """Seller application complete view"""
    template_name = 'account/seller_application_complete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Application Submitted')
        return context


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def delete_account(request):
    """Account deletion view"""
    if request.method == 'POST':
        password = request.POST.get('password')
        
        if request.user.check_password(password):
            # Soft delete - deactivate account instead of hard delete
            request.user.is_active = False
            request.user.save()
            
            logout(request)
            
            messages.success(
                request,
                _('Your account has been deactivated. Contact support if you want to reactivate it.')
            )
            return redirect('home')
        else:
            messages.error(request, _('Incorrect password.'))
    
    return render(request, 'account/delete_account.html', {
        'title': _('Delete Account')
    })


def email_confirmation(request, token):
    """Email confirmation view with token"""
    try:
        # Decode the token to get user ID
        uid = urlsafe_base64_decode(token).decode()
        user = get_object_or_404(User, pk=uid)
        
        if not user.email_verified:
            user.email_verified = True
            user.save()
            
            messages.success(
                request,
                _('Email verified successfully! You can now use all features.')
            )
        else:
            messages.info(request, _('Email is already verified.'))
        
        return redirect('marketplace:login')
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, _('Invalid verification link.'))
        return redirect('marketplace:home')


@login_required
def address_book(request):
    """User address book management"""
    from ..models.address import Address
    
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    
    return render(request, 'account/address_book.html', {
        'addresses': addresses,
        'title': _('My Addresses')
    })


@login_required
def add_address(request):
    """Add new address"""
    from ..forms import AddressForm
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If this is the first address, make it default
            if not Address.objects.filter(user=request.user).exists():
                address.is_default = True
            
            address.save()
            
            messages.success(request, _('Address added successfully.'))
            return redirect('marketplace:address_book')
    else:
        form = AddressForm()
    
    return render(request, 'account/add_address.html', {
        'form': form,
        'title': _('Add Address')
    })


@login_required
def edit_address(request, address_id):
    """Edit existing address"""
    from ..models.address import Address
    from ..forms import AddressForm
    
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, _('Address updated successfully.'))
            return redirect('marketplace:address_book')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'account/edit_address.html', {
        'form': form,
        'address': address,
        'title': _('Edit Address')
    })


class UserLogoutView(TemplateView):
    """User logout view"""
    template_name = 'account/logout_confirm.html'
    
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, _('You have been logged out successfully.'))
        return redirect('marketplace:home')