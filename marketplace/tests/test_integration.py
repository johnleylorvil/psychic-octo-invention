# Integration tests for Afèpanou marketplace
import pytest
import json
from decimal import Decimal
from unittest.mock import patch, Mock
from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import transaction

from marketplace.models import (
    Category, Product, Cart, CartItem, Order, OrderItem, 
    Transaction, Review, VendorProfile
)
from marketplace.services.payment_service import PaymentService
from marketplace.services.order_service import OrderService
from marketplace.services.email_service import EmailService
from .factories import (
    UserFactory, SellerUserFactory, VendorProfileFactory, CategoryFactory,
    ProductFactory, CartFactory, CartItemFactory, OrderFactory
)

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.integration
class TestUserRegistrationWorkflow:
    """Integration test for complete user registration workflow"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
    
    def test_complete_user_registration_flow(self):
        """Test complete user registration from form to login"""
        # Step 1: Access registration page
        response = self.client.get(reverse('register'))
        assert response.status_code == 200
        
        # Step 2: Submit registration form
        registration_data = {
            'email': 'newuser@test.com',
            'first_name': 'Jean',
            'last_name': 'Pierre',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'phone': '+509 1234-5678',
            'terms_accepted': True
        }
        
        response = self.client.post(reverse('register'), registration_data)
        assert response.status_code == 302  # Redirect after successful registration
        
        # Step 3: Verify user was created
        user = User.objects.get(email='newuser@test.com')
        assert user.first_name == 'Jean'
        assert user.is_active
        assert not user.is_seller
        
        # Step 4: Test login with new credentials
        login_data = {
            'username': 'newuser@test.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(reverse('login'), login_data)
        assert response.status_code == 302
        
        # Step 5: Verify user is logged in
        assert '_auth_user_id' in self.client.session
        
        # Step 6: Access protected page
        response = self.client.get(reverse('profile'))
        assert response.status_code == 200
        assert response.context['user'] == user
    
    @patch('marketplace.services.email_service.EmailService.send_welcome_email')
    def test_registration_sends_welcome_email(self, mock_send_email):
        """Test that registration sends welcome email"""
        registration_data = {
            'email': 'newuser@test.com',
            'first_name': 'Jean',
            'last_name': 'Pierre',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'phone': '+509 1234-5678',
            'terms_accepted': True
        }
        
        self.client.post(reverse('register'), registration_data)
        
        # Verify email was sent
        mock_send_email.assert_called_once()
        user = User.objects.get(email='newuser@test.com')
        mock_send_email.assert_called_with(user)


@pytest.mark.django_db
@pytest.mark.integration
class TestSellerOnboardingWorkflow:
    """Integration test for seller onboarding workflow"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
        self.user = UserFactory(is_seller=False)
    
    def test_complete_seller_onboarding_flow(self):
        """Test complete seller onboarding from application to approval"""
        self.client.force_login(self.user)
        
        # Step 1: Access become seller page
        response = self.client.get(reverse('become_seller'))
        assert response.status_code == 200
        
        # Step 2: Submit seller application
        application_data = {
            'business_name': 'Mon Entreprise Haiti',
            'business_description': 'Description détaillée de mon entreprise innovante qui aide les communautés locales.',
            'business_address': '123 Rue de la Paix, Port-au-Prince, Haïti',
            'business_phone': '+509 1234-5678',
            'business_email': 'contact@monentreprise.ht',
            'business_type': 'retail',
            'tax_id': 'HTI123456789'
        }
        
        response = self.client.post(reverse('become_seller'), application_data)
        assert response.status_code == 302  # Redirect after submission
        
        # Step 3: Verify user is now a seller
        self.user.refresh_from_db()
        assert self.user.is_seller
        
        # Step 4: Verify vendor profile was created
        vendor_profile = VendorProfile.objects.get(user=self.user)
        assert vendor_profile.business_name == 'Mon Entreprise Haiti'
        assert vendor_profile.business_email == 'contact@monentreprise.ht'
        
        # Step 5: Access seller dashboard
        response = self.client.get(reverse('seller_dashboard'))
        assert response.status_code == 200
        assert 'seller/dashboard.html' in [t.name for t in response.templates]
    
    def test_seller_product_creation_workflow(self):
        """Test seller creating their first product"""
        # Set up seller
        seller = SellerUserFactory()
        vendor = VendorProfileFactory(user=seller)
        category = CategoryFactory()
        
        self.client.force_login(seller)
        
        # Step 1: Access product creation page
        response = self.client.get(reverse('seller_add_product'))
        assert response.status_code == 200
        
        # Step 2: Submit product creation form
        product_data = {
            'name': 'Artisanat Haïtien Authentique',
            'description': 'Magnifique pièce d\'artisanat traditionnelle faite à la main par des artisans locaux.',
            'category': category.id,
            'price': '75.00',
            'stock_quantity': '20',
            'brand': 'Artisans Haiti',
            'weight': '0.5'
        }
        
        response = self.client.post(reverse('seller_add_product'), product_data)
        assert response.status_code == 302
        
        # Step 3: Verify product was created
        product = Product.objects.get(name='Artisanat Haïtien Authentique')
        assert product.seller == seller
        assert product.category == category
        assert product.price == Decimal('75.00')
        assert product.is_active
        
        # Step 4: Verify product appears in seller dashboard
        response = self.client.get(reverse('seller_dashboard'))
        assert response.status_code == 200
        assert product in response.context['products']


@pytest.mark.django_db
@pytest.mark.integration
class TestShoppingCartWorkflow:
    """Integration test for shopping cart workflow"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
        self.user = UserFactory()
        self.category = CategoryFactory()
        self.products = ProductFactory.create_batch(3, category=self.category, stock_quantity=10)
    
    def test_anonymous_user_cart_workflow(self):
        """Test shopping cart workflow for anonymous user"""
        # Step 1: Add product to cart as anonymous user
        response = self.client.post(reverse('add_to_cart'), {
            'product_id': self.products[0].id,
            'quantity': 2
        })
        assert response.status_code == 302
        
        # Step 2: Verify session cart was created
        session_id = self.client.session.session_key
        cart = Cart.objects.get(session_id=session_id, user__isnull=True)
        assert cart.total_items == 2
        
        # Step 3: Add another product
        self.client.post(reverse('add_to_cart'), {
            'product_id': self.products[1].id,
            'quantity': 1
        })
        
        cart.refresh_from_db()
        assert cart.total_items == 3
        
        # Step 4: View cart
        response = self.client.get(reverse('cart'))
        assert response.status_code == 200
        assert len(response.context['cart_items']) == 2
        
        # Step 5: Update cart item quantity
        cart_item = cart.items.first()
        response = self.client.post(reverse('update_cart'), {
            'cart_item_id': cart_item.id,
            'quantity': 3
        })
        assert response.status_code == 302
        
        cart_item.refresh_from_db()
        assert cart_item.quantity == 3
        
        # Step 6: Remove item from cart
        response = self.client.post(reverse('remove_from_cart'), {
            'cart_item_id': cart_item.id
        })
        assert response.status_code == 302
        
        assert not CartItem.objects.filter(id=cart_item.id).exists()
    
    def test_authenticated_user_cart_workflow(self):
        """Test shopping cart workflow for authenticated user"""
        self.client.force_login(self.user)
        
        # Step 1: Add products to cart
        for i, product in enumerate(self.products):
            self.client.post(reverse('add_to_cart'), {
                'product_id': product.id,
                'quantity': i + 1
            })
        
        # Step 2: Verify cart was created for user
        cart = Cart.objects.get(user=self.user)
        assert cart.total_items == 6  # 1 + 2 + 3
        
        # Step 3: Test cart persistence across sessions
        self.client.logout()
        self.client.force_login(self.user)
        
        response = self.client.get(reverse('cart'))
        assert response.status_code == 200
        assert response.context['cart'] == cart
    
    def test_cart_merge_on_login(self):
        """Test cart merging when anonymous user logs in"""
        # Step 1: Add items to cart as anonymous user
        self.client.post(reverse('add_to_cart'), {
            'product_id': self.products[0].id,
            'quantity': 2
        })
        
        # Step 2: Create user with existing cart
        self.client.force_login(self.user)
        existing_cart = CartFactory(user=self.user)
        CartItemFactory(cart=existing_cart, product=self.products[1], quantity=1)
        
        # Step 3: Login should merge carts
        response = self.client.post(reverse('login'), {
            'username': self.user.email,
            'password': 'testpass123'
        })
        
        # Step 4: Verify carts were merged
        user_cart = Cart.objects.get(user=self.user, is_active=True)
        assert user_cart.total_items == 3  # 2 from anonymous + 1 from existing


@pytest.mark.django_db
@pytest.mark.integration
class TestCheckoutWorkflow:
    """Integration test for complete checkout workflow"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
        self.user = UserFactory()
        self.products = ProductFactory.create_batch(2, stock_quantity=10, price=Decimal('50.00'))
        
        # Create cart with items
        self.cart = CartFactory(user=self.user)
        self.cart_items = [
            CartItemFactory(cart=self.cart, product=self.products[0], quantity=2),
            CartItemFactory(cart=self.cart, product=self.products[1], quantity=1)
        ]
    
    @patch('marketplace.services.payment_service.PaymentService.create_payment')
    @patch('marketplace.services.email_service.EmailService.send_order_confirmation')
    def test_complete_checkout_workflow(self, mock_send_email, mock_create_payment):
        """Test complete checkout workflow from cart to order confirmation"""
        # Mock payment service
        mock_create_payment.return_value = {
            'success': True,
            'payment_url': 'https://payment.example.com/pay/123',
            'transaction_id': 'TXN123456'
        }
        
        self.client.force_login(self.user)
        
        # Step 1: Access checkout page
        response = self.client.get(reverse('checkout'))
        assert response.status_code == 200
        assert response.context['cart'] == self.cart
        
        # Step 2: Submit checkout form
        checkout_data = {
            'shipping_first_name': 'Jean',
            'shipping_last_name': 'Pierre',
            'shipping_address': '123 Rue de la République',
            'shipping_city': 'Port-au-Prince',
            'shipping_country': 'Haïti',
            'phone': '+509 1234-5678',
            'payment_method': 'moncash',
            'moncash_phone': '+509 1234-5678'
        }
        
        response = self.client.post(reverse('checkout'), checkout_data)
        assert response.status_code == 302  # Redirect to payment
        
        # Step 3: Verify order was created
        order = Order.objects.get(user=self.user)
        assert order.customer_name == 'Jean Pierre'
        assert order.shipping_address == '123 Rue de la République'
        assert order.total_amount == Decimal('125.00')  # (50*2) + (50*1) + shipping
        assert order.status == 'pending'
        assert order.payment_status == 'pending'
        
        # Step 4: Verify order items were created
        order_items = order.items.all()
        assert len(order_items) == 2
        
        for item in order_items:
            assert item.product in self.products
            assert item.product_name  # Snapshot saved
            assert item.total_price == item.quantity * item.unit_price
        
        # Step 5: Verify cart was cleared
        self.cart.refresh_from_db()
        assert not self.cart.is_active
        
        # Step 6: Verify transaction was created
        transaction = Transaction.objects.get(order=order)
        assert transaction.amount == order.total_amount
        assert transaction.payment_method == 'moncash'
        assert transaction.status == 'pending'
        
        # Step 7: Verify email was sent
        mock_send_email.assert_called_once_with(order)
        
        # Step 8: Verify payment service was called
        mock_create_payment.assert_called_once_with(order)
    
    def test_checkout_insufficient_stock(self):
        """Test checkout behavior when product stock is insufficient"""
        # Reduce stock below cart quantity
        self.products[0].stock_quantity = 1  # Less than cart quantity of 2
        self.products[0].save()
        
        self.client.force_login(self.user)
        
        checkout_data = {
            'shipping_first_name': 'Jean',
            'shipping_last_name': 'Pierre',
            'shipping_address': '123 Rue Example',
            'shipping_city': 'Port-au-Prince',
            'shipping_country': 'Haïti',
            'phone': '+509 1234-5678',
            'payment_method': 'moncash'
        }
        
        response = self.client.post(reverse('checkout'), checkout_data)
        
        # Should redirect back to cart with error
        assert response.status_code == 302
        assert reverse('cart') in response.url
        
        # Verify no order was created
        assert not Order.objects.filter(user=self.user).exists()


@pytest.mark.django_db
@pytest.mark.integration
class TestOrderFulfillmentWorkflow:
    """Integration test for order fulfillment workflow"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
        self.seller = SellerUserFactory()
        self.vendor = VendorProfileFactory(user=self.seller)
        self.customer = UserFactory()
        
        # Create products and order
        self.product = ProductFactory(seller=self.seller, stock_quantity=10)
        self.order = OrderFactory(user=self.customer, status='confirmed', payment_status='paid')
        self.order_item = OrderFactory(order=self.order, product=self.product, quantity=2)
    
    @patch('marketplace.services.email_service.EmailService.send_shipping_notification')
    def test_seller_order_fulfillment_workflow(self, mock_send_email):
        """Test seller fulfilling an order"""
        self.client.force_login(self.seller)
        
        # Step 1: View order in seller dashboard
        response = self.client.get(reverse('seller_orders'))
        assert response.status_code == 200
        assert self.order in response.context['orders']
        
        # Step 2: View order details
        response = self.client.get(reverse('seller_order_detail', kwargs={'order_id': self.order.id}))
        assert response.status_code == 200
        assert response.context['order'] == self.order
        
        # Step 3: Update order status to 'processing'
        response = self.client.post(reverse('seller_update_order'), {
            'order_id': self.order.id,
            'status': 'processing',
            'notes': 'Commande en cours de préparation'
        })
        assert response.status_code == 302
        
        self.order.refresh_from_db()
        assert self.order.status == 'processing'
        
        # Step 4: Add tracking information and mark as shipped
        response = self.client.post(reverse('seller_update_order'), {
            'order_id': self.order.id,
            'status': 'shipped',
            'tracking_number': 'TRACK123456',
            'notes': 'Expédié via service de livraison local'
        })
        assert response.status_code == 302
        
        self.order.refresh_from_db()
        assert self.order.status == 'shipped'
        assert self.order.tracking_number == 'TRACK123456'
        
        # Step 5: Verify email notification was sent
        mock_send_email.assert_called_once_with(self.order)
        
        # Step 6: Verify stock was reduced
        self.product.refresh_from_db()
        assert self.product.stock_quantity == 8  # 10 - 2
    
    def test_customer_order_tracking(self):
        """Test customer tracking their order"""
        self.client.force_login(self.customer)
        
        # Step 1: View order history
        response = self.client.get(reverse('order_history'))
        assert response.status_code == 200
        assert self.order in response.context['orders']
        
        # Step 2: View specific order details
        response = self.client.get(reverse('order_detail', kwargs={'order_id': self.order.id}))
        assert response.status_code == 200
        assert response.context['order'] == self.order
        
        # Step 3: Update order to shipped with tracking
        self.order.status = 'shipped'
        self.order.tracking_number = 'TRACK123456'
        self.order.save()
        
        # Step 4: Verify tracking information is displayed
        response = self.client.get(reverse('order_detail', kwargs={'order_id': self.order.id}))
        assert 'TRACK123456' in response.content.decode()


@pytest.mark.django_db
@pytest.mark.integration
class TestProductReviewWorkflow:
    """Integration test for product review workflow"""
    
    def setup_method(self):
        """Set up test data"""
        self.client = Client()
        self.customer = UserFactory()
        self.product = ProductFactory()
        
        # Create completed order to allow reviews
        self.order = OrderFactory(user=self.customer, status='delivered', payment_status='paid')
        self.order_item = OrderFactory(order=self.order, product=self.product)
    
    def test_customer_product_review_workflow(self):
        """Test customer leaving a product review"""
        self.client.force_login(self.customer)
        
        # Step 1: Access product page
        response = self.client.get(reverse('product_detail', kwargs={'slug': self.product.slug}))
        assert response.status_code == 200
        
        # Step 2: Submit review form
        review_data = {
            'rating': 5,
            'title': 'Excellent produit!',
            'comment': 'Très satisfait de cet achat. Qualité exceptionnelle et livraison rapide.'
        }
        
        response = self.client.post(
            reverse('add_review', kwargs={'product_id': self.product.id}),
            review_data
        )
        assert response.status_code == 302
        
        # Step 3: Verify review was created
        review = Review.objects.get(user=self.customer, product=self.product)
        assert review.rating == 5
        assert review.title == 'Excellent produit!'
        assert review.is_verified_purchase  # Should be True due to completed order
        
        # Step 4: Verify review appears on product page
        response = self.client.get(reverse('product_detail', kwargs={'slug': self.product.slug}))
        assert review.title in response.content.decode()
        
        # Step 5: Verify product rating was updated
        self.product.refresh_from_db()
        assert self.product.average_rating == 5.0
        assert self.product.review_count == 1
    
    def test_review_moderation_workflow(self):
        """Test admin review moderation"""
        # Create review that needs moderation
        review_data = {
            'rating': 1,
            'title': 'Produit décevant',
            'comment': 'Contenu inapproprié qui doit être modéré.'
        }
        
        self.client.force_login(self.customer)
        self.client.post(
            reverse('add_review', kwargs={'product_id': self.product.id}),
            review_data
        )
        
        review = Review.objects.get(user=self.customer, product=self.product)
        
        # Step 1: Admin marks review as unapproved
        admin_user = UserFactory(is_staff=True, is_superuser=True)
        self.client.force_login(admin_user)
        
        # Step 2: Access admin panel to moderate review
        from django.contrib.admin.sites import site
        from marketplace.models import Review
        
        # Mark review as unapproved
        review.is_approved = False
        review.save()
        
        # Step 3: Verify review no longer appears on product page
        self.client.logout()
        response = self.client.get(reverse('product_detail', kwargs={'slug': self.product.slug}))
        assert review.title not in response.content.decode()
        
        # Step 4: Verify product rating excludes unapproved review
        assert self.product.average_rating == 0  # No approved reviews