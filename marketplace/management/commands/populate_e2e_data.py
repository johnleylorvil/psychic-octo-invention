"""
Django management command to populate comprehensive E2E test data
Usage: python manage.py populate_e2e_data
"""

import random
from decimal import Decimal
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from marketplace.models import (
    User, Category, Product, ProductImage, Banner, VendorProfile, Review, Page,
    Cart, CartItem, Order, OrderItem, OrderStatusHistory, Transaction,
    Wishlist, WishlistItem, WishlistCollection, WishlistCollectionItem, ProductAlert,
    Address, SavedLocation, NewsletterSubscriber, SiteSetting, Promotion,
    MediaContentSection
)

class Command(BaseCommand):
    help = 'Populate comprehensive E2E test data for full simulation'
    
    def __init__(self):
        super().__init__()
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
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip if data already exists',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting comprehensive E2E data population...\n')
        )
        
        with transaction.atomic():
            self.create_customers()
            self.create_addresses()
            self.create_carts_and_items()
            self.create_orders_and_transactions()
            self.create_wishlists()
            self.create_product_alerts()
            self.create_newsletter_subscribers()
            self.create_promotions()
            self.create_site_settings()
            self.create_media_content_sections()
        
        self.print_summary()
    
    def create_customers(self):
        """Create regular customer accounts"""
        self.stdout.write('Creating customer accounts...')
        
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
                "city": "Cap-Haitien"
            },
            {
                "username": "claire_shopper",
                "email": "claire.shop@hotmail.com",
                "first_name": "Claire",
                "last_name": "Moise",
                "phone": "+509 5678-9012",
                "city": "Les Cayes"
            },
            {
                "username": "jean_customer",
                "email": "jean.customer@aol.com",
                "first_name": "Jean",
                "last_name": "Baptiste",
                "phone": "+509 6789-0123",
                "city": "Gonaives"
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
                    "country": "Haiti",
                    "is_seller": False,
                    "email_verified": True,
                    "phone_verified": random.choice([True, False])
                }
            )
            
            if created:
                user.set_password("customer123")
                user.save()
                self.stats['customers'] += 1
                self.stdout.write(f'  Created customer: {user.get_display_name()}')
    
    def create_addresses(self):
        """Create addresses for customers"""
        self.stdout.write('Creating customer addresses...')
        
        customers = User.objects.filter(is_seller=False)
        
        address_templates = [
            {"address": "15 Rue Capois", "city": "Port-au-Prince", "type": "home"},
            {"address": "23 Avenue John Brown", "city": "Port-au-Prince", "type": "work"},
            {"address": "8 Rue Geffrard", "city": "Cap-Haitien", "type": "home"},
            {"address": "45 Boulevard Jean-Jacques Dessalines", "city": "Les Cayes", "type": "home"},
            {"address": "12 Rue Stenio Vincent", "city": "Gonaives", "type": "home"},
            {"address": "67 Avenue Lamartiniere", "city": "Port-au-Prince", "type": "work"},
        ]
        
        for customer in customers:
            # Create 1-2 addresses per customer
            num_addresses = random.randint(1, 2)
            for i in range(num_addresses):
                template = random.choice(address_templates)
                
                Address.objects.create(
                    user=customer,
                    first_name=customer.first_name,
                    last_name=customer.last_name,
                    phone=customer.phone or "+509 1234-5678",
                    address_line1=template["address"],
                    city=template["city"],
                    country="HT",
                    address_type=template["type"],
                    is_default=(i == 0)  # First address is default
                )
                self.stats['addresses'] += 1
        
        self.stdout.write(f'  Created {self.stats["addresses"]} addresses')
    
    def create_carts_and_items(self):
        """Create shopping carts with items"""
        self.stdout.write('Creating shopping carts...')
        
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
                self.stdout.write(f'  Created cart for {customer.username} with {num_items} items')
    
    def create_orders_and_transactions(self):
        """Create orders with transactions"""
        self.stdout.write('Creating orders and transactions...')
        
        customers = User.objects.filter(is_seller=False)
        products = list(Product.objects.filter(is_active=True))
        
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
                    shipping_address=customer_address.address_line1 if customer_address else "Port-au-Prince, Haiti",
                    shipping_city=customer_address.city if customer_address else "Port-au-Prince",
                    shipping_country="Haiti",
                    billing_address=customer_address.address_line1 if customer_address else "Port-au-Prince, Haiti",
                    billing_city=customer_address.city if customer_address else "Port-au-Prince",
                    billing_country="Haiti",
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
                Transaction.objects.create(
                    order=order,
                    amount=order.total_amount,
                    currency="HTG",
                    status='completed' if order.payment_status == 'paid' else 'pending',
                    payment_method='moncash',
                    moncash_order_id=f"MC{random.randint(100000, 999999)}",
                    reference_number=f"REF{random.randint(1000, 9999)}",
                    transaction_date=order_date,
                    verified_at=order_date if order.payment_status == 'paid' else None,
                    gateway_response={"status": "success"} if order.payment_status == 'paid' else None
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
        
        self.stdout.write(f'  Created {self.stats["orders"]} orders with transactions')
    
    def create_wishlists(self):
        """Create wishlists with items"""
        self.stdout.write('Creating wishlists...')
        
        customers = User.objects.filter(is_seller=False)
        products = list(Product.objects.filter(is_active=True))
        
        for customer in customers:
            # 60% chance customer has wishlist
            if random.random() < 0.6:
                wishlist = Wishlist.objects.create(
                    user=customer,
                    name="Ma Liste de Souhaits",
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
                            "Produit interessant",
                            ""
                        ]),
                        priority=random.choice([1, 2, 2, 3, 3, 4]),
                        target_price=product.current_price * Decimal('0.9') if random.choice([True, False]) else None
                    )
                    self.stats['wishlist_items'] += 1
                
                self.stats['wishlists'] += 1
        
        self.stdout.write(f'  Created {self.stats["wishlists"]} wishlists with {self.stats["wishlist_items"]} items')
    
    def create_product_alerts(self):
        """Create product price alerts"""
        self.stdout.write('Creating product alerts...')
        
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
        
        self.stdout.write(f'  Created {self.stats["alerts"]} product alerts')
    
    def create_newsletter_subscribers(self):
        """Create newsletter subscribers"""
        self.stdout.write('Creating newsletter subscribers...')
        
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
        
        self.stdout.write(f'  Created {self.stats["newsletter"]} newsletter subscribers')
    
    def create_promotions(self):
        """Create promotional campaigns"""
        self.stdout.write('Creating promotions...')
        
        promotions_data = [
            {
                "name": "Promotion Rentree Scolaire",
                "description": "15% de reduction sur tous les produits educatifs",
                "discount_type": "percentage",
                "discount_value": 15,
                "code": "RENTREE2025"
            },
            {
                "name": "Fete des Meres",
                "description": "Offre speciale pour la fete des meres",
                "discount_type": "percentage", 
                "discount_value": 20,
                "code": "MAMAN2025"
            },
            {
                "name": "Premiere Commande",
                "description": "50 HTG de reduction pour votre premiere commande",
                "discount_type": "fixed_amount",
                "discount_value": 50,
                "code": "BIENVENUE50"
            }
        ]
        
        for promo_data in promotions_data:
            Promotion.objects.create(
                name=promo_data["name"],
                discount_type=promo_data["discount_type"],
                discount_value=Decimal(str(promo_data["discount_value"])),
                code=promo_data["code"],
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=30),
                is_active=True,
                maximum_uses=100,
                current_uses=random.randint(5, 25),
                minimum_amount=Decimal('100.00') if random.choice([True, False]) else None
            )
            self.stats['promotions'] += 1
            
        self.stdout.write(f'  Created {self.stats["promotions"]} promotions')
    
    def create_site_settings(self):
        """Create site configuration settings"""
        self.stdout.write('Creating site settings...')
        
        settings_data = [
            ("site_name", "Afepanou", "Nom du site marketplace"),
            ("site_tagline", "Le marketplace haitien de reference", "Slogan du site"),
            ("contact_email", "contact@afepanou.com", "Email de contact principal"),
            ("support_phone", "+509 1234-5678", "Numero de support client"),
            ("default_shipping_cost", "50.00", "Cout de livraison par defaut en HTG"),
            ("min_order_amount", "100.00", "Montant minimum de commande en HTG"),
            ("featured_products_limit", "12", "Nombre de produits vedettes a afficher"),
            ("maintenance_mode", "false", "Mode maintenance du site")
        ]
        
        for key, value, description in settings_data:
            SiteSetting.objects.get_or_create(
                setting_key=key,
                defaults={
                    "setting_value": value,
                    "description": description,
                    "setting_type": "text",
                    "group_name": "general",
                    "is_public": True
                }
            )
            self.stats['settings'] += 1
        
        self.stdout.write(f'  Created {self.stats["settings"]} site settings')
    
    def create_media_content_sections(self):
        """Create media content sections for homepage"""
        self.stdout.write('Creating media content sections...')
        
        sections_data = [
            {
                "title": "Produits Locaux Authentiques",
                "subtitle": "Decouvrez l'artisanat haitien",
                "description": "Une selection unique de produits fabriques par nos artisans locaux.",
                "button_text": "Voir la collection",
                "button_link": "/categories/locaux/",
                "layout_type": "left"
            },
            {
                "title": "Services Professionnels",
                "subtitle": "Expertise a votre portee",
                "description": "Trouvez des professionnels qualifies pour tous vos besoins.",
                "button_text": "Decouvrir les services",
                "button_link": "/categories/services/",
                "layout_type": "right"
            },
            {
                "title": "Electronique et High-Tech",
                "subtitle": "Technologie de pointe",
                "description": "Les derniers smartphones et appareils electroniques.",
                "button_text": "Voir les produits",
                "button_link": "/categories/electroniques/",
                "layout_type": "center"
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
                is_active=True,
                sort_order=self.stats['media_sections']
            )
            self.stats['media_sections'] += 1
            
        self.stdout.write(f'  Created {self.stats["media_sections"]} media content sections')
    
    def print_summary(self):
        """Print comprehensive summary"""
        self.stdout.write(
            self.style.SUCCESS('\nComplete E2E data population finished!')
        )
        self.stdout.write('Comprehensive Summary:')
        
        # New data created
        self.stdout.write('\nNEW DATA CREATED:')
        for key, value in self.stats.items():
            if value > 0:
                self.stdout.write(f'   - {key.title().replace("_", " ")}: {value}')
        
        # Total statistics
        self.stdout.write('\nTOTAL DATABASE:')
        self.stdout.write(f'   - Total Users: {User.objects.count()}')
        self.stdout.write(f'   - Total Customers: {User.objects.filter(is_seller=False).count()}')
        self.stdout.write(f'   - Total Orders: {Order.objects.count()}')
        self.stdout.write(f'   - Total Transactions: {Transaction.objects.count()}')
        self.stdout.write(f'   - Active Carts: {Cart.objects.filter(is_active=True).count()}')
        self.stdout.write(f'   - Wishlist Items: {WishlistItem.objects.count()}')
        self.stdout.write(f'   - Product Alerts: {ProductAlert.objects.count()}')
        
        self.stdout.write(
            self.style.SUCCESS('\nFull E2E simulation ready!')
        )
        self.stdout.write('Test the complete workflow:')
        self.stdout.write('   1. Customer registration/login')
        self.stdout.write('   2. Browse products and categories')
        self.stdout.write('   3. Add to cart and wishlist') 
        self.stdout.write('   4. Checkout and payment')
        self.stdout.write('   5. Order tracking')
        self.stdout.write('   6. Vendor management')