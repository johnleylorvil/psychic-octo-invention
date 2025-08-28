# Unit tests for Afèpanou marketplace models
import pytest
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

from marketplace.models import (
    Category, Product, ProductImage, Cart, CartItem, Order, OrderItem,
    Transaction, Review, VendorProfile, Banner, Page
)
from .factories import (
    UserFactory, SellerUserFactory, VendorProfileFactory, CategoryFactory,
    ProductFactory, ProductWithPromotionFactory, ProductImageFactory,
    CartFactory, CartItemFactory, OrderFactory, OrderItemFactory,
    TransactionFactory, ReviewFactory, BannerFactory, PageFactory
)

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test suite for User model"""
    
    def test_user_creation(self):
        """Test basic user creation"""
        user = UserFactory()
        assert user.email
        assert user.first_name
        assert user.last_name
        assert user.is_active
        assert not user.is_seller
        assert str(user) == f"{user.first_name} {user.last_name}"
    
    def test_seller_user_creation(self):
        """Test seller user creation"""
        seller = SellerUserFactory()
        assert seller.is_seller
        assert seller.is_active
    
    def test_email_uniqueness(self):
        """Test that email addresses must be unique"""
        user1 = UserFactory(email="test@example.com")
        with pytest.raises(IntegrityError):
            UserFactory(email="test@example.com")
    
    def test_user_full_name_property(self):
        """Test user full name property"""
        user = UserFactory(first_name="Jean", last_name="Pierre")
        assert user.get_full_name() == "Jean Pierre"


@pytest.mark.django_db
class TestVendorProfileModel:
    """Test suite for VendorProfile model"""
    
    def test_vendor_profile_creation(self):
        """Test vendor profile creation"""
        vendor = VendorProfileFactory()
        assert vendor.user.is_seller
        assert vendor.business_name
        assert vendor.is_verified
        assert str(vendor) == vendor.business_name


@pytest.mark.django_db
class TestCategoryModel:
    """Test suite for Category model"""
    
    def test_category_creation(self):
        """Test basic category creation"""
        category = CategoryFactory(name="Électronique")
        assert category.name == "Électronique"
        assert category.slug == "électronique"
        assert category.is_active
        assert str(category) == "Électronique"
    
    def test_category_slug_generation(self):
        """Test automatic slug generation"""
        category = CategoryFactory(name="Vêtements et Mode")
        assert category.slug == "vêtements et mode"
    
    def test_category_hierarchy(self):
        """Test category parent-child relationships"""
        parent = CategoryFactory(name="Électronique")
        child = CategoryFactory(name="Téléphones", parent=parent)
        
        assert child.parent == parent
        assert child in parent.children.all()
    
    def test_category_product_count_property(self):
        """Test product count property"""
        category = CategoryFactory()
        ProductFactory.create_batch(3, category=category, is_active=True)
        ProductFactory(category=category, is_active=False)
        
        assert category.product_count == 3
    
    def test_category_uniqueness(self):
        """Test that category slugs must be unique"""
        CategoryFactory(slug="electronics")
        with pytest.raises(IntegrityError):
            CategoryFactory(slug="electronics")


@pytest.mark.django_db
class TestProductModel:
    """Test suite for Product model"""
    
    def test_product_creation(self):
        """Test basic product creation"""
        product = ProductFactory()
        assert product.name
        assert product.slug
        assert product.category
        assert product.seller
        assert product.price > 0
        assert product.stock_quantity >= 0
        assert product.sku
        assert product.is_active
    
    def test_product_slug_generation(self):
        """Test automatic slug generation"""
        product = ProductFactory(name="iPhone 13 Pro Max")
        assert "iphone-13-pro-max" in product.slug.lower()
    
    def test_product_sku_generation(self):
        """Test automatic SKU generation"""
        product = ProductFactory()
        assert product.sku.startswith("AFE-")
        assert len(product.sku) >= 8
    
    def test_product_current_price_property(self):
        """Test current price property with and without promotion"""
        regular_product = ProductFactory(price=Decimal('100.00'))
        assert regular_product.current_price == Decimal('100.00')
        
        promo_product = ProductWithPromotionFactory(
            price=Decimal('100.00'), 
            promotional_price=Decimal('80.00')
        )
        assert promo_product.current_price == Decimal('80.00')
    
    def test_product_discount_percentage(self):
        """Test discount percentage calculation"""
        product = ProductWithPromotionFactory(
            price=Decimal('100.00'),
            promotional_price=Decimal('80.00')
        )
        assert product.discount_percentage == 20.0
    
    def test_product_in_stock_property(self):
        """Test stock availability check"""
        in_stock = ProductFactory(stock_quantity=10)
        assert in_stock.in_stock
        
        out_of_stock = ProductFactory(stock_quantity=0)
        assert not out_of_stock.in_stock
        
        no_stock_tracking = ProductFactory(stock_quantity=None)
        assert not no_stock_tracking.in_stock
    
    def test_product_is_low_stock_property(self):
        """Test low stock detection"""
        low_stock = ProductFactory(stock_quantity=3, min_stock_alert=5)
        assert low_stock.is_low_stock
        
        good_stock = ProductFactory(stock_quantity=10, min_stock_alert=5)
        assert not good_stock.is_low_stock
    
    def test_product_reserve_quantity(self):
        """Test quantity reservation functionality"""
        product = ProductFactory(stock_quantity=10, reserved_quantity=2)
        
        # Test successful reservation
        assert product.reserve_quantity(3)
        assert product.reserved_quantity == 5
        assert product.available_quantity == 5
        
        # Test insufficient stock
        assert not product.reserve_quantity(10)
        assert product.reserved_quantity == 5
    
    def test_product_release_reserved_quantity(self):
        """Test releasing reserved quantity"""
        product = ProductFactory(stock_quantity=10, reserved_quantity=5)
        
        # Test successful release
        assert product.release_reserved_quantity(3)
        assert product.reserved_quantity == 2
        
        # Test invalid release amount
        assert not product.release_reserved_quantity(10)
        assert product.reserved_quantity == 2
    
    def test_product_validation(self):
        """Test product model validation"""
        # Test promotional price validation
        with pytest.raises(ValidationError):
            product = ProductFactory.build(
                price=Decimal('100.00'),
                promotional_price=Decimal('150.00')  # Higher than regular price
            )
            product.full_clean()
    
    def test_product_uniqueness(self):
        """Test product SKU uniqueness"""
        ProductFactory(sku="TEST-001")
        with pytest.raises(IntegrityError):
            ProductFactory(sku="TEST-001")


@pytest.mark.django_db
class TestProductImageModel:
    """Test suite for ProductImage model"""
    
    def test_product_image_creation(self):
        """Test product image creation"""
        image = ProductImageFactory()
        assert image.product
        assert image.image_url
        assert image.image_path
        assert not image.is_primary
    
    def test_primary_image_enforcement(self):
        """Test that only one image can be primary per product"""
        product = ProductFactory()
        
        # Create first primary image
        image1 = ProductImageFactory(product=product, is_primary=True)
        assert image1.is_primary
        
        # Create second primary image - should make first non-primary
        image2 = ProductImageFactory(product=product, is_primary=True)
        image1.refresh_from_db()
        
        assert image2.is_primary
        assert not image1.is_primary
    
    def test_product_primary_image_property(self):
        """Test product's primary image property"""
        product = ProductFactory()
        
        # No images - should return None
        assert product.primary_image is None
        
        # Add non-primary images
        img1 = ProductImageFactory(product=product, is_primary=False, sort_order=2)
        img2 = ProductImageFactory(product=product, is_primary=False, sort_order=1)
        
        # Should return first image (by sort order)
        assert product.primary_image == img2
        
        # Add primary image
        primary_img = ProductImageFactory(product=product, is_primary=True)
        assert product.primary_image == primary_img


@pytest.mark.django_db
class TestCartModel:
    """Test suite for Cart model"""
    
    def test_cart_creation(self):
        """Test cart creation for authenticated user"""
        cart = CartFactory()
        assert cart.user
        assert cart.is_active
        assert cart.session_id is None
    
    def test_anonymous_cart_creation(self):
        """Test cart creation for anonymous user"""
        from .factories import AnonymousCartFactory
        cart = AnonymousCartFactory()
        assert cart.user is None
        assert cart.session_id
        assert cart.expires_at
    
    def test_cart_total_items_property(self):
        """Test cart total items calculation"""
        cart = CartFactory()
        CartItemFactory(cart=cart, quantity=2)
        CartItemFactory(cart=cart, quantity=3)
        
        assert cart.total_items == 5
    
    def test_cart_subtotal_property(self):
        """Test cart subtotal calculation"""
        cart = CartFactory()
        
        # Add items with known prices
        product1 = ProductFactory(price=Decimal('50.00'))
        product2 = ProductFactory(price=Decimal('25.00'))
        
        CartItemFactory(cart=cart, product=product1, quantity=2)
        CartItemFactory(cart=cart, product=product2, quantity=1)
        
        expected_subtotal = (Decimal('50.00') * 2) + (Decimal('25.00') * 1)
        assert cart.subtotal == expected_subtotal
    
    def test_cart_is_empty_property(self):
        """Test cart empty status"""
        cart = CartFactory()
        assert cart.is_empty
        
        CartItemFactory(cart=cart)
        assert not cart.is_empty
    
    def test_cart_clear_method(self):
        """Test cart clearing functionality"""
        cart = CartFactory()
        CartItemFactory.create_batch(3, cart=cart)
        
        assert not cart.is_empty
        cart.clear()
        assert cart.is_empty


@pytest.mark.django_db
class TestCartItemModel:
    """Test suite for CartItem model"""
    
    def test_cart_item_creation(self):
        """Test cart item creation"""
        item = CartItemFactory()
        assert item.cart
        assert item.product
        assert item.quantity > 0
        assert item.price > 0
    
    def test_cart_item_total_price_property(self):
        """Test total price calculation"""
        product = ProductFactory(price=Decimal('25.00'))
        item = CartItemFactory(product=product, quantity=3)
        
        assert item.total_price == Decimal('75.00')
    
    def test_cart_item_price_update(self):
        """Test that price is updated on save"""
        product = ProductFactory(price=Decimal('100.00'))
        item = CartItemFactory(product=product)
        
        # Change product price
        product.price = Decimal('120.00')
        product.save()
        
        # Save cart item - should update price
        item.save()
        assert item.price == Decimal('120.00')


@pytest.mark.django_db
class TestOrderModel:
    """Test suite for Order model"""
    
    def test_order_creation(self):
        """Test basic order creation"""
        order = OrderFactory()
        assert order.user
        assert order.order_number
        assert order.customer_email
        assert order.total_amount > 0
        assert order.status == 'pending'
        assert order.payment_status == 'pending'
    
    def test_order_number_generation(self):
        """Test automatic order number generation"""
        order = OrderFactory()
        assert order.order_number.startswith("AF")
        assert len(order.order_number) >= 8
    
    def test_order_status_properties(self):
        """Test order status checking properties"""
        order = OrderFactory(status='pending', payment_status='pending')
        assert order.can_be_cancelled
        assert not order.is_paid
        assert not order.is_delivered
        
        order.status = 'delivered'
        order.payment_status = 'paid'
        order.save()
        
        assert not order.can_be_cancelled
        assert order.is_paid
        assert order.is_delivered


@pytest.mark.django_db
class TestOrderItemModel:
    """Test suite for OrderItem model"""
    
    def test_order_item_creation(self):
        """Test order item creation"""
        item = OrderItemFactory()
        assert item.order
        assert item.product
        assert item.quantity > 0
        assert item.unit_price > 0
        assert item.product_name
    
    def test_order_item_total_calculation(self):
        """Test total price calculation on save"""
        item = OrderItemFactory(quantity=2, unit_price=Decimal('50.00'))
        assert item.total_price == Decimal('100.00')
    
    def test_order_item_product_snapshot(self):
        """Test product information snapshot"""
        product = ProductFactory(name="Test Product", sku="TEST-001")
        item = OrderItemFactory(product=product)
        
        assert item.product_name == "Test Product"
        assert item.product_sku == "TEST-001"


@pytest.mark.django_db
class TestTransactionModel:
    """Test suite for Transaction model"""
    
    def test_transaction_creation(self):
        """Test transaction creation"""
        transaction = TransactionFactory()
        assert transaction.order
        assert transaction.amount > 0
        assert transaction.currency == 'HTG'
        assert transaction.status == 'pending'
        assert transaction.transaction_id
    
    def test_transaction_id_generation(self):
        """Test automatic transaction ID generation"""
        transaction = TransactionFactory()
        assert transaction.transaction_id.startswith("TXN")
    
    def test_transaction_status_properties(self):
        """Test transaction status properties"""
        transaction = TransactionFactory(status='pending')
        assert transaction.is_pending
        assert not transaction.is_successful
        
        transaction.status = 'completed'
        transaction.save()
        
        assert not transaction.is_pending
        assert transaction.is_successful
    
    def test_transaction_mark_as_completed(self):
        """Test marking transaction as completed"""
        transaction = TransactionFactory(status='pending')
        
        gateway_response = {'status': 'success', 'reference': '12345'}
        transaction.mark_as_completed(gateway_response)
        
        assert transaction.status == 'completed'
        assert transaction.verified_at
        assert transaction.gateway_response == gateway_response
    
    def test_transaction_mark_as_failed(self):
        """Test marking transaction as failed"""
        transaction = TransactionFactory(status='pending')
        
        transaction.mark_as_failed("Payment declined")
        
        assert transaction.status == 'failed'
        assert transaction.failure_reason == "Payment declined"


@pytest.mark.django_db
class TestReviewModel:
    """Test suite for Review model"""
    
    def test_review_creation(self):
        """Test review creation"""
        review = ReviewFactory()
        assert review.product
        assert review.user
        assert 1 <= review.rating <= 5
        assert review.title
        assert review.is_approved
    
    def test_review_uniqueness(self):
        """Test that users can only review products once"""
        user = UserFactory()
        product = ProductFactory()
        
        ReviewFactory(user=user, product=product)
        
        with pytest.raises(IntegrityError):
            ReviewFactory(user=user, product=product)
    
    def test_product_average_rating(self):
        """Test product average rating calculation"""
        product = ProductFactory()
        
        # Add reviews with different ratings
        ReviewFactory(product=product, rating=5, is_approved=True)
        ReviewFactory(product=product, rating=3, is_approved=True)
        ReviewFactory(product=product, rating=4, is_approved=True)
        ReviewFactory(product=product, rating=2, is_approved=False)  # Should be excluded
        
        # Average of 5, 3, 4 = 4.0
        assert product.average_rating == 4.0
    
    def test_product_review_count(self):
        """Test product review count"""
        product = ProductFactory()
        
        ReviewFactory.create_batch(3, product=product, is_approved=True)
        ReviewFactory.create_batch(2, product=product, is_approved=False)
        
        # Only approved reviews should be counted
        assert product.review_count == 3


@pytest.mark.django_db
class TestBannerModel:
    """Test suite for Banner model"""
    
    def test_banner_creation(self):
        """Test banner creation"""
        banner = BannerFactory()
        assert banner.title
        assert banner.image_url
        assert banner.is_active
        assert str(banner) == banner.title
    
    def test_banner_is_currently_active_property(self):
        """Test banner active status with date restrictions"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Active banner without date restrictions
        banner = BannerFactory(is_active=True, start_date=None, end_date=None)
        assert banner.is_currently_active
        
        # Inactive banner
        banner.is_active = False
        banner.save()
        assert not banner.is_currently_active
        
        # Banner with future start date
        banner.is_active = True
        banner.start_date = timezone.now().date() + timedelta(days=1)
        banner.save()
        assert not banner.is_currently_active
        
        # Banner with past end date
        banner.start_date = None
        banner.end_date = timezone.now().date() - timedelta(days=1)
        banner.save()
        assert not banner.is_currently_active


@pytest.mark.django_db
class TestPageModel:
    """Test suite for Page model"""
    
    def test_page_creation(self):
        """Test page creation"""
        page = PageFactory()
        assert page.title
        assert page.slug
        assert page.is_active
        assert page.author
    
    def test_page_slug_generation(self):
        """Test automatic slug generation"""
        page = PageFactory(title="About Our Company")
        assert page.slug == "about-our-company"
    
    def test_page_word_count_property(self):
        """Test word count calculation"""
        page = PageFactory(content="This is a test content with exactly eight words.")
        assert page.word_count == 8
    
    def test_page_reading_time_property(self):
        """Test reading time estimation"""
        # Create content with approximately 400 words (should be 2 minutes)
        content = " ".join(["word"] * 400)
        page = PageFactory(content=content)
        assert page.reading_time == 2