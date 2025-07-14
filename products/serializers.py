# ======================================
# apps/products/serializers.py
# ======================================

from rest_framework import serializers
from django.db.models import Avg, Count
from .models import Category, Product, ProductImage, Review


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'banner_image', 
            'icon', 'is_featured', 'products_count'
        ]
    
    def get_products_count(self, obj):
        return obj.product_set.filter(is_active=True).count()


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'title', 'is_primary', 'sort_order']


class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'customer_name', 'rating', 'title', 'comment', 
            'pros', 'cons', 'is_verified_purchase', 'created_at'
        ]
        read_only_fields = ['is_verified_purchase', 'created_at']


# Serializer simple pour les relations (utilisé dans orders/serializers.py)
class ProductSerializer(serializers.ModelSerializer):
    """Serializer simple pour les relations avec d'autres apps"""
    primary_image = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'promotional_price', 
            'final_price', 'primary_image', 'stock_quantity'
        ]
    
    def get_primary_image(self, obj):
        primary_image = obj.productimage_set.filter(is_primary=True).first()
        if primary_image:
            return {
                'id': primary_image.id,
                'image_url': primary_image.image_url,
                'alt_text': primary_image.alt_text
            }
        return None
    
    def get_final_price(self, obj):
        return obj.promotional_price or obj.price


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'category',
            'price', 'promotional_price', 'final_price', 'primary_image',
            'rating', 'reviews_count', 'is_featured', 'stock_quantity'
        ]
    
    def get_primary_image(self, obj):
        primary_image = obj.productimage_set.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None
    
    def get_final_price(self, obj):
        return obj.promotional_price or obj.price
    
    def get_rating(self, obj):
        avg_rating = obj.review_set.filter(is_approved=True).aggregate(
            avg=Avg('rating')
        )['avg']
        return round(avg_rating, 1) if avg_rating else 0
    
    def get_reviews_count(self, obj):
        return obj.review_set.filter(is_approved=True).count()


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(source='productimage_set', many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    final_price = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'description', 
            'detailed_description', 'specifications', 'category', 'seller_name',
            'price', 'promotional_price', 'final_price', 'stock_quantity',
            'brand', 'model', 'color', 'material', 'weight', 'dimensions',
            'origin_country', 'condition_type', 'warranty_period',
            'images', 'reviews', 'rating', 'reviews_count', 'tags',
            'video_url', 'created_at'
        ]
    
    def get_final_price(self, obj):
        return obj.promotional_price or obj.price
    
    def get_rating(self, obj):
        avg_rating = obj.review_set.filter(is_approved=True).aggregate(
            avg=Avg('rating')
        )['avg']
        return round(avg_rating, 1) if avg_rating else 0
    
    def get_reviews_count(self, obj):
        return obj.review_set.filter(is_approved=True).count()
    
    def get_reviews(self, obj):
        reviews = obj.review_set.filter(is_approved=True).order_by('-created_at')[:5]
        return ReviewSerializer(reviews, many=True).data


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'pros', 'cons']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return value