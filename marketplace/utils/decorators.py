# marketplace/utils/decorators.py
"""
Custom decorators for Afèpanou marketplace
"""

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


def seller_required(view_func):
    """Decorator to require user to be a verified seller"""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_seller:
            messages.error(request, _('You must be a registered seller to access this page.'))
            return redirect('become_seller')
        
        # Check if seller profile is complete
        if not hasattr(request.user, 'vendor_profile'):
            messages.error(request, _('Please complete your seller profile.'))
            return redirect('become_seller')
        
        # Check if account is suspended
        if request.user.is_suspended:
            messages.error(request, _('Your seller account is suspended.'))
            return redirect('seller_application_status')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def admin_required(view_func):
    """Decorator to require admin privileges"""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied(_('Admin access required.'))
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def verified_seller_required(view_func):
    """Decorator to require verified seller status"""
    @wraps(view_func)
    @seller_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.vendor_profile.is_verified:
            messages.error(request, _('Your seller account must be verified to access this feature.'))
            return redirect('seller_application_status')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view