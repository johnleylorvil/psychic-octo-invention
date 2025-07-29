from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
import json

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class MissionView(TemplateView):
    template_name = 'pages/mission.html'


class StoryView(TemplateView):
    template_name = 'pages/story.html'


class ValuesView(TemplateView):
    template_name = 'pages/values.html'


class TeamView(TemplateView):
    template_name = 'pages/team.html'


class ImpactView(TemplateView):
    template_name = 'pages/impact.html'


@csrf_exempt
def newsletter_subscribe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            privacy_consent = data.get('privacy_consent', False)
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email requis'
                }, status=400)
            
            if not privacy_consent:
                return JsonResponse({
                    'success': False,
                    'message': 'Consentement requis'
                }, status=400)
            
            return JsonResponse({
                'success': True,
                'message': 'Inscription réussie!'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Données invalides'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Erreur serveur'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    }, status=405)


def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    suggestions = [
        {'text': 'Artisanat traditionnel', 'category': 'artisanats'},
        {'text': 'Café haïtien', 'category': 'agriculture'},
        {'text': 'Produits locaux', 'category': 'locaux'},
        {'text': 'Services consultation', 'category': 'services'},
    ]
    
    filtered_suggestions = [
        s for s in suggestions 
        if query.lower() in s['text'].lower()
    ][:5]
    
    return JsonResponse({
        'suggestions': filtered_suggestions,
        'query': query
    })


def get_category_products(request, category_slug):
    products = {
        'artisanats': [
            {'name': 'Bijoux traditionnels', 'price': '500 HTG'},
            {'name': 'Sculptures en bois', 'price': '1200 HTG'},
        ],
        'agriculture': [
            {'name': 'Café Arabica', 'price': '800 HTG'},
            {'name': 'Mangues fraîches', 'price': '300 HTG'},
        ],
        'services': [
            {'name': 'Consultation Marketing', 'price': '2000 HTG'},
            {'name': 'Design Web', 'price': '5000 HTG'},
        ]
    }
    
    category_products = products.get(category_slug, [])
    
    return JsonResponse({
        'success': True,
        'category': category_slug,
        'products': category_products,
        'count': len(category_products)
    })


def site_stats(request):
    stats = {
        'vendors': 1250,
        'products': 15000,
        'transactions': 75000,
        'departments': 25,
        'last_updated': '2025-01-29T10:30:00Z'
    }
    
    return JsonResponse({
        'success': True,
        'stats': stats
    })


class RobotsView(TemplateView):
    template_name = 'robots.txt'
    content_type = 'text/plain'


class SitemapView(TemplateView):
    template_name = 'sitemap.xml'
    content_type = 'application/xml'