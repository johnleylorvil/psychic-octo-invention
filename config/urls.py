# rbackend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API
    path('api/', include('marketplace.urls')),
    
    # Home (page d'accueil)
    path('', include('marketplace.homeurls')),
    
    # Store (avec namespace 'store')
    path('store/', include('marketplace.storeurls', namespace='store')),
]