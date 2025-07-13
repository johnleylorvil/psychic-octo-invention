from django.db import models


class SiteSetting(models.Model):
    id = models.AutoField(primary_key=True)
    setting_key = models.CharField(max_length=100)
    setting_value = models.TextField(null=True, blank=True)
    setting_type = models.CharField(max_length=10, blank=True, default='text')
    description = models.TextField(null=True, blank=True)
    group_name = models.CharField(max_length=50, blank=True, default='general')
    is_public = models.BooleanField(null=True, blank=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'site_settings'

    def __str__(self):
        return f'SiteSetting {self.id}'


class NewsletterSubscriber(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(null=True, blank=True, default=True)
    subscribed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=50, blank=True, default='website')

    class Meta:
        db_table = 'newsletter_subscribers'

    def __str__(self):
        return self.email

