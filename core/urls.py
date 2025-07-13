# ======================================
# apps/core/urls.py
# ======================================

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Paramètres du site
    path('settings/', views.site_settings, name='site-settings'),
    path('settings/group/<str:group_name>/', views.site_settings_by_group, name='site-settings-group'),
    
    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', views.newsletter_unsubscribe, name='newsletter-unsubscribe'),
    path('newsletter/stats/', views.newsletter_stats, name='newsletter-stats'),
]
