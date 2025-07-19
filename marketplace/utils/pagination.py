# marketplace/utils/pagination.py

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound


class StandardResultsSetPagination(PageNumberPagination):
    """
    Pagination standard pour le marketplace Afèpanou
    Optimisée pour performance et UX moderne
    """
    page_size = 12  # Grid 3x4 optimal pour produits
    page_size_query_param = 'page_size'
    max_page_size = 48  # Maximum pour éviter surcharge serveur
    
    # Messages d'erreur en français
    page_size_query_description = 'Nombre de résultats par page'
    invalid_page_message = 'Page invalide'
    
    def get_paginated_response(self, data):
        """
        Response formatée avec métadonnées complètes pour frontend
        """
        return Response({
            'pagination': {
                # Informations basiques
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'page_size': self.get_page_size(self.request),
                
                # Navigation
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                
                # Informations additionnelles UX
                'start_index': self.page.start_index(),
                'end_index': self.page.end_index(),
                'range_display': f"{self.page.start_index()}-{self.page.end_index()} sur {self.page.paginator.count}",
                
                # Pages adjacentes pour navigation
                'page_links': self._get_page_links(),
            },
            'results': data
        })
    
    def _get_page_links(self):
        """
        Génère les liens de pages adjacentes pour navigation UI
        Exemple: [1, 2, 3, '...', 8, 9, 10]
        """
        current_page = self.page.number
        total_pages = self.page.paginator.num_pages
        
        # Nombre de pages à afficher de chaque côté
        delta = 2
        
        # Calcul des pages à afficher
        start_page = max(1, current_page - delta)
        end_page = min(total_pages, current_page + delta)
        
        pages = []
        
        # Première page si pas dans la range
        if start_page > 1:
            pages.append(1)
            if start_page > 2:
                pages.append('...')
        
        # Pages centrales
        for page_num in range(start_page, end_page + 1):
            pages.append(page_num)
        
        # Dernière page si pas dans la range
        if end_page < total_pages:
            if end_page < total_pages - 1:
                pages.append('...')
            pages.append(total_pages)
        
        return pages
    
    def paginate_queryset(self, queryset, request, view=None):
        """
        Override pour ajouter des validations et optimisations
        """
        # 🎯 CORRECTION: Ajout de cette ligne pour sauvegarder la requête sur l'instance
        self.request = request

        # Validation page size
        page_size = self.get_page_size(request)
        if page_size is None:
            return None
        
        # Optimisation: évite de compter si pas nécessaire
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)
        
        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)
        
        # Cache le count pour éviter requêtes multiples
        if len(self.page) < page_size and not self.page.has_next():
            # Dernière page, on peut calculer le count sans requête
            # (Le bug précédent du TypeError est aussi corrigé ici)
            self.page.paginator._count = (int(page_number) - 1) * page_size + len(self.page)
        
        return list(self.page)


class ProductPagination(StandardResultsSetPagination):
    """
    Pagination spécialisée pour les produits
    Grid layout optimisé
    """
    page_size = 12  # 3x4 grid parfait
    page_size_query_param = 'page_size'
    max_page_size = 24  # Maximum 2 grids pour performance mobile
    
    def get_paginated_response(self, data):
        """
        Response adaptée pour produits avec métadonnées business
        """
        base_response = super().get_paginated_response(data)
        
        # Ajoute des métadonnées spécifiques produits
        base_response.data['meta'] = {
            'grid_layout': '3x4',
            'optimal_page_sizes': [12, 24],
            'recommended_page_size': 12,
            'loading_type': 'pagination',  # vs 'infinite_scroll'
        }
        
        return base_response


class SearchPagination(StandardResultsSetPagination):
    """
    Pagination pour résultats de recherche
    Plus de résultats par page pour meilleure overview
    """
    page_size = 20  # Plus de résultats pour recherche
    page_size_query_param = 'page_size'
    max_page_size = 50
    
    def get_paginated_response(self, data):
        """
        Response adaptée pour recherche avec scoring
        """
        base_response = super().get_paginated_response(data)
        
        # Ajoute métadonnées recherche
        search_query = self.request.query_params.get('q', '')
        base_response.data['search'] = {
            'query': search_query,
            'has_results': len(data) > 0,
            'suggestion': 'Essayez des termes plus généraux' if len(data) == 0 else None,
        }
        
        return base_response


class CategoryPagination(StandardResultsSetPagination):
    """
    Pagination pour produits d'une catégorie
    Optimisée pour navigation catégories
    """
    page_size = 16  # 4x4 grid pour catégories
    page_size_query_param = 'page_size'
    max_page_size = 32
    
    def get_paginated_response(self, data):
        """
        Response avec métadonnées catégorie
        """
        base_response = super().get_paginated_response(data)
        
        # Ajoute métadonnées catégorie
        base_response.data['category_meta'] = {
            'grid_layout': '4x4',
            'sort_options': ['price', 'name', 'created_at', '-created_at'],
            'filter_options': ['price_range', 'brand', 'condition_type'],
        }
        
        return base_response


class InfiniteScrollPagination(PageNumberPagination):
    """
    Pagination pour infinite scroll (mobile)
    Load more pattern
    """
    page_size = 10  # Petites pages pour scroll fluide
    page_size_query_param = None  # Pas de customisation
    max_page_size = 10
    
    def get_paginated_response(self, data):
        """
        Response simplifiée pour infinite scroll
        """
        return Response({
            'results': data,
            'has_more': self.page.has_next(),
            'next_page': self.page.next_page_number() if self.page.has_next() else None,
            'count': self.page.paginator.count if hasattr(self.page, 'paginator') else len(data)
        })


class AdminPagination(StandardResultsSetPagination):
    """
    Pagination pour interface admin
    Plus d'éléments par page pour gestion bulk
    """
    page_size = 50  # Plus d'éléments pour admin
    page_size_query_param = 'page_size'
    max_page_size = 200
    
    def get_paginated_response(self, data):
        """
        Response avec outils admin
        """
        base_response = super().get_paginated_response(data)
        
        # Ajoute outils admin
        base_response.data['admin_tools'] = {
            'bulk_actions': ['delete', 'activate', 'deactivate'],
            'export_formats': ['csv', 'xlsx', 'json'],
            'quick_filters': ['active', 'inactive', 'featured'],
        }
        
        return base_response


# Utilitaires pour pagination
class PaginationUtils:
    """
    Utilitaires helper pour pagination
    """
    
    @staticmethod
    def get_pagination_class(view_type='default'):
        """
        Retourne la classe pagination selon le type de vue
        """
        pagination_classes = {
            'default': StandardResultsSetPagination,
            'products': ProductPagination,
            'search': SearchPagination,
            'category': CategoryPagination,
            'infinite': InfiniteScrollPagination,
            'admin': AdminPagination,
        }
        return pagination_classes.get(view_type, StandardResultsSetPagination)
    
    @staticmethod
    def calculate_optimal_page_size(total_items, target_pages=5):
        """
        Calcule la taille de page optimale pour un nombre cible de pages
        """
        if total_items <= 0:
            return 12
        
        optimal_size = max(12, total_items // target_pages)
        
        # Arrondi aux multiples de 12 (grid 3x4)
        return ((optimal_size // 12) + 1) * 12
    
    @staticmethod
    def get_page_size_options():
        """
        Retourne les options de taille de page disponibles
        """
        return [
            {'value': 12, 'label': '12 par page', 'grid': '3x4'},
            {'value': 24, 'label': '24 par page', 'grid': '6x4'},
            {'value': 36, 'label': '36 par page', 'grid': '9x4'},
            {'value': 48, 'label': '48 par page', 'grid': '12x4'},
        ]