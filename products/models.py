from django.db import models


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    detailed_description = models.TextField(null=True, blank=True)
    folder_path = models.CharField(max_length=255, blank=True)
    banner_image = models.CharField(max_length=255, blank=True)
    banner_image_path = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(null=True, blank=True, default=False)
    is_active = models.BooleanField(null=True, blank=True, default=True)
    sort_order = models.IntegerField(null=True, blank=True, default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('Categorie', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    short_description = models.CharField(max_length=500, blank=True)
    description = models.TextField(null=True, blank=True)
    detailed_description = models.TextField(null=True, blank=True)
    specifications = models.JSONField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.IntegerField(null=True, blank=True, default=0)
    min_stock_alert = models.IntegerField(null=True, blank=True, default=5)
    sku = models.CharField(max_length=50, blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    is_featured = models.BooleanField(null=True, blank=True, default=False)
    is_active = models.BooleanField(null=True, blank=True, default=True)
    is_digital = models.BooleanField(null=True, blank=True, default=False)
    requires_shipping = models.BooleanField(null=True, blank=True, default=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)
    tags = models.TextField(null=True, blank=True)
    video_url = models.CharField(max_length=255, blank=True)
    warranty_period = models.IntegerField(null=True, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=100, blank=True)
    origin_country = models.CharField(max_length=50, blank=True, default='Haïti')
    condition_type = models.CharField(max_length=20, blank=True, default='new')
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey('Categorie', on_delete=models.CASCADE)
    seller = models.ForeignKey('users.User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    id = models.AutoField(primary_key=True)
    image_url = models.CharField(max_length=255)
    image_path = models.CharField(max_length=255)
    alt_text = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(null=True, blank=True, default=False)
    sort_order = models.IntegerField(null=True, blank=True, default=0)
    image_type = models.CharField(max_length=20, blank=True, default='gallery')
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_images'

    def __str__(self):
        return self.title


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    customer_email = models.CharField(max_length=100, blank=True)
    rating = models.IntegerField()
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(null=True, blank=True)
    pros = models.TextField(null=True, blank=True)
    cons = models.TextField(null=True, blank=True)
    is_verified_purchase = models.BooleanField(null=True, blank=True, default=False)
    is_approved = models.BooleanField(null=True, blank=True, default=False)
    helpful_count = models.IntegerField(null=True, blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'reviews'

    def __str__(self):
        return self.title

