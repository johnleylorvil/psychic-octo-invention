# Test factories for Afèpanou marketplace
import factory
from factory import fuzzy
from decimal import Decimal
from django.contrib.auth import get_user_model
from marketplace.models import (
    Category, Product, ProductImage, Cart, CartItem, Order, OrderItem,
    Transaction, Review, VendorProfile, Banner, Page, NewsletterSubscriber,
    SiteSetting, Promotion
)

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users"""
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f"user{n}@test.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name') 
    phone = factory.Faker('phone_number')
    is_active = True
    is_seller = False
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if create:
            obj.set_password(extracted or 'testpass123')
            obj.save()


class SellerUserFactory(UserFactory):
    """Factory for creating seller users"""
    is_seller = True


class VendorProfileFactory(factory.django.DjangoModelFactory):
    """Factory for creating vendor profiles"""
    class Meta:
        model = VendorProfile
    
    user = factory.SubFactory(SellerUserFactory)
    business_name = factory.Faker('company')
    business_description = factory.Faker('text', max_nb_chars=500)
    business_address = factory.Faker('address')
    business_phone = factory.Faker('phone_number')
    business_email = factory.LazyAttribute(lambda obj: obj.user.email)
    is_verified = True


class CategoryFactory(factory.django.DjangoModelFactory):
    """Factory for creating product categories"""
    class Meta:
        model = Category
    
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower())
    description = factory.Faker('text', max_nb_chars=200)
    is_active = True
    is_featured = False
    sort_order = factory.Sequence(lambda n: n)


class ProductFactory(factory.django.DjangoModelFactory):
    """Factory for creating products"""
    class Meta:
        model = Product
    
    name = factory.Faker('catch_phrase')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    short_description = factory.Faker('sentence', nb_words=10)
    description = factory.Faker('text', max_nb_chars=1000)
    category = factory.SubFactory(CategoryFactory)
    seller = factory.SubFactory(SellerUserFactory)
    price = fuzzy.FuzzyDecimal(10.00, 1000.00, 2)
    promotional_price = None
    cost_price = fuzzy.FuzzyDecimal(5.00, 500.00, 2)
    stock_quantity = fuzzy.FuzzyInteger(0, 100)
    min_stock_alert = 5
    sku = factory.Sequence(lambda n: f"AFE-TEST-{n:04d}")
    is_active = True
    is_featured = False
    is_digital = False
    weight = fuzzy.FuzzyDecimal(0.1, 10.0, 2)
    brand = factory.Faker('company')


class ProductWithPromotionFactory(ProductFactory):
    """Factory for products with promotional pricing"""
    promotional_price = factory.LazyAttribute(
        lambda obj: obj.price * Decimal('0.8')  # 20% discount
    )


class ProductImageFactory(factory.django.DjangoModelFactory):
    """Factory for creating product images"""
    class Meta:
        model = ProductImage
    
    product = factory.SubFactory(ProductFactory)
    image_url = factory.Faker('image_url')
    image_path = factory.Faker('file_path', extension='jpg')
    alt_text = factory.LazyAttribute(lambda obj: f"Image of {obj.product.name}")
    is_primary = False
    sort_order = factory.Sequence(lambda n: n)


class CartFactory(factory.django.DjangoModelFactory):
    """Factory for creating shopping carts"""
    class Meta:
        model = Cart
    
    user = factory.SubFactory(UserFactory)
    session_id = None
    is_active = True


class AnonymousCartFactory(CartFactory):
    """Factory for anonymous user carts"""
    user = None
    session_id = factory.Faker('uuid4')


class CartItemFactory(factory.django.DjangoModelFactory):
    """Factory for creating cart items"""
    class Meta:
        model = CartItem
    
    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = fuzzy.FuzzyInteger(1, 5)
    price = factory.LazyAttribute(lambda obj: obj.product.current_price)


class OrderFactory(factory.django.DjangoModelFactory):
    """Factory for creating orders"""
    class Meta:
        model = Order
    
    user = factory.SubFactory(UserFactory)
    customer_name = factory.LazyAttribute(lambda obj: f"{obj.user.first_name} {obj.user.last_name}")
    customer_email = factory.LazyAttribute(lambda obj: obj.user.email)
    customer_phone = factory.Faker('phone_number')
    shipping_address = factory.Faker('address')
    shipping_city = 'Port-au-Prince'
    shipping_country = 'Haïti'
    subtotal = fuzzy.FuzzyDecimal(50.00, 500.00, 2)
    shipping_cost = Decimal('25.00')
    tax_amount = Decimal('0.00')
    total_amount = factory.LazyAttribute(lambda obj: obj.subtotal + obj.shipping_cost)
    status = 'pending'
    payment_status = 'pending'
    payment_method = 'moncash'


class OrderItemFactory(factory.django.DjangoModelFactory):
    """Factory for creating order items"""
    class Meta:
        model = OrderItem
    
    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = fuzzy.FuzzyInteger(1, 3)
    unit_price = factory.LazyAttribute(lambda obj: obj.product.current_price)
    total_price = factory.LazyAttribute(lambda obj: obj.quantity * obj.unit_price)
    product_name = factory.LazyAttribute(lambda obj: obj.product.name)
    product_sku = factory.LazyAttribute(lambda obj: obj.product.sku)


class TransactionFactory(factory.django.DjangoModelFactory):
    """Factory for creating transactions"""
    class Meta:
        model = Transaction
    
    order = factory.SubFactory(OrderFactory)
    amount = factory.LazyAttribute(lambda obj: obj.order.total_amount)
    currency = 'HTG'
    status = 'pending'
    payment_method = 'moncash'
    transaction_id = factory.Sequence(lambda n: f"TXN{n:08d}")
    reference_number = factory.Faker('uuid4')


class ReviewFactory(factory.django.DjangoModelFactory):
    """Factory for creating product reviews"""
    class Meta:
        model = Review
    
    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory(UserFactory)
    rating = fuzzy.FuzzyInteger(1, 5)
    title = factory.Faker('sentence', nb_words=4)
    comment = factory.Faker('text', max_nb_chars=500)
    is_approved = True
    is_verified_purchase = False


class BannerFactory(factory.django.DjangoModelFactory):
    """Factory for creating banners"""
    class Meta:
        model = Banner
    
    title = factory.Faker('catch_phrase')
    subtitle = factory.Faker('sentence')
    description = factory.Faker('text', max_nb_chars=200)
    image_url = factory.Faker('image_url')
    image_path = factory.Faker('file_path', extension='jpg')
    link_url = factory.Faker('url')
    button_text = 'Découvrir'
    is_active = True
    sort_order = factory.Sequence(lambda n: n)


class PageFactory(factory.django.DjangoModelFactory):
    """Factory for creating static pages"""
    class Meta:
        model = Page
    
    title = factory.Faker('sentence', nb_words=3)
    slug = factory.LazyAttribute(lambda obj: obj.title.lower().replace(' ', '-'))
    content = factory.Faker('text', max_nb_chars=2000)
    is_active = True
    author = factory.SubFactory(UserFactory)


class NewsletterSubscriberFactory(factory.django.DjangoModelFactory):
    """Factory for creating newsletter subscribers"""
    class Meta:
        model = NewsletterSubscriber
    
    email = factory.Sequence(lambda n: f"subscriber{n}@test.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    status = 'active'
    source = 'website'


class SiteSettingFactory(factory.django.DjangoModelFactory):
    """Factory for creating site settings"""
    class Meta:
        model = SiteSetting
    
    setting_key = factory.Sequence(lambda n: f"test_setting_{n}")
    setting_value = factory.Faker('word')
    setting_type = 'text'
    description = factory.Faker('sentence')
    group_name = 'general'
    is_public = False


class PromotionFactory(factory.django.DjangoModelFactory):
    """Factory for creating promotions"""
    class Meta:
        model = Promotion
    
    name = factory.Faker('catch_phrase')
    code = factory.Sequence(lambda n: f"TEST{n:04d}")
    discount_type = 'percentage'
    discount_value = fuzzy.FuzzyDecimal(5.00, 25.00, 2)
    minimum_amount = fuzzy.FuzzyDecimal(50.00, 200.00, 2)
    maximum_uses = fuzzy.FuzzyInteger(10, 100)
    current_uses = 0
    start_date = factory.Faker('date_time_this_month')
    end_date = factory.Faker('date_time_this_year')
    is_active = True