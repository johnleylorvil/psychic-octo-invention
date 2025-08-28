# rbackend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API
    path('api/v1/', include('marketplace.api.urls')),
    
    # Marketplace
    path('', include('marketplace.urls')),
]

# Static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)