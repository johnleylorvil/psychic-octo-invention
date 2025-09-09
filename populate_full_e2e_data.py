#!/usr/bin/env python3
"""
populate_full_e2e_data.py
Complete end-to-end data population for Afèpanou marketplace
Populates all remaining tables for full simulation readiness
"""

import os
import sys
import random
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password

# Setup Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from marketplace.models import (
    User, Category, Product, ProductImage, Banner, VendorProfile, Review, Page,
    Cart, CartItem, Order, OrderItem, OrderStatusHistory, Transaction,
    Wishlist, WishlistItem, WishlistCollection, WishlistCollectionItem, ProductAlert,
    Address, SavedLocation, NewsletterSubscriber, SiteSetting, Promotion,
    MediaContentSection
)

class FullDataPopulator:
    def __init__(self):
        self.stats = {
            'customers': 0,
            'addresses': 0,
            'carts': 0,
            'cart_items': 0,
            'orders': 0,
            'order_items': 0,
            'transactions': 0,
            'wishlists': 0,
            'wishlist_items': 0,
            'alerts': 0,
            'newsletter': 0,
            'promotions': 0,
            'settings': 0,
            'media_sections': 0
        }
    
    @transaction.atomic
    def populate_all(self):
        """Populate all remaining tables for E2E simulation"""
        print("🚀 Starting comprehensive E2E data population...\n")
        
        # Create regular customers
        self.create_customers()
        
        # Create addresses
        self.create_addresses()
        
        # Create shopping carts with items
        self.create_carts_and_items()
        
        # Create orders and transactions
        self.create_orders_and_transactions()
        
        # Create wishlists
        self.create_wishlists()
        
        # Create product alerts
        self.create_product_alerts()
        
        # Create newsletter subscribers
        self.create_newsletter_subscribers()
        
        # Create promotions
        self.create_promotions()
        
        # Create site settings
        self.create_site_settings()
        
        # Create media content sections
        self.create_media_content_sections()
        
        self.print_summary()
    
    def create_customers(self):
        """Create regular customer accounts"""
        print("👥 Creating customer accounts...")
        
        customers_data = [
            {
                "username": "marie_client",
                "email": "marie.customer@gmail.com",
                "first_name": "Marie",
                "last_name": "Jean",
                "phone": "+509 3456-7890",
                "city": "Port-au-Prince"
            },
            {
                "username": "pierre_acheteur",
                "email": "pierre.buyer@yahoo.com", 
                "first_name": "Pierre",
                "last_name": "Louis",
                "phone": "+509 4567-8901",
                "city": "Cap-Haïtien"
            },
            {
                "username": "claire_shopper",
                "email": "claire.shop@hotmail.com",
                "first_name": "Claire",
                "last_name": "Moïse",
                "phone": "+509 5678-9012",
                "city": "Les Cayes"
            },
            {
                "username": "jean_customer",
                "email": "jean.customer@aol.com",
                "first_name": "Jean",
                "last_name": "Baptiste",
                "phone": "+509 6789-0123",
                "city": "Gonaïves"
            },
            {
                "username": "rose_buyer",
                "email": "rose.buyer@gmail.com",
                "first_name": "Rose",
                "last_name": "Pierre",
                "phone": "+509 7890-1234",
                "city": "Port-au-Prince"
            }
        ]
        
        for customer_data in customers_data:
            user, created = User.objects.get_or_create(
                username=customer_data["username"],
                defaults={
                    "email": customer_data["email"],
                    "first_name": customer_data["first_name"],
                    "last_name": customer_data["last_name"],
                    "phone": customer_data["phone"],
                    "city": customer_data["city"],
                    "country": "Haïti",
                    "is_seller": False,
                    "email_verified": True,
                    "phone_verified": random.choice([True, False])
                }
            )
            
            if created:
                user.set_password("customer123")
                user.save()
                self.stats['customers'] += 1
                print(f"  ✅ Created customer: {user.get_display_name()}")
    
    def create_addresses(self):
        """Create addresses for customers"""
        print("📍 Creating customer addresses...")
        
        customers = User.objects.filter(is_seller=False)
        
        address_templates = [
            {"address": "15 Rue Capois", "city": "Port-au-Prince", "type": "home"},
            {"address": "23 Avenue John Brown", "city": "Port-au-Prince", "type": "work"},
            {"address": "8 Rue Geffrard", "city": "Cap-Haïtien", "type": "home"},
            {"address": "45 Boulevard Jean-Jacques Dessalines", "city": "Les Cayes", "type": "home"},
            {"address": "12 Rue Stenio Vincent", "city": "Gonaïves", "type": "home"},
            {"address": "67 Avenue Lamartinière", "city": "Port-au-Prince", "type": "work"},
        ]
        
        for customer in customers:
            # Create 1-2 addresses per customer
            num_addresses = random.randint(1, 2)
            for i in range(num_addresses):
                template = random.choice(address_templates)
                
                Address.objects.create(
                    user=customer,
                    full_name=customer.get_display_name(),
                    phone=customer.phone or "+509 1234-5678",
                    address_line_1=template["address"],
                    city=template["city"],
                    country="Haïti",
                    address_type=template["type"],
                    is_default=(i == 0)  # First address is default
                )
                self.stats['addresses'] += 1
        
        print(f"  ✅ Created {self.stats['addresses']} addresses")
    
    def create_carts_and_items(self):
        """Create shopping carts with items"""
        print("🛒 Creating shopping carts...")
        
        customers = User.objects.filter(is_seller=False)
        products = list(Product.objects.filter(is_active=True))
        
        for customer in customers:
            # 70% chance customer has active cart
            if random.random() < 0.7:
                cart = Cart.objects.create(
                    user=customer,
                    is_active=True
                )
                
                # Add 1-5 items to cart
                num_items = random.randint(1, 5)
                cart_products = random.sample(products, min(num_items, len(products)))
                
                for product in cart_products:
                    quantity = random.randint(1, 3)
                    CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=quantity,
                        price=product.current_price
                    )
                    self.stats['cart_items'] += 1
                
                self.stats['carts'] += 1
                print(f"  ✅ Created cart for {customer.username} with {num_items} items")
    
    def create_orders_and_transactions(self):
        """Create orders with transactions"""
        print("📦 Creating orders and transactions...")
        
        customers = User.objects.filter(is_seller=False)
        products = list(Product.objects.filter(is_active=True))
        
        # Create orders for past 3 months
        start_date = timezone.now() - timedelta(days=90)
        
        for customer in customers:
            # Each customer has 1-4 orders
            num_orders = random.randint(1, 4)
            
            for _ in range(num_orders):
                # Random order date in past 90 days
                days_ago = random.randint(1, 90)
                order_date = timezone.now() - timedelta(days=days_ago)
                
                # Get customer address
                customer_address = Address.objects.filter(
                    user=customer, 
                    is_default=True
                ).first()
                
                if not customer_address:
                    customer_address = Address.objects.filter(user=customer).first()
                
                # Create order
                subtotal = Decimal('0.00')
                order = Order.objects.create(
                    user=customer,
                    customer_name=customer.get_display_name(),
                    customer_email=customer.email,
                    customer_phone=customer.phone or "+509 1234-5678",
                    shipping_address=customer_address.address_line_1 if customer_address else "Port-au-Prince, Haïti",
                    shipping_city=customer_address.city if customer_address else "Port-au-Prince",
                    shipping_country="Haïti",
                    billing_address=customer_address.address_line_1 if customer_address else "Port-au-Prince, Haïti",
                    billing_city=customer_address.city if customer_address else "Port-au-Prince",
                    billing_country="Haïti",
                    subtotal=subtotal,  # Will be updated
                    shipping_cost=Decimal('50.00'),
                    tax_amount=Decimal('0.00'),
                    total_amount=subtotal,  # Will be updated
                    currency="HTG",
                    status=random.choice(['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'delivered', 'delivered']),
                    payment_status=random.choice(['paid', 'paid', 'paid', 'pending']),
                    payment_method='moncash',
                    shipping_method='standard',
                    created_at=order_date,
                    updated_at=order_date
                )
                
                # Add order items
                num_items = random.randint(1, 4)
                order_products = random.sample(products, min(num_items, len(products)))
                
                for product in order_products:
                    quantity = random.randint(1, 2)
                    unit_price = product.current_price
                    total_price = unit_price * quantity
                    subtotal += total_price
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price,
                        product_name=product.name,
                        product_sku=product.sku,
                        product_image=product.primary_image.image_url if product.primary_image else "",
                        created_at=order_date
                    )
                    self.stats['order_items'] += 1
                
                # Update order totals
                order.subtotal = subtotal
                order.total_amount = subtotal + order.shipping_cost + order.tax_amount
                order.save()
                
                # Create transaction
                transaction = Transaction.objects.create(
                    order=order,
                    amount=order.total_amount,
                    currency="HTG",
                    status='completed' if order.payment_status == 'paid' else 'pending',
                    payment_method='moncash',
                    moncash_order_id=f"MC{random.randint(100000, 999999)}",
                    reference_number=f"REF{random.randint(1000, 9999)}",
                    transaction_date=order_date,
                    verified_at=order_date if order.payment_status == 'paid' else None,
                    gateway_response={"status": "success", "message": "Payment completed"} if order.payment_status == 'paid' else None
                )
                
                # Create order status history
                OrderStatusHistory.objects.create(
                    order=order,
                    old_status=None,
                    new_status=order.status,
                    comment=f"Order {order.status}",
                    created_at=order_date
                )
                
                self.stats['orders'] += 1
                self.stats['transactions'] += 1
                
                print(f"  ✅ Created order {order.order_number} for {customer.username} - {order.total_amount} HTG")
    
    def create_wishlists(self):
        """Create wishlists with items"""
        print("❤️ Creating wishlists...")
        
        customers = User.objects.filter(is_seller=False)
        products = list(Product.objects.filter(is_active=True))
        
        for customer in customers:
            # 60% chance customer has wishlist
            if random.random() < 0.6:
                wishlist = Wishlist.objects.create(
                    user=customer,
                    name=f"Ma Liste de Souhaits",
                    description="Produits que j'aimerais acheter",
                    is_public=random.choice([True, False])
                )
                
                # Add 2-8 items to wishlist
                num_items = random.randint(2, 8)
                wishlist_products = random.sample(products, min(num_items, len(products)))
                
                for product in wishlist_products:
                    WishlistItem.objects.create(
                        wishlist=wishlist,
                        product=product,
                        notes=random.choice([
                            "Pour mon anniversaire",
                            "Quand il y aura une promotion",
                            "Produit intéressant",
                            ""
                        ]),
                        priority=random.choice([1, 2, 2, 3, 3, 4]),
                        target_price=product.current_price * Decimal('0.9') if random.choice([True, False]) else None
                    )
                    self.stats['wishlist_items'] += 1
                
                self.stats['wishlists'] += 1
                print(f"  ✅ Created wishlist for {customer.username} with {num_items} items")
    
    def create_product_alerts(self):
        """Create product price alerts"""
        print("🔔 Creating product alerts...")
        
        customers = User.objects.filter(is_seller=False)
        products = list(Product.objects.filter(is_active=True))
        
        for customer in customers:
            # 40% chance customer has alerts
            if random.random() < 0.4:
                num_alerts = random.randint(1, 3)
                alert_products = random.sample(products, min(num_alerts, len(products)))
                
                for product in alert_products:
                    alert_type = random.choice(['price_drop', 'back_in_stock', 'price_target'])
                    
                    ProductAlert.objects.create(
                        user=customer,
                        product=product,
                        alert_type=alert_type,
                        target_price=product.current_price * Decimal('0.8') if alert_type in ['price_drop', 'price_target'] else None,
                        notify_email=True,
                        notify_sms=random.choice([True, False])
                    )
                    self.stats['alerts'] += 1
        
        print(f"  ✅ Created {self.stats['alerts']} product alerts")
    
    def create_newsletter_subscribers(self):
        """Create newsletter subscribers"""
        print("📧 Creating newsletter subscribers...")
        
        # Add existing users to newsletter
        all_users = User.objects.all()
        for user in all_users:
            if random.random() < 0.7:  # 70% subscribe
                NewsletterSubscriber.objects.get_or_create(
                    email=user.email,
                    defaults={
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_active': True,
                        'source': 'registration'
                    }
                )
                self.stats['newsletter'] += 1
        
        # Add some external subscribers
        external_emails = [
            "subscriber1@gmail.com",
            "newsletter.fan@yahoo.com",
            "shopper@hotmail.com",
            "deals.lover@outlook.com"
        ]
        
        for email in external_emails:
            NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={
                    'is_active': True,
                    'source': 'website'
                }
            )
            self.stats['newsletter'] += 1
        
        print(f"  ✅ Created {self.stats['newsletter']} newsletter subscribers")
    
    def create_promotions(self):
        """Create promotional campaigns"""
        print("🎁 Creating promotions...")
        
        promotions_data = [
            {
                "name": "Promotion Rentrée Scolaire",
                "description": "15% de réduction sur tous les produits éducatifs",
                "discount_type": "percentage",
                "discount_value": 15,
                "code": "RENTREE2025",
                "start_date": timezone.now(),
                "end_date": timezone.now() + timedelta(days=30)
            },
            {
                "name": "Fête des Mères",
                "description": "Offre spéciale pour la fête des mères",
                "discount_type": "percentage",
                "discount_value": 20,
                "code": "MAMAN2025",
                "start_date": timezone.now() + timedelta(days=10),
                "end_date": timezone.now() + timedelta(days=40)
            },
            {
                "name": "Première Commande",
                "description": "50 HTG de réduction pour votre première commande",
                "discount_type": "fixed",
                "discount_value": 50,
                "code": "BIENVENUE50",
                "start_date": timezone.now() - timedelta(days=30),
                "end_date": timezone.now() + timedelta(days=90)
            }
        ]
        
        for promo_data in promotions_data:
            Promotion.objects.create(
                name=promo_data["name"],
                description=promo_data["description"],
                discount_type=promo_data["discount_type"],
                discount_value=Decimal(str(promo_data["discount_value"])),
                code=promo_data["code"],
                start_date=promo_data["start_date"],
                end_date=promo_data["end_date"],
                is_active=True,
                max_uses=100,
                used_count=random.randint(5, 25)
            )
            self.stats['promotions'] += 1
            print(f"  ✅ Created promotion: {promo_data['name']}")
    
    def create_site_settings(self):
        """Create site configuration settings"""
        print("⚙️ Creating site settings...")
        
        settings_data = [
            {
                "key": "site_name",
                "value": "Afèpanou",
                "description": "Nom du site marketplace"
            },
            {
                "key": "site_tagline",
                "value": "Le marketplace haïtien de référence",
                "description": "Slogan du site"
            },
            {
                "key": "contact_email",
                "value": "contact@afepanou.com",
                "description": "Email de contact principal"
            },
            {
                "key": "support_phone",
                "value": "+509 1234-5678",
                "description": "Numéro de support client"
            },
            {
                "key": "default_shipping_cost",
                "value": "50.00",
                "description": "Coût de livraison par défaut en HTG"
            },
            {
                "key": "min_order_amount",
                "value": "100.00",
                "description": "Montant minimum de commande en HTG"
            },
            {
                "key": "featured_products_limit",
                "value": "12",
                "description": "Nombre de produits vedettes à afficher"
            },
            {
                "key": "maintenance_mode",
                "value": "false",
                "description": "Mode maintenance du site"
            }
        ]
        
        for setting_data in settings_data:
            SiteSetting.objects.get_or_create(
                key=setting_data["key"],
                defaults={
                    "value": setting_data["value"],
                    "description": setting_data["description"]
                }
            )
            self.stats['settings'] += 1
        
        print(f"  ✅ Created {self.stats['settings']} site settings")
    
    def create_media_content_sections(self):
        """Create media content sections for homepage"""
        print("📱 Creating media content sections...")
        
        sections_data = [
            {
                "title": "Produits Locaux Authentiques",
                "subtitle": "Découvrez l'artisanat haïtien",
                "description": "Une sélection unique de produits fabriqués par nos artisans locaux avec savoir-faire traditionnel et matériaux de qualité.",
                "button_text": "Voir la collection",
                "button_link": "/categories/locaux/",
                "layout_type": "left",
                "category_tags": "locaux,artisanat,traditionnel"
            },
            {
                "title": "Services Professionnels",
                "subtitle": "Expertise à votre portée",
                "description": "Trouvez des professionnels qualifiés pour tous vos besoins : comptabilité, formation, réparation et bien plus encore.",
                "button_text": "Découvrir les services",
                "button_link": "/categories/services/",
                "layout_type": "right",
                "category_tags": "services,professionnel,formation"
            },
            {
                "title": "Électronique et High-Tech",
                "subtitle": "Technologie de pointe",
                "description": "Les derniers smartphones, accessoires et appareils électroniques avec garantie et service après-vente.",
                "button_text": "Voir les produits",
                "button_link": "/categories/electroniques/",
                "layout_type": "center",
                "category_tags": "electroniques,smartphone,technologie"
            }
        ]
        
        for section_data in sections_data:
            MediaContentSection.objects.create(
                title=section_data["title"],
                subtitle=section_data["subtitle"],
                description=section_data["description"],
                button_text=section_data["button_text"],
                button_link=section_data["button_link"],
                layout_type=section_data["layout_type"],
                category_tags=section_data["category_tags"],
                is_active=True,
                sort_order=self.stats['media_sections']
            )
            self.stats['media_sections'] += 1
            print(f"  ✅ Created media section: {section_data['title']}")
    
    def print_summary(self):
        """Print comprehensive summary"""
        print(f"\n✅ Complete E2E data population finished!")
        print(f"📊 Comprehensive Summary:")
        
        # Existing data
        print(f"\n🏪 EXISTING DATA:")
        print(f"   - Categories: {Category.objects.count()}")
        print(f"   - Products: {Product.objects.count()}")
        print(f"   - Vendors: {User.objects.filter(is_seller=True).count()}")
        print(f"   - Product Images: {ProductImage.objects.count()}")
        print(f"   - Banners: {Banner.objects.count()}")
        print(f"   - Reviews: {Review.objects.count()}")
        
        # New data created
        print(f"\n🆕 NEW DATA CREATED:")
        for key, value in self.stats.items():
            if value > 0:
                print(f"   - {key.title().replace('_', ' ')}: {value}")
        
        # Total statistics
        print(f"\n📈 TOTAL DATABASE:")
        print(f"   - Total Users: {User.objects.count()}")
        print(f"   - Total Customers: {User.objects.filter(is_seller=False).count()}")
        print(f"   - Total Orders: {Order.objects.count()}")
        print(f"   - Total Transactions: {Transaction.objects.count()}")
        print(f"   - Active Carts: {Cart.objects.filter(is_active=True).count()}")
        print(f"   - Wishlist Items: {WishlistItem.objects.count()}")
        print(f"   - Product Alerts: {ProductAlert.objects.count()}")
        
        print(f"\n🎉 Full E2E simulation ready!")
        print(f"📝 Test the complete workflow:")
        print(f"   1. Customer registration/login")
        print(f"   2. Browse products and categories") 
        print(f"   3. Add to cart and wishlist")
        print(f"   4. Checkout and payment")
        print(f"   5. Order tracking")
        print(f"   6. Vendor management")

if __name__ == "__main__":
    print("🚀 Starting comprehensive E2E data population for Afèpanou...")
    
    response = input("\n⚠️  This will add comprehensive test data to all tables. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    try:
        populator = FullDataPopulator()
        populator.populate_all()
    except Exception as e:
        print(f"\n❌ Error during population: {e}")
        raise