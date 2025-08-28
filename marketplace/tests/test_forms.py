# Unit tests for Afèpanou marketplace forms
import pytest
from decimal import Decimal
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from marketplace.forms import (
    ProductSearchForm, UserRegistrationForm, SellerApplicationForm,
    ShippingAddressForm, PaymentMethodForm, ProductCreationForm,
    UserProfileForm, ContactForm, NewsletterSubscriptionForm
)
from .factories import UserFactory, CategoryFactory, ProductFactory


@pytest.mark.django_db
class TestUserRegistrationForm:
    """Test suite for UserRegistrationForm"""
    
    def test_valid_registration_data(self):
        """Test form with valid registration data"""
        form_data = {
            'email': 'newuser@test.com',
            'first_name': 'Jean',
            'last_name': 'Pierre',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'phone': '+509 1234-5678',
            'terms_accepted': True
        }
        
        form = UserRegistrationForm(data=form_data)
        assert form.is_valid()
        
        # Test user creation
        user = form.save()
        assert user.email == 'newuser@test.com'
        assert user.first_name == 'Jean'
        assert user.last_name == 'Pierre'
        assert user.check_password('TestPass123!')
    
    def test_invalid_email_format(self):
        """Test form with invalid email format"""
        form_data = {
            'email': 'invalid-email-format',
            'first_name': 'Jean',
            'last_name': 'Pierre',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'phone': '+509 1234-5678',
            'terms_accepted': True
        }
        
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors
    
    def test_duplicate_email(self):
        """Test form with already existing email"""
        existing_user = UserFactory(email='existing@test.com')
        
        form_data = {
            'email': 'existing@test.com',
            'first_name': 'Jean',
            'last_name': 'Pierre',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'phone': '+509 1234-5678',
            'terms_accepted': True
        }
        
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors
    
    def test_password_mismatch(self):
        """Test form with mismatched passwords"""
        form_data = {
            'email': 'newuser@test.com',
            'first_name': 'Jean',
            'last_name': 'Pierre',
            'password1': 'TestPass123!',
            'password2': 'DifferentPass123!',
            'phone': '+509 1234-5678',
            'terms_accepted': True
        }
        
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert 'password2' in form.errors
    
    def test_weak_password(self):
        """Test form with weak password"""
        form_data = {
            'email': 'newuser@test.com',
            'first_name': 'Jean',
            'last_name': 'Pierre',
            'password1': '123',
            'password2': '123',
            'phone': '+509 1234-5678',
            'terms_accepted': True
        }
        
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert 'password2' in form.errors
    
    def test_terms_not_accepted(self):
        """Test form without accepting terms"""
        form_data = {
            'email': 'newuser@test.com',
            'first_name': 'Jean',
            'last_name': 'Pierre',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'phone': '+509 1234-5678',
            'terms_accepted': False
        }
        
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert 'terms_accepted' in form.errors
    
    def test_haitian_phone_validation(self):
        """Test Haitian phone number validation"""
        valid_phones = [
            '+509 1234-5678',
            '+509 3456-7890',
            '509 1234 5678',
            '(509) 1234-5678'
        ]
        
        for phone in valid_phones:
            form_data = {
                'email': f'user{phone[-4:]}@test.com',
                'first_name': 'Jean',
                'last_name': 'Pierre',
                'password1': 'TestPass123!',
                'password2': 'TestPass123!',
                'phone': phone,
                'terms_accepted': True
            }
            
            form = UserRegistrationForm(data=form_data)
            assert form.is_valid(), f"Phone {phone} should be valid"
    
    def test_required_fields(self):
        """Test form with missing required fields"""
        form_data = {}
        
        form = UserRegistrationForm(data=form_data)
        assert not form.is_valid()
        
        required_fields = ['email', 'first_name', 'last_name', 'password1', 'password2']
        for field in required_fields:
            assert field in form.errors


@pytest.mark.django_db
class TestSellerApplicationForm:
    """Test suite for SellerApplicationForm"""
    
    def test_valid_seller_application(self):
        """Test form with valid seller application data"""
        form_data = {
            'business_name': 'Mon Entreprise Haiti',
            'business_description': 'Description de mon entreprise innovante.',
            'business_address': '123 Rue de la Paix, Port-au-Prince, Haïti',
            'business_phone': '+509 1234-5678',
            'business_email': 'contact@monentreprise.ht',
            'business_type': 'retail',
            'tax_id': 'HTI123456789',
            'bank_account_info': 'Compte bancaire: 1234567890'
        }
        
        form = SellerApplicationForm(data=form_data)
        assert form.is_valid()
    
    def test_business_name_validation(self):
        """Test business name validation"""
        form_data = {
            'business_name': 'X',  # Too short
            'business_description': 'Description valide.',
            'business_address': '123 Rue Example',
            'business_phone': '+509 1234-5678',
            'business_email': 'test@example.com',
            'business_type': 'retail'
        }
        
        form = SellerApplicationForm(data=form_data)
        assert not form.is_valid()
        assert 'business_name' in form.errors
    
    def test_business_email_validation(self):
        """Test business email validation"""
        form_data = {
            'business_name': 'Mon Entreprise',
            'business_description': 'Description valide.',
            'business_address': '123 Rue Example',
            'business_phone': '+509 1234-5678',
            'business_email': 'invalid-email',
            'business_type': 'retail'
        }
        
        form = SellerApplicationForm(data=form_data)
        assert not form.is_valid()
        assert 'business_email' in form.errors
    
    def test_description_length_validation(self):
        """Test business description length validation"""
        short_description = "Trop court."
        long_description = "x" * 2001  # Too long
        
        # Test too short
        form_data = {
            'business_name': 'Mon Entreprise',
            'business_description': short_description,
            'business_address': '123 Rue Example',
            'business_phone': '+509 1234-5678',
            'business_email': 'test@example.com',
            'business_type': 'retail'
        }
        
        form = SellerApplicationForm(data=form_data)
        assert not form.is_valid()
        assert 'business_description' in form.errors
        
        # Test too long
        form_data['business_description'] = long_description
        form = SellerApplicationForm(data=form_data)
        assert not form.is_valid()
        assert 'business_description' in form.errors


@pytest.mark.django_db
class TestProductSearchForm:
    """Test suite for ProductSearchForm"""
    
    def test_valid_search_form(self):
        """Test form with valid search parameters"""
        category = CategoryFactory()
        
        form_data = {
            'q': 'iPhone',
            'category': category.id,
            'min_price': '100.00',
            'max_price': '1000.00',
            'sort_by': 'price_asc'
        }
        
        form = ProductSearchForm(data=form_data)
        assert form.is_valid()
    
    def test_empty_search_form(self):
        """Test form with no search parameters (should be valid)"""
        form = ProductSearchForm(data={})
        assert form.is_valid()
    
    def test_invalid_price_range(self):
        """Test form with invalid price range"""
        form_data = {
            'min_price': '1000.00',
            'max_price': '100.00'  # Max less than min
        }
        
        form = ProductSearchForm(data=form_data)
        assert not form.is_valid()
        assert 'max_price' in form.errors
    
    def test_negative_prices(self):
        """Test form with negative prices"""
        form_data = {
            'min_price': '-50.00',
            'max_price': '-10.00'
        }
        
        form = ProductSearchForm(data=form_data)
        assert not form.is_valid()
        assert 'min_price' in form.errors
    
    def test_search_query_sanitization(self):
        """Test that search query is properly sanitized"""
        form_data = {
            'q': '<script>alert("xss")</script>iPhone'
        }
        
        form = ProductSearchForm(data=form_data)
        assert form.is_valid()
        # Query should be cleaned
        assert '<script>' not in form.cleaned_data['q']


@pytest.mark.django_db
class TestShippingAddressForm:
    """Test suite for ShippingAddressForm"""
    
    def test_valid_shipping_address(self):
        """Test form with valid shipping address"""
        form_data = {
            'first_name': 'Jean',
            'last_name': 'Pierre',
            'address_line1': '123 Rue de la République',
            'address_line2': 'Appartement 4B',
            'city': 'Port-au-Prince',
            'state': 'Ouest',
            'postal_code': 'HT1234',
            'country': 'Haïti',
            'phone': '+509 1234-5678'
        }
        
        form = ShippingAddressForm(data=form_data)
        assert form.is_valid()
    
    def test_required_fields_only(self):
        """Test form with only required fields"""
        form_data = {
            'first_name': 'Jean',
            'last_name': 'Pierre',
            'address_line1': '123 Rue Example',
            'city': 'Port-au-Prince',
            'country': 'Haïti',
            'phone': '+509 1234-5678'
        }
        
        form = ShippingAddressForm(data=form_data)
        assert form.is_valid()
    
    def test_missing_required_fields(self):
        """Test form with missing required fields"""
        form_data = {
            'first_name': 'Jean',
            # Missing last_name, address_line1, city, country, phone
        }
        
        form = ShippingAddressForm(data=form_data)
        assert not form.is_valid()
        
        required_fields = ['last_name', 'address_line1', 'city', 'country', 'phone']
        for field in required_fields:
            assert field in form.errors
    
    def test_haitian_address_validation(self):
        """Test Haitian-specific address validation"""
        # Test valid Haitian cities
        valid_cities = ['Port-au-Prince', 'Cap-Haïtien', 'Gonaïves', 'Saint-Marc']
        
        for city in valid_cities:
            form_data = {
                'first_name': 'Jean',
                'last_name': 'Pierre',
                'address_line1': '123 Rue Example',
                'city': city,
                'country': 'Haïti',
                'phone': '+509 1234-5678'
            }
            
            form = ShippingAddressForm(data=form_data)
            assert form.is_valid(), f"City {city} should be valid"


@pytest.mark.django_db
class TestPaymentMethodForm:
    """Test suite for PaymentMethodForm"""
    
    def test_moncash_payment_method(self):
        """Test form with MonCash payment method"""
        form_data = {
            'payment_method': 'moncash',
            'moncash_phone': '+509 1234-5678'
        }
        
        form = PaymentMethodForm(data=form_data)
        assert form.is_valid()
    
    def test_cash_on_delivery_method(self):
        """Test form with cash on delivery"""
        form_data = {
            'payment_method': 'cash_on_delivery'
        }
        
        form = PaymentMethodForm(data=form_data)
        assert form.is_valid()
    
    def test_moncash_without_phone(self):
        """Test MonCash selection without phone number"""
        form_data = {
            'payment_method': 'moncash'
            # Missing moncash_phone
        }
        
        form = PaymentMethodForm(data=form_data)
        assert not form.is_valid()
        assert 'moncash_phone' in form.errors
    
    def test_invalid_moncash_phone(self):
        """Test MonCash with invalid phone number"""
        form_data = {
            'payment_method': 'moncash',
            'moncash_phone': '+1 555-1234'  # Not Haitian number
        }
        
        form = PaymentMethodForm(data=form_data)
        assert not form.is_valid()
        assert 'moncash_phone' in form.errors


@pytest.mark.django_db  
class TestProductCreationForm:
    """Test suite for ProductCreationForm"""
    
    def setup_method(self):
        """Set up test data"""
        self.category = CategoryFactory()
    
    def test_valid_product_creation(self):
        """Test form with valid product data"""
        form_data = {
            'name': 'iPhone 13 Pro',
            'description': 'Dernière génération d\'iPhone avec des fonctionnalités avancées.',
            'category': self.category.id,
            'price': '999.99',
            'stock_quantity': '50',
            'brand': 'Apple',
            'is_digital': False,
            'weight': '0.5'
        }
        
        form = ProductCreationForm(data=form_data)
        assert form.is_valid()
    
    def test_invalid_price(self):
        """Test form with invalid price"""
        form_data = {
            'name': 'Test Product',
            'description': 'Test description',
            'category': self.category.id,
            'price': '-50.00',  # Negative price
            'stock_quantity': '10'
        }
        
        form = ProductCreationForm(data=form_data)
        assert not form.is_valid()
        assert 'price' in form.errors
    
    def test_promotional_price_validation(self):
        """Test promotional price validation"""
        form_data = {
            'name': 'Test Product',
            'description': 'Test description',
            'category': self.category.id,
            'price': '100.00',
            'promotional_price': '150.00',  # Higher than regular price
            'stock_quantity': '10'
        }
        
        form = ProductCreationForm(data=form_data)
        assert not form.is_valid()
        assert 'promotional_price' in form.errors
    
    def test_negative_stock_quantity(self):
        """Test form with negative stock quantity"""
        form_data = {
            'name': 'Test Product',
            'description': 'Test description',
            'category': self.category.id,
            'price': '50.00',
            'stock_quantity': '-5'  # Negative stock
        }
        
        form = ProductCreationForm(data=form_data)
        assert not form.is_valid()
        assert 'stock_quantity' in form.errors


@pytest.mark.django_db
class TestContactForm:
    """Test suite for ContactForm"""
    
    def test_valid_contact_form(self):
        """Test form with valid contact data"""
        form_data = {
            'name': 'Jean Pierre',
            'email': 'jean@example.com',
            'subject': 'Question sur un produit',
            'message': 'Bonjour, j\'aimerais avoir plus d\'informations sur vos produits.'
        }
        
        form = ContactForm(data=form_data)
        assert form.is_valid()
    
    def test_missing_required_fields(self):
        """Test form with missing required fields"""
        form_data = {
            'name': 'Jean Pierre',
            # Missing email, subject, message
        }
        
        form = ContactForm(data=form_data)
        assert not form.is_valid()
        
        required_fields = ['email', 'subject', 'message']
        for field in required_fields:
            assert field in form.errors
    
    def test_invalid_email(self):
        """Test form with invalid email"""
        form_data = {
            'name': 'Jean Pierre',
            'email': 'invalid-email',
            'subject': 'Test',
            'message': 'Test message'
        }
        
        form = ContactForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors
    
    def test_message_length_validation(self):
        """Test message length validation"""
        short_message = "Trop court."
        long_message = "x" * 2001  # Too long
        
        # Test too short
        form_data = {
            'name': 'Jean Pierre',
            'email': 'jean@example.com',
            'subject': 'Test',
            'message': short_message
        }
        
        form = ContactForm(data=form_data)
        assert not form.is_valid()
        assert 'message' in form.errors
        
        # Test too long
        form_data['message'] = long_message
        form = ContactForm(data=form_data)
        assert not form.is_valid()
        assert 'message' in form.errors


@pytest.mark.django_db
class TestNewsletterSubscriptionForm:
    """Test suite for NewsletterSubscriptionForm"""
    
    def test_valid_newsletter_subscription(self):
        """Test form with valid subscription data"""
        form_data = {
            'email': 'subscriber@example.com',
            'first_name': 'Marie',
            'last_name': 'Dupont',
            'categories_of_interest': ['electronics', 'fashion']
        }
        
        form = NewsletterSubscriptionForm(data=form_data)
        assert form.is_valid()
    
    def test_email_only_subscription(self):
        """Test subscription with email only"""
        form_data = {
            'email': 'subscriber@example.com'
        }
        
        form = NewsletterSubscriptionForm(data=form_data)
        assert form.is_valid()
    
    def test_invalid_email(self):
        """Test form with invalid email"""
        form_data = {
            'email': 'invalid-email-format'
        }
        
        form = NewsletterSubscriptionForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors
    
    def test_duplicate_email_subscription(self):
        """Test subscription with already subscribed email"""
        from .factories import NewsletterSubscriberFactory
        
        # Create existing subscriber
        existing_subscriber = NewsletterSubscriberFactory(email='existing@example.com')
        
        form_data = {
            'email': 'existing@example.com'
        }
        
        form = NewsletterSubscriptionForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors


@pytest.mark.django_db
class TestUserProfileForm:
    """Test suite for UserProfileForm"""
    
    def setup_method(self):
        """Set up test data"""
        self.user = UserFactory()
    
    def test_valid_profile_update(self):
        """Test form with valid profile update data"""
        form_data = {
            'first_name': 'Jean-Baptiste',
            'last_name': 'Pierre-Louis',
            'phone': '+509 3456-7890',
            'date_of_birth': '1990-01-15'
        }
        
        form = UserProfileForm(data=form_data, instance=self.user)
        assert form.is_valid()
        
        # Test saving
        updated_user = form.save()
        assert updated_user.first_name == 'Jean-Baptiste'
        assert updated_user.last_name == 'Pierre-Louis'
    
    def test_phone_number_update(self):
        """Test updating phone number"""
        form_data = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'phone': '+509 9999-8888'
        }
        
        form = UserProfileForm(data=form_data, instance=self.user)
        assert form.is_valid()
        
        updated_user = form.save()
        assert updated_user.phone == '+509 9999-8888'
    
    def test_invalid_phone_format(self):
        """Test form with invalid phone format"""
        form_data = {
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'phone': '123-456'  # Invalid format
        }
        
        form = UserProfileForm(data=form_data, instance=self.user)
        assert not form.is_valid()
        assert 'phone' in form.errors