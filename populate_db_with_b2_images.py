#!/usr/bin/env python3
"""
populate_db_with_b2_images.py
Database population script for Afèpanou marketplace using B2 bucket images
"""

import os
import sys
import json
import random
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

# Add the project directory to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from marketplace.models import (
    User, Category, Product, ProductImage, Banner, 
    VendorProfile, Review, Page, MediaContentSection
)

# B2 Bucket Configuration
B2_BUCKET_NAME = "afepanou"
B2_ENDPOINT_URL = "https://s3.us-east-005.backblazeb2.com"
B2_BASE_URL = f"{B2_ENDPOINT_URL}/{B2_BUCKET_NAME}"

class DatabasePopulator:
    def __init__(self):
        self.images_data = self.load_images_data()
        self.categories_map = {}
        self.products_created = 0
        self.banners_created = 0
        
    def load_images_data(self):
        """Load images data from JSON file"""
        try:
            with open('images_list.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Error: images_list.json not found. Please run analyze_b2_bucket.py first.")
            sys.exit(1)
            
    def get_image_url(self, file_path):
        """Generate full B2 URL for image"""
        return f"{B2_BASE_URL}/{file_path}"
    
    def create_categories(self):
        """Create product categories based on B2 folder structure"""
        print("📂 Creating categories...")
        
        categories_data = {
            "premiere-necessite": {
                "name": "Produits de Première Nécessité",
                "description": "Produits essentiels pour la vie quotidienne en Haïti",
                "icon": "🛒",
                "is_featured": True,
                "sort_order": 1
            },
            "locaux": {
                "name": "Produits Locaux",
                "description": "Produits fabriqués localement en Haïti",
                "icon": "🏺",
                "is_featured": True,
                "sort_order": 2
            },
            "patriotiques": {
                "name": "Produits Patriotiques et Artisanaux",
                "description": "Artisanat haïtien et produits patriotiques",
                "icon": "🇭🇹",
                "is_featured": True,
                "sort_order": 3
            },
            "electroniques": {
                "name": "Produits Électroniques",
                "description": "Appareils électroniques et accessoires",
                "icon": "📱",
                "is_featured": True,
                "sort_order": 4
            },
            "services": {
                "name": "Services Divers",
                "description": "Services professionnels et personnels",
                "icon": "🔧",
                "is_featured": True,
                "sort_order": 5
            },
            "agricole": {
                "name": "Produits Agricoles",
                "description": "Fruits, légumes et produits agricoles locaux",
                "icon": "🌾",
                "parent": "locaux",
                "sort_order": 6
            },
            "artisanat": {
                "name": "Artisanat",
                "description": "Objets d'art et artisanat traditionnel",
                "icon": "🎨",
                "parent": "patriotiques",
                "sort_order": 7
            }
        }
        
        # Create parent categories first
        for slug, data in categories_data.items():
            if 'parent' not in data:
                category, created = Category.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': data['name'],
                        'description': data['description'],
                        'is_featured': data.get('is_featured', False),
                        'sort_order': data['sort_order'],
                        'is_active': True
                    }
                )
                self.categories_map[slug] = category
                if created:
                    print(f"  ✅ Created category: {category.name}")
        
        # Create subcategories
        for slug, data in categories_data.items():
            if 'parent' in data:
                parent_category = self.categories_map.get(data['parent'])
                category, created = Category.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': data['name'],
                        'description': data['description'],
                        'parent': parent_category,
                        'sort_order': data['sort_order'],
                        'is_active': True
                    }
                )
                self.categories_map[slug] = category
                if created:
                    print(f"  ✅ Created subcategory: {category.name}")
    
    def create_users_and_vendors(self):
        """Create test users and vendor profiles"""
        print("👥 Creating users and vendors...")
        
        vendors_data = [
            {
                "username": "marie_artisan",
                "email": "marie@afepanou.com",
                "first_name": "Marie",
                "last_name": "Dupont",
                "business_name": "Artisanat Marie",
                "business_type": "individual",
                "business_description": "Artisanat traditionnel haïtien fait main",
                "categories": ["patriotiques", "artisanat"]
            },
            {
                "username": "jean_agriculteur",
                "email": "jean@afepanou.com", 
                "first_name": "Jean",
                "last_name": "Pierre",
                "business_name": "Ferme Jean Pierre",
                "business_type": "individual",
                "business_description": "Producteur local de fruits et légumes",
                "categories": ["locaux", "agricole"]
            },
            {
                "username": "tech_haiti",
                "email": "contact@techhaiti.com",
                "first_name": "Paul",
                "last_name": "Moïse",
                "business_name": "Tech Haiti Store",
                "business_type": "corporation",
                "business_description": "Vente d'appareils électroniques",
                "categories": ["electroniques"]
            },
            {
                "username": "services_pro",
                "email": "info@servicespro.ht",
                "first_name": "Claire",
                "last_name": "Joseph",
                "business_name": "Services Professionnels",
                "business_type": "sole_proprietorship", 
                "business_description": "Services divers pour particuliers et entreprises",
                "categories": ["services"]
            },
            {
                "username": "epicerie_locale",
                "email": "contact@epicerielocale.ht",
                "first_name": "Robert",
                "last_name": "Charles",
                "business_name": "Épicerie Locale",
                "business_type": "individual",
                "business_description": "Produits de première nécessité",
                "categories": ["premiere-necessite"]
            }
        ]
        
        for vendor_data in vendors_data:
            # Create user
            user, created = User.objects.get_or_create(
                username=vendor_data["username"],
                defaults={
                    "email": vendor_data["email"],
                    "first_name": vendor_data["first_name"],
                    "last_name": vendor_data["last_name"],
                    "is_seller": True,
                    "seller_since": timezone.now(),
                    "phone": f"+509 {random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                    "city": "Port-au-Prince",
                    "country": "Haïti"
                }
            )
            
            if created:
                user.set_password("afepanoutest123")
                user.save()
                print(f"  ✅ Created user: {user.username}")
                
                # Create vendor profile
                vendor_profile, vp_created = VendorProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "business_name": vendor_data["business_name"],
                        "business_type": vendor_data["business_type"],
                        "business_description": vendor_data["business_description"],
                        "business_address": f"{random.randint(10, 999)} Rue de la Paix, Port-au-Prince",
                        "business_phone": f"+509 {random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                        "business_email": vendor_data["email"],
                        "is_verified": True,
                        "verification_status": "verified",
                        "verified_at": timezone.now()
                    }
                )
                
                if vp_created:
                    print(f"  ✅ Created vendor profile: {vendor_profile.business_name}")
    
    def create_products_from_images(self):
        """Create products using B2 bucket images"""
        print("🛍️ Creating products from B2 images...")
        
        # Product templates by category
        product_templates = {
            "premiere-necessite": [
                {"name": "Café Haïtien Premium", "base_price": 250, "description": "Café 100% haïtien cultivé dans nos montagnes"},
                {"name": "Riz Local", "base_price": 180, "description": "Riz de qualité supérieure produit localement"},
                {"name": "Haricots Noirs", "base_price": 120, "description": "Haricots noirs riches en protéines"},
                {"name": "Huile Végétale", "base_price": 350, "description": "Huile de cuisson de première qualité"},
                {"name": "Conserves de Poisson", "base_price": 95, "description": "Poisson en conserve, source de protéines"},
                {"name": "Dentifrice", "base_price": 45, "description": "Hygiène dentaire quotidienne"},
                {"name": "Sauce Tomate", "base_price": 35, "description": "Sauce tomate concentrée pour vos plats"},
                {"name": "Lentilles", "base_price": 140, "description": "Lentilles séchées riches en fibres"},
                {"name": "Farine de Maïs", "base_price": 85, "description": "Farine de maïs pour préparations locales"}
            ],
            "locaux": [
                {"name": "Bol en Céramique Artisanal", "base_price": 450, "description": "Bol en céramique fait main par nos artisans"},
                {"name": "Chapeau de Paille Traditionnel", "base_price": 320, "description": "Chapeau de paille tressée à la main"},
                {"name": "Chemise Traditionnelle", "base_price": 680, "description": "Chemise traditionnelle haïtienne"},
                {"name": "Collier en Graines", "base_price": 180, "description": "Bijoux artisanaux en graines locales"},
                {"name": "Huile de Palma Christi", "base_price": 220, "description": "Huile naturelle aux vertus thérapeutiques"},
                {"name": "Savon au Moringa", "base_price": 65, "description": "Savon naturel enrichi au moringa"},
                {"name": "Valise en Paille", "base_price": 890, "description": "Valise artisanale en paille tressée"},
                {"name": "Vase en Céramique", "base_price": 520, "description": "Vase décoratif en céramique peinte"}
            ],
            "patriotiques": [
                {"name": "Sculpture en Bois Haïtienne", "base_price": 850, "description": "Sculpture artisanale représentant la culture haïtienne"},
                {"name": "Bijoux aux Couleurs d'Haïti", "base_price": 380, "description": "Bijoux artisanaux aux couleurs du drapeau"},
                {"name": "Bracelet Haïti", "base_price": 280, "description": "Bracelet patriotique fait main"},
                {"name": "Drapeau de Table", "base_price": 150, "description": "Petit drapeau haïtien pour décoration"},
                {"name": "T-Shirt 'Fier d'être Haïtien'", "base_price": 420, "description": "T-shirt patriotique de qualité"},
                {"name": "Grand Drapeau Haïti", "base_price": 680, "description": "Grand drapeau haïtien officiel"},
                {"name": "Portrait Héros de l'Indépendance", "base_price": 950, "description": "Tableau des héros de l'indépendance"},
                {"name": "Pendentif Haïti", "base_price": 190, "description": "Pendentif carte d'Haïti"},
                {"name": "Pin Drapeau Haïti", "base_price": 45, "description": "Pin's drapeau haïtien"},
                {"name": "Tableau Artistique", "base_price": 1200, "description": "Œuvre d'art originale haïtienne"}
            ],
            "electroniques": [
                {"name": "Coque iPhone Protection", "base_price": 280, "description": "Coque de protection pour iPhone"},
                {"name": "Casque Audio Premium", "base_price": 1250, "description": "Casque audio haute qualité"},
                {"name": "iPhone 14", "base_price": 45000, "description": "iPhone 14 dernière génération"},
                {"name": "iPhone 15", "base_price": 52000, "description": "iPhone 15 avec technologie avancée"},
                {"name": "Samsung Galaxy", "base_price": 38000, "description": "Smartphone Samsung dernière génération"},
                {"name": "Coque Samsung Silicone", "base_price": 220, "description": "Coque en silicone pour Samsung"},
                {"name": "Smart TV", "base_price": 28000, "description": "Télévision intelligente HD"}
            ],
            "services": [
                {"name": "Service Comptabilité", "base_price": 2500, "description": "Services comptables professionnels"},
                {"name": "Aide Démarches Administratives", "base_price": 800, "description": "Assistance pour démarches légales"},
                {"name": "Cours d'Anglais Privés", "base_price": 1200, "description": "Cours particuliers d'anglais"},
                {"name": "Formation Informatique", "base_price": 3500, "description": "Formation en bureautique et informatique"},
                {"name": "Cours Particuliers Mathématiques", "base_price": 1500, "description": "Soutien scolaire en mathématiques"},
                {"name": "Service Livraison Colis", "base_price": 150, "description": "Livraison rapide dans Port-au-Prince"},
                {"name": "Nettoyage Résidentiel", "base_price": 1800, "description": "Service de nettoyage à domicile"},
                {"name": "Nettoyage Appartement", "base_price": 2200, "description": "Nettoyage complet d'appartement"},
                {"name": "Réparation Écran Téléphone", "base_price": 1250, "description": "Réparation d'écrans de smartphones"}
            ]
        }
        
        # Get vendors for each category
        vendors = list(User.objects.filter(is_seller=True))
        
        for image_data in self.images_data:
            file_path = image_data["file_name"]
            
            # Skip non-product images
            if any(skip in file_path for skip in ["Logo.png", "banners/", "featured/", "bestproduct/", "payments/", ".jpg"]):
                continue
            
            # Determine category from file path
            category_slug = None
            template_category = None
            
            if "Première Nécessité" in file_path:
                category_slug = "premiere-necessite"
                template_category = "premiere-necessite"
            elif "Produits Locaux" in file_path:
                category_slug = "locaux"
                template_category = "locaux"
            elif "Patriotiques et Artisanaux" in file_path:
                category_slug = "patriotiques"
                template_category = "patriotiques"
            elif "Électroniques" in file_path:
                category_slug = "electroniques"
                template_category = "electroniques"
            elif "Services Divers" in file_path:
                category_slug = "services"
                template_category = "services"
            elif "produits/locaux/agricole" in file_path:
                category_slug = "agricole"
                template_category = "locaux"
            elif "produits/locaux/artisanat" in file_path or "produits/patriotiques" in file_path:
                category_slug = "artisanat"
                template_category = "patriotiques"
            
            if not category_slug or category_slug not in self.categories_map:
                continue
                
            # Get random product template
            if template_category and template_category in product_templates:
                templates = product_templates[template_category]
                if templates:
                    template = random.choice(templates)
                    product_templates[template_category].remove(template)  # Don't reuse
                else:
                    continue
            else:
                continue
            
            # Create product
            category = self.categories_map[category_slug]
            vendor = random.choice(vendors)
            
            # Generate product name based on image filename if template is exhausted
            base_name = template["name"]
            filename = os.path.splitext(os.path.basename(file_path))[0]
            
            product, created = Product.objects.get_or_create(
                name=base_name,
                seller=vendor,
                defaults={
                    "category": category,
                    "short_description": template["description"],
                    "description": f"{template['description']}. Produit de qualité disponible sur Afèpanou.",
                    "price": Decimal(str(template["base_price"])),
                    "promotional_price": Decimal(str(template["base_price"] * 0.85)) if random.choice([True, False]) else None,
                    "stock_quantity": random.randint(5, 50),
                    "is_active": True,
                    "is_featured": random.choice([True, False, False, False]),  # 25% chance
                    "weight": Decimal(str(random.uniform(0.1, 5.0))),
                    "brand": "Haïti Local" if "locaux" in category_slug else "Afèpanou",
                    "origin_country": "Haïti",
                    "condition_type": "new"
                }
            )
            
            if created:
                # Create product image
                ProductImage.objects.create(
                    product=product,
                    image_url=self.get_image_url(file_path),
                    image_path=file_path,
                    alt_text=f"Image de {product.name}",
                    title=product.name,
                    is_primary=True,
                    sort_order=0
                )
                
                self.products_created += 1
                print(f"  ✅ Created product: {product.name} ({category.name})")
                
                # Add some reviews randomly
                if random.choice([True, False]):
                    self.create_product_reviews(product)
    
    def create_product_reviews(self, product):
        """Create random reviews for a product"""
        review_texts = [
            "Excellent produit, très satisfait de mon achat!",
            "Qualité au rendez-vous, je recommande vivement.",
            "Produit conforme à la description, livraison rapide.",
            "Très bon rapport qualité-prix, je rachèterai.",
            "Service client excellent, produit de qualité.",
            "Exactement ce que je cherchais, parfait!",
            "Produit authentique, très content de mon achat."
        ]
        
        # Create 1-3 reviews per product
        num_reviews = random.randint(1, 3)
        regular_users = User.objects.filter(is_seller=False)
        
        if not regular_users.exists():
            # Create some regular users for reviews
            for i in range(5):
                user = User.objects.create(
                    username=f"client_{i+1}",
                    email=f"client{i+1}@example.com",
                    first_name=f"Client{i+1}",
                    last_name="Test"
                )
                user.set_password("testpass123")
                user.save()
        
        regular_users = User.objects.filter(is_seller=False)
        
        for _ in range(num_reviews):
            Review.objects.create(
                product=product,
                user=random.choice(regular_users),
                rating=random.choice([4, 5, 5, 5]),  # Mostly good reviews
                comment=random.choice(review_texts),
                is_approved=True
            )
    
    def create_banners(self):
        """Create banners using B2 images"""
        print("🎨 Creating banners...")
        
        banner_images = [
            img for img in self.images_data 
            if "banners/" in img["file_name"] or img["file_name"] in [
                "fresh-food-banner.jpg", "grocery-marketplace-hero.jpg", 
                "local-artisan-hero.png", "patriotic-marketplace-hero.png",
                "professional-services-hero.jpg", "tech-gadgets-banner.png"
            ]
        ]
        
        banner_data = [
            {
                "title": "Produits Agricoles Frais",
                "subtitle": "Mangues, avocats et produits locaux",
                "description": "Découvrez nos produits agricoles frais directement des producteurs haïtiens",
                "button_text": "Voir les produits",
                "link_url": "/categories/agricole/",
                "layout_type": "hero"
            },
            {
                "title": "Fête du Drapeau 2025",
                "subtitle": "Célébrons ensemble notre patrimoine",
                "description": "Collection spéciale produits patriotiques pour la fête du drapeau",
                "button_text": "Collection patriotique", 
                "link_url": "/categories/patriotiques/",
                "layout_type": "carousel"
            },
            {
                "title": "Formation Informatique",
                "subtitle": "Développez vos compétences numériques",
                "description": "Cours d'informatique et bureautique avec des professionnels qualifiés",
                "button_text": "S'inscrire",
                "link_url": "/categories/services/",
                "layout_type": "sidebar"
            }
        ]
        
        for i, banner_info in enumerate(banner_data):
            if i < len(banner_images):
                image_data = banner_images[i]
                
                Banner.objects.create(
                    title=banner_info["title"],
                    subtitle=banner_info["subtitle"],
                    description=banner_info["description"],
                    image_url=self.get_image_url(image_data["file_name"]),
                    image_path=image_data["file_name"],
                    link_url=banner_info["link_url"],
                    button_text=banner_info["button_text"],
                    layout_type=banner_info["layout_type"],
                    is_active=True,
                    sort_order=i,
                    view_count=random.randint(100, 1000),
                    click_count=random.randint(10, 100)
                )
                
                self.banners_created += 1
                print(f"  ✅ Created banner: {banner_info['title']}")
    
    def create_content_pages(self):
        """Create static content pages"""
        print("📄 Creating content pages...")
        
        pages_data = [
            {
                "title": "À propos d'Afèpanou",
                "slug": "a-propos",
                "content": """
                <h2>Bienvenue sur Afèpanou</h2>
                <p>Afèpanou est la première plateforme e-commerce dédiée aux produits et services haïtiens. 
                Notre mission est de connecter les producteurs locaux avec les consommateurs, 
                en valorisant le savoir-faire et l'authenticité de nos artisans.</p>
                
                <h3>Notre Vision</h3>
                <p>Créer un écosystème numérique qui soutient l'économie haïtienne en offrant 
                une vitrine moderne et sécurisée pour nos entrepreneurs locaux.</p>
                """,
                "is_featured": True
            },
            {
                "title": "Politique de Confidentialité",
                "slug": "politique-confidentialite",
                "content": """
                <h2>Politique de Confidentialité</h2>
                <p>Chez Afèpanou, nous prenons la protection de vos données personnelles très au sérieux...</p>
                """,
                "is_active": True
            },
            {
                "title": "Conditions d'Utilisation",
                "slug": "conditions-utilisation", 
                "content": """
                <h2>Conditions d'Utilisation</h2>
                <p>En utilisant la plateforme Afèpanou, vous acceptez les conditions suivantes...</p>
                """,
                "is_active": True
            }
        ]
        
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()
        
        for page_data in pages_data:
            Page.objects.get_or_create(
                slug=page_data["slug"],
                defaults={
                    "title": page_data["title"],
                    "content": page_data["content"],
                    "is_active": page_data.get("is_active", True),
                    "is_featured": page_data.get("is_featured", False),
                    "author": admin_user
                }
            )
            print(f"  ✅ Created page: {page_data['title']}")
    
    @transaction.atomic
    def populate(self):
        """Main population method"""
        print("🚀 Starting database population with B2 images...\n")
        
        # Create categories
        self.create_categories()
        
        # Create users and vendors
        self.create_users_and_vendors()
        
        # Create products from images
        self.create_products_from_images()
        
        # Create banners
        self.create_banners()
        
        # Create content pages
        self.create_content_pages()
        
        print(f"\n✅ Database population completed!")
        print(f"📊 Summary:")
        print(f"   • Categories: {len(self.categories_map)}")
        print(f"   • Vendors: {User.objects.filter(is_seller=True).count()}")
        print(f"   • Products: {self.products_created}")
        print(f"   • Banners: {self.banners_created}")
        print(f"   • Reviews: {Review.objects.count()}")
        print(f"   • Pages: {Page.objects.count()}")

if __name__ == "__main__":
    populator = DatabasePopulator()
    
    # Check if images data exists
    if not populator.images_data:
        print("❌ No images data found. Please run analyze_b2_bucket.py first.")
        sys.exit(1)
    
    print(f"📊 Found {len(populator.images_data)} images in B2 bucket")
    
    # Confirm before proceeding
    response = input("\n⚠️  This will populate the database with test data. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    # Run population
    try:
        populator.populate()
        print("\n🎉 Database successfully populated with B2 images!")
    except Exception as e:
        print(f"\n❌ Error during population: {e}")
        raise