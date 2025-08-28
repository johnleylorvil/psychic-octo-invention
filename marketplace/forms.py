# marketplace/forms.py
"""
Comprehensive form classes for Afèpanou marketplace
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

from .models import (
    User, Product, Review, VendorProfile, Address, 
    Wishlist, Order, NewsletterSubscriber
)
from .validators import validate_haitian_phone_number
from .constants import HAITI_DEPARTMENTS, RATING_CHOICES


class ProductSearchForm(forms.Form):
    """Advanced product search form"""
    
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search for products...'),
            'autocomplete': 'off'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label=_('All Categories'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Min Price')
        })
    )
    
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Max Price')
        })
    )
    
    brand = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Brand')
        })
    )
    
    in_stock = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    on_sale = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('relevance', _('Relevance')),
            ('price_low', _('Price: Low to High')),
            ('price_high', _('Price: High to Low')),
            ('newest', _('Newest First')),
            ('rating', _('Highest Rated')),
            ('popular', _('Most Popular')),
        ],
        required=False,
        initial='relevance',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category
        self.fields['category'].queryset = Category.objects.active()
    
    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise ValidationError(_('Maximum price must be greater than minimum price.'))
        
        return cleaned_data


class ProductReviewForm(forms.ModelForm):
    """Form for product reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=RATING_CHOICES,
                attrs={'class': 'form-select'}
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Share your experience with this product...')
            })
        }
    
    def clean_comment(self):
        comment = self.cleaned_data['comment']
        if len(comment.strip()) < 10:
            raise ValidationError(_('Review must be at least 10 characters long.'))
        return comment


class UserRegistrationForm(UserCreationForm):
    """Enhanced user registration form for Haiti"""
    
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('First Name')
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Last Name')
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Email Address')
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        validators=[validate_haitian_phone_number],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Phone Number (e.g., +509 1234 5678)')
        })
    )
    
    city = forms.CharField(
        max_length=50,
        initial='Port-au-Prince',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('City')
        })
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={
            'required': _('You must accept the terms and conditions.')
        }
    )
    
    newsletter_signup = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 
                  'city', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Username')
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': _('Password')
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': _('Confirm Password')
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('This email address is already registered.'))
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.city = self.cleaned_data['city']
        
        if commit:
            user.save()
            
            # Subscribe to newsletter if requested
            if self.cleaned_data['newsletter_signup']:
                NewsletterSubscriber.objects.create(
                    user=user,
                    email=user.email,
                    is_active=True
                )
        
        return user


class UserProfileForm(forms.ModelForm):
    """User profile update form"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 
                  'city', 'birth_date', 'gender', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Phone Number')
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_('This email address is already in use.'))
        return email


class SellerApplicationForm(forms.ModelForm):
    """Seller application form"""
    
    business_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Describe your business and the products you plan to sell...')
        })
    )
    
    class Meta:
        model = VendorProfile
        fields = ['business_name', 'business_type', 'business_description', 
                  'business_address', 'business_phone', 'business_email', 
                  'website', 'tax_id', 'moncash_number']
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Business Name')
            }),
            'business_type': forms.Select(attrs={'class': 'form-select'}),
            'business_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Business Address')
            }),
            'business_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Business Phone Number')
            }),
            'business_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Business Email')
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('Website (optional)')
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Tax ID (optional)')
            }),
            'moncash_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('MonCash Number for payments')
            })
        }


class ShippingAddressForm(forms.ModelForm):
    """Shipping address form"""
    
    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'phone', 'company_name',
                  'address_line1', 'address_line2', 'city', 'department',
                  'postal_code', 'delivery_instructions', 'landmark']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('First Name')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Last Name')
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Phone Number')
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Company Name (optional)')
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Address Line 1')
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Address Line 2 (optional)')
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('City')
            }),
            'department': forms.Select(
                choices=[('', _('Select Department'))] + list(HAITI_DEPARTMENTS),
                attrs={'class': 'form-select'}
            ),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Postal Code')
            }),
            'delivery_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('Special delivery instructions (optional)')
            }),
            'landmark': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nearby landmark (optional)')
            })
        }


class PaymentMethodForm(forms.Form):
    """Payment method selection form"""
    
    PAYMENT_METHOD_CHOICES = [
        ('moncash', _('MonCash')),
        ('cash_on_delivery', _('Cash on Delivery')),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='moncash'
    )
    
    moncash_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your MonCash Number')
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        moncash_number = cleaned_data.get('moncash_number')
        
        if payment_method == 'moncash' and not moncash_number:
            raise ValidationError({
                'moncash_number': _('MonCash number is required for MonCash payment.')
            })
        
        return cleaned_data


class ProductCreateForm(forms.ModelForm):
    """Form for creating/editing products"""
    
    class Meta:
        model = Product
        fields = ['name', 'category', 'short_description', 'description', 
                  'price', 'promotional_price', 'cost_price', 'sku',
                  'stock_quantity', 'min_stock_alert', 'is_digital',
                  'weight', 'brand', 'color', 'material', 'condition_type',
                  'tags', 'warranty_period', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Product Name')
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'short_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Brief product description')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('Detailed product description')
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'promotional_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'cost_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Stock Keeping Unit (optional)')
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'min_stock_alert': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'is_digital': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Brand Name')
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Product Color')
            }),
            'material': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Material')
            }),
            'condition_type': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Tags (comma-separated)')
            }),
            'warranty_period': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': _('Warranty period in months')
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        promotional_price = cleaned_data.get('promotional_price')
        
        if promotional_price and price and promotional_price >= price:
            raise ValidationError({
                'promotional_price': _('Promotional price must be less than regular price.')
            })
        
        return cleaned_data


class NewsletterSubscriptionForm(forms.ModelForm):
    """Newsletter subscription form"""
    
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter your email address')
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if NewsletterSubscriber.objects.filter(email=email, is_active=True).exists():
            raise ValidationError(_('This email is already subscribed to our newsletter.'))
        return email


class ContactForm(forms.Form):
    """Contact form"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your Name')
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Your Email')
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Subject')
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': _('Your Message')
        })
    )
    
    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message.strip()) < 20:
            raise ValidationError(_('Message must be at least 20 characters long.'))
        return message


class CustomLoginForm(AuthenticationForm):
    """Custom login form with styling"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Username or Email'),
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Password')
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_username(self):
        username = self.cleaned_data['username']
        # Allow login with email
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                return user.username
            except User.DoesNotExist:
                pass
        return username


class AddressForm(forms.ModelForm):
    """Address management form"""
    
    class Meta:
        model = Address
        fields = [
            'first_name', 'last_name', 'address_line1', 'address_line2',
            'city', 'department', 'postal_code', 'phone', 'is_default'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('First name')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': _('Last name')
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Street address')
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Apartment, suite, etc. (optional)'),
                'required': False
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('City')
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Department')
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Postal code'),
                'required': False
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Phone number')
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'address_line1': _('Address Line 1'),
            'address_line2': _('Address Line 2'),
            'city': _('City'),
            'department': _('Department'),
            'postal_code': _('Postal Code'),
            'phone': _('Phone Number'),
            'is_default': _('Set as default address')
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            try:
                validate_haitian_phone_number(phone)
            except ValidationError as e:
                raise forms.ValidationError(e.message)
        return phone