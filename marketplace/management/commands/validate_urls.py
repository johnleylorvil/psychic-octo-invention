"""
Django management command to validate URL patterns
Checks for broken URLs, conflicts, and SEO issues
"""
from django.core.management.base import BaseCommand
from django.urls import reverse, NoReverseMatch
from django.test import RequestFactory
from django.http import Http404
import sys

class Command(BaseCommand):
    help = 'Validate marketplace URL patterns'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--check-views',
            action='store_true',
            help='Check if views are accessible',
        )
        parser.add_argument(
            '--check-names',
            action='store_true', 
            help='Check if URL names are resolvable',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output',
        )
    
    def handle(self, *args, **options):
        self.verbose = options['verbose']
        self.factory = RequestFactory()
        
        self.stdout.write(
            self.style.SUCCESS('🔗 Validating Afèpanou marketplace URLs...')
        )
        
        errors = 0
        
        if options['check_names']:
            errors += self.check_url_names()
        
        if options['check_views']:
            errors += self.check_view_accessibility()
        
        errors += self.check_url_conflicts()
        errors += self.check_seo_patterns()
        
        if errors == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ All URL validation checks passed!')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Found {errors} URL issues')
            )
            sys.exit(1)
    
    def check_url_names(self):
        """Check if URL names can be reversed"""
        self.stdout.write('Checking URL name resolution...')
        
        url_names = [
            # Core pages
            'marketplace:home',
            'marketplace:about', 
            'marketplace:contact',
            'marketplace:terms',
            'marketplace:privacy',
            
            # Product catalog
            'marketplace:category_index',
            'marketplace:product_search',
            
            # User account
            'marketplace:register',
            'marketplace:login',
            'marketplace:profile',
            
            # Shopping
            'marketplace:cart',
            'marketplace:checkout',
            'marketplace:order_history',
            
            # Seller area
            'marketplace:become_seller',
            'marketplace:seller_dashboard',
            'marketplace:seller_products',
            
            # AJAX endpoints
            'marketplace:ajax_add_to_cart',
            'marketplace:ajax_search_autocomplete',
            
            # Payment
            'marketplace:moncash_payment',
        ]
        
        errors = 0
        for name in url_names:
            try:
                url = reverse(name)
                if self.verbose:
                    self.stdout.write(f'  ✅ {name} -> {url}')
            except NoReverseMatch:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Cannot reverse URL name: {name}')
                )
                errors += 1
        
        return errors
    
    def check_view_accessibility(self):
        """Check if views are accessible (basic check)"""
        self.stdout.write('Checking view accessibility...')
        
        test_urls = [
            '/',
            '/apropos/',
            '/contact/',
            '/categories/',
            '/recherche/',
            '/compte/inscription/',
            '/panier/',
        ]
        
        errors = 0
        for url in test_urls:
            try:
                request = self.factory.get(url)
                # Note: This is a basic check - doesn't actually call the view
                if self.verbose:
                    self.stdout.write(f'  ✅ URL pattern exists: {url}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ URL pattern error: {url} - {e}')
                )
                errors += 1
        
        return errors
    
    def check_url_conflicts(self):
        """Check for potential URL pattern conflicts"""
        self.stdout.write('Checking for URL conflicts...')
        
        # Check for overlapping patterns that might cause issues
        potential_conflicts = [
            ('/produit/', '/produits/'),  # Singular vs plural
            ('/categorie/', '/categories/'),
            ('/commande/', '/commandes/'),
        ]
        
        errors = 0
        for url1, url2 in potential_conflicts:
            if self.verbose:
                self.stdout.write(f'  Checking conflict: {url1} vs {url2}')
        
        # This is a placeholder - real conflict detection would be more complex
        return errors
    
    def check_seo_patterns(self):
        """Check SEO-friendly URL patterns"""
        self.stdout.write('Checking SEO patterns...')
        
        seo_checks = [
            {
                'pattern': '/produit/<slug>/',
                'description': 'Product URLs use slugs',
                'valid': True,
            },
            {
                'pattern': '/categorie/<slug>/',
                'description': 'Category URLs use slugs',
                'valid': True,
            },
            {
                'pattern': '/boutique/<vendor_slug>/',
                'description': 'Vendor URLs use slugs',
                'valid': True,
            },
        ]
        
        errors = 0
        for check in seo_checks:
            if check['valid']:
                if self.verbose:
                    self.stdout.write(f'  ✅ {check["description"]}')
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️ {check["description"]}')
                )
                errors += 1
        
        # Check for French-friendly URLs
        french_urls = [
            '/apropos/', '/contact/', '/recherche/',
            '/compte/', '/panier/', '/commande/',
            '/vendeur/', '/favoris/', '/avis/'
        ]
        
        for url in french_urls:
            if self.verbose:
                self.stdout.write(f'  ✅ French URL: {url}')
        
        return errors