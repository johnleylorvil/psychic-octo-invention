"""
Django management command to populate test data from B2 bucket images
Usage: python manage.py populate_test_data
"""

import os
import json
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from marketplace.models import (
    User, Category, Product, ProductImage, Banner, 
    VendorProfile, Review, Page
)

class Command(BaseCommand):
    help = 'Populate database with test data using B2 bucket images'
    
    def __init__(self):
        super().__init__()
        self.B2_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'afepanou')
        self.B2_ENDPOINT = getattr(settings, 'AWS_S3_ENDPOINT_URL', 'https://s3.us-east-005.backblazeb2.com')
        self.B2_BASE_URL = f"{self.B2_ENDPOINT}/{self.B2_BUCKET_NAME}"
        self.categories_map = {}
        self.stats = {
            'categories': 0,
            'vendors': 0, 
            'products': 0,
            'banners': 0,
            'reviews': 0,
            'pages': 0
        }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing test data before populating',
        )
        parser.add_argument(
            '--images-file',
            type=str,
            default='images_list.json',
            help='Path to images JSON file',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting Afepanou database population...\n')
        )
        
        # Load images data
        images_file = options['images_file']
        if not os.path.exists(images_file):
            self.stdout.write(
                self.style.ERROR(f'❌ Images file {images_file} not found. Run analyze_b2_bucket.py first.')
            )
            return
        
        with open(images_file, 'r', encoding='utf-8') as f:
            self.images_data = json.load(f)
        
        if options['clear_existing']:
            self.clear_test_data()
        
        # Population steps
        with transaction.atomic():
            self.create_categories()
            self.create_vendors() 
            self.create_products()
            self.create_banners()
            self.create_pages()
        
        self.print_summary()
    
    def clear_test_data(self):
        """Clear existing test data"""
        self.stdout.write('Clearing existing test data...')
        
        # Delete in proper order to respect foreign keys
        ProductImage.objects.all().delete()
        Review.objects.all().delete()
        Product.objects.all().delete()
        VendorProfile.objects.all().delete()
        Banner.objects.all().delete()
        Page.objects.all().delete()
        
        # Keep superuser but delete test users
        User.objects.filter(username__startswith='test_').delete()
        User.objects.filter(is_superuser=False, is_staff=False).delete()
        
        # Delete categories except if they have real data
        Category.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Test data cleared'))
    
    def get_image_url(self, file_path):
        """Generate full B2 URL for image"""
        return f"{self.B2_BASE_URL}/{file_path}"
    
    def create_categories(self):
        """Create product categories"""
        self.stdout.write('Creating categories...')
        
        categories_data = {
            "premiere-necessite": {
                "name": "Produits de Première Nécessité",
                "description": "Produits essentiels pour la vie quotidienne",
                "is_featured": True,
                "sort_order": 1
            },
            "locaux": {
                "name": "Produits Locaux", 
                "description": "Produits fabriqués localement en Haïti",
                "is_featured": True,
                "sort_order": 2
            },
            "patriotiques": {
                "name": "Produits Patriotiques",
                "description": "Artisanat haïtien et produits patriotiques",
                "is_featured": True,
                "sort_order": 3
            },
            "electroniques": {
                "name": "Électroniques",
                "description": "Appareils électroniques et accessoires",
                "is_featured": True,
                "sort_order": 4
            },
            "services": {
                "name": "Services",
                "description": "Services professionnels et personnels",
                "is_featured": True,
                "sort_order": 5
            }
        }
        
        for slug, data in categories_data.items():
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'is_featured': data['is_featured'],
                    'sort_order': data['sort_order'],
                    'is_active': True
                }
            )
            self.categories_map[slug] = category
            if created:
                self.stats['categories'] += 1
                self.stdout.write(f'  Created: {category.name}')
    
    def create_vendors(self):
        """Create test vendor accounts"""
        self.stdout.write('Creating vendor accounts...')
        
        vendors_data = [
            {
                "username": "test_marie_artisan",
                "email": "marie@afepanou.com",
                "first_name": "Marie",
                "last_name": "Dupont",
                "business_name": "Artisanat Marie",
                "business_type": "individual"
            },
            {
                "username": "test_jean_agriculteur",
                "email": "jean@afepanou.com",
                "first_name": "Jean", 
                "last_name": "Pierre",
                "business_name": "Ferme Jean Pierre",
                "business_type": "individual"
            },
            {
                "username": "test_tech_haiti",
                "email": "tech@afepanou.com",
                "first_name": "Paul",
                "last_name": "Moïse", 
                "business_name": "Tech Haiti",
                "business_type": "corporation"
            }
        ]
        
        for vendor_data in vendors_data:
            user, created = User.objects.get_or_create(
                username=vendor_data["username"],
                defaults={
                    "email": vendor_data["email"],
                    "first_name": vendor_data["first_name"],
                    "last_name": vendor_data["last_name"],
                    "is_seller": True,
                    "seller_since": timezone.now(),
                    "city": "Port-au-Prince",
                    "country": "Haïti"
                }
            )
            
            if created:
                user.set_password("testpass123")
                user.save()
                
                # Create vendor profile
                VendorProfile.objects.create(
                    user=user,
                    business_name=vendor_data["business_name"],
                    business_type=vendor_data["business_type"],
                    business_address="Port-au-Prince, Haïti",
                    business_phone="+509 1234-5678",
                    is_verified=True,
                    verification_status="verified"
                )
                
                self.stats['vendors'] += 1
                self.stdout.write(f'  Created vendor: {vendor_data["business_name"]}')
    
    def create_products(self):
        """Create products from B2 images"""
        self.stdout.write('Creating products...')
        
        # Simple product templates
        templates = {
            "premiere-necessite": [
                {"name": "Café Haïtien", "price": 250},
                {"name": "Riz Local", "price": 180},
                {"name": "Haricots Noirs", "price": 120},
            ],
            "locaux": [
                {"name": "Artisanat Local", "price": 450},
                {"name": "Produit Traditionnel", "price": 320},
            ],
            "patriotiques": [
                {"name": "Produit Patriotique", "price": 380},
                {"name": "Artisanat Haïtien", "price": 280},
            ],
            "electroniques": [
                {"name": "Accessoire Électronique", "price": 1250},
                {"name": "Appareil Mobile", "price": 25000},
            ],
            "services": [
                {"name": "Service Professionnel", "price": 1500},
            ]
        }
        
        vendors = list(User.objects.filter(is_seller=True))
        if not vendors:
            return
        
        # Process product images
        for image_data in self.images_data:
            file_path = image_data["file_name"]
            
            # Skip non-product images
            if any(skip in file_path for skip in ["Logo.png", "banners/", "featured/"]):
                continue
            
            # Determine category
            category_slug = None
            if "Première Nécessité" in file_path:
                category_slug = "premiere-necessite"
            elif "Produits Locaux" in file_path:
                category_slug = "locaux"
            elif "Patriotiques" in file_path:
                category_slug = "patriotiques"
            elif "Électroniques" in file_path:
                category_slug = "electroniques" 
            elif "Services" in file_path:
                category_slug = "services"
            
            if not category_slug or category_slug not in self.categories_map:
                continue
            
            # Get template and create product
            template_list = templates.get(category_slug, [])
            if not template_list:
                continue
                
            template = random.choice(template_list)
            
            # Create unique product name
            base_name = template["name"]
            filename = os.path.splitext(os.path.basename(file_path))[0]
            product_name = f"{base_name} - {filename[:20]}"
            
            try:
                product = Product.objects.create(
                    name=product_name,
                    category=self.categories_map[category_slug],
                    seller=random.choice(vendors),
                    short_description=f"Produit de qualité disponible sur Afèpanou",
                    description=f"Excellent {base_name.lower()} disponible sur notre marketplace.",
                    price=Decimal(str(template["price"])),
                    stock_quantity=random.randint(10, 50),
                    is_active=True,
                    origin_country="Haïti"
                )
                
                # Create product image
                ProductImage.objects.create(
                    product=product,
                    image_url=self.get_image_url(file_path),
                    image_path=file_path,
                    alt_text=f"Image de {product.name}",
                    is_primary=True
                )
                
                # Create some reviews
                if random.choice([True, False]):
                    self.create_review(product)
                
                self.stats['products'] += 1
                
                if self.stats['products'] % 10 == 0:
                    self.stdout.write(f'  {self.stats["products"]} products created...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'  WARNING: Skipped {product_name}: {e}')
                )
    
    def create_review(self, product):
        """Create a random review"""
        # Create regular user if needed
        regular_user, created = User.objects.get_or_create(
            username="test_client",
            defaults={
                "email": "client@test.com",
                "first_name": "Client",
                "last_name": "Test"
            }
        )
        
        if created:
            regular_user.set_password("testpass123")
            regular_user.save()
        
        Review.objects.create(
            product=product,
            user=regular_user,
            rating=random.choice([4, 5]),
            comment="Excellent produit, très satisfait!",
            is_approved=True
        )
        self.stats['reviews'] += 1
    
    def create_banners(self):
        """Create homepage banners"""
        self.stdout.write('Creating banners...')
        
        banner_images = [
            img for img in self.images_data
            if "banner" in img["file_name"].lower() or 
            img["file_name"] in ["fresh-food-banner.jpg", "grocery-marketplace-hero.jpg"]
        ]
        
        for i, image_data in enumerate(banner_images[:3]):
            Banner.objects.create(
                title=f"Promotion Spéciale {i+1}",
                subtitle="Découvrez nos produits locaux",
                description="Les meilleurs produits haïtiens sur Afèpanou",
                image_url=self.get_image_url(image_data["file_name"]),
                image_path=image_data["file_name"],
                button_text="Découvrir",
                link_url="/",
                is_active=True,
                sort_order=i
            )
            self.stats['banners'] += 1
    
    def create_pages(self):
        """Create static pages"""
        self.stdout.write('Creating pages...')
        
        pages = [
            {
                "title": "À propos",
                "slug": "a-propos",
                "content": "<h2>Bienvenue sur Afèpanou</h2><p>La marketplace haïtienne.</p>"
            }
        ]
        
        for page_data in pages:
            Page.objects.get_or_create(
                slug=page_data["slug"],
                defaults={
                    "title": page_data["title"],
                    "content": page_data["content"],
                    "is_active": True
                }
            )
            self.stats['pages'] += 1
    
    def print_summary(self):
        """Print creation summary"""
        self.stdout.write(
            self.style.SUCCESS('\nDatabase population completed!')
        )
        self.stdout.write('Summary:')
        for key, value in self.stats.items():
            self.stdout.write(f'   - {key.title()}: {value}')
        
        self.stdout.write(
            self.style.SUCCESS('\nReady to test the application!')
        )