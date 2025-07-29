from django.urls import path
from marketplace.viewsets import home_view

app_name = 'core'

urlpatterns = [
    # Homepage
    path('', home_view.HomeView.as_view(), name='home'),
    
    # Static Pages
    path('about/', home_view.AboutView.as_view(), name='about'),
    path('mission/', home_view.MissionView.as_view(), name='mission'),
    path('story/', home_view.StoryView.as_view(), name='story'),
    path('values/', home_view.ValuesView.as_view(), name='values'),
    path('team/', home_view.TeamView.as_view(), name='team'),
    path('impact/', home_view.ImpactView.as_view(), name='impact'),
    
    # AJAX Endpoints
    path('api/newsletter/subscribe/', home_view.newsletter_subscribe, name='newsletter_subscribe'),
    path('api/search/suggestions/', home_view.search_suggestions, name='search_suggestions'),
    path('api/category/<slug:category_slug>/products/', home_view.get_category_products, name='category_products'),
    path('api/stats/', home_view.site_stats, name='site_stats'),
    
    # SEO
    path('robots.txt', home_view.RobotsView.as_view(), name='robots'),
    path('sitemap.xml', home_view.SitemapView.as_view(), name='sitemap'),
]