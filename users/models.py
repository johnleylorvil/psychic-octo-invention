from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50, blank=True, default='Port-au-Prince')
    country = models.CharField(max_length=50, blank=True, default='Haïti')
    is_seller = models.BooleanField(null=True, blank=True, default=False)
    email_verified = models.BooleanField(null=True, blank=True, default=False)
    profile_image = models.CharField(max_length=255, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username
