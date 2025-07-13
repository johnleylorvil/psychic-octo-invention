from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    # Bannières
    path('banners/', views.active_banners, name='active-banners'),
    path('banners/<int:banner_id>/click/', views.track_banner_click, name='track-banner-click'),
    
    # Pages
    path('pages/', views.all_pages, name='all-pages'),
    path('pages/featured/', views.featured_pages, name='featured-pages'),
    path('pages/<slug:slug>/', views.page_detail, name='page-detail'),
    
    # Sections média
    path('sections/', views.media_content_sections, name='media-sections'),
    path('sections/<int:section_id>/products/', views.section_products, name='section-products'),
]