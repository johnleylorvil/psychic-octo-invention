# ======================================
# apps/users/urls.py
# ======================================

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

urlpatterns = [
    # Authentification
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Profil utilisateur
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update-profile'),
    path('change-password/', views.change_password, name='change-password'),
    
    # Vendeur
    path('request-seller/', views.request_seller_status, name='request-seller'),
]