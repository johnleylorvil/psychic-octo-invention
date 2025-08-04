# rbackend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API
    
    
    # Home (page d'accueil)
    path('', include('marketplace.testurls')),
    
    # Store (avec namespace 'store')
    
]