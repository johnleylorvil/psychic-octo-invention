"""
Afèpanou Marketplace - Main URL Configuration
SEO-friendly URL patterns for the Haitian e-commerce marketplace
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.http import HttpResponse

# Import sitemaps
from marketplace.sitemaps import sitemaps

# Custom error handlers
def custom_404_view(request, exception):
    """Custom 404 error handler"""
    from django.shortcuts import render
    return render(request, 'errors/404.html', status=404)

def custom_500_view(request):
    """Custom 500 error handler"""
    from django.shortcuts import render
    return render(request, 'errors/500.html', status=500)

def custom_403_view(request, exception):
    """Custom 403 error handler"""
    from django.shortcuts import render
    return render(request, 'errors/403.html', status=403)

def custom_400_view(request, exception):
    """Custom 400 error handler"""
    from django.shortcuts import render
    return render(request, 'errors/400.html', status=400)

# Robots.txt view
def robots_txt_view(request):
    """Serve robots.txt for SEO"""
    content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /ajax/

Sitemap: https://afepanou.com/sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain')

# Main URL patterns
urlpatterns = [
    # Admin interface with custom site branding
    path('admin/', admin.site.urls),
    
    # SEO and robots
    path('robots.txt', robots_txt_view, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    
    # Health check for monitoring
    path('health/', lambda request: HttpResponse('OK'), name='health_check'),
    
    # API endpoints (versioned)
    path('api/', include([
        path('v1/', include('marketplace.api.urls', namespace='api_v1')),
    ])),
    
    # Main marketplace application
    path('', include('marketplace.urls', namespace='marketplace')),
    
    # Authentication (Django built-in with customization)
    path('auth/', include('django.contrib.auth.urls')),
]

# Custom error handlers
handler404 = custom_404_view
handler500 = custom_500_view
handler403 = custom_403_view
handler400 = custom_400_view

# Static and media files serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar in development
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns