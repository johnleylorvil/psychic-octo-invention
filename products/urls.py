from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Catégories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<slug:slug>/products/', views.category_products, name='category-products'),
    
    # Produits
    path('', views.ProductListView.as_view(), name='product-list'),
    path('featured/', views.featured_products, name='featured-products'),
    path('search/', views.search_products, name='search-products'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # Avis
    path('<int:product_id>/reviews/', views.product_reviews, name='product-reviews'),
    path('<int:product_id>/reviews/create/', views.create_review, name='create-review'),
]