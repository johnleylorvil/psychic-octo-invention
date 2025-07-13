# ======================================
# apps/core/serializers.py
# ======================================

from rest_framework import serializers
from .models import SiteSetting, NewsletterSubscriber


class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = ['setting_key', 'setting_value', 'setting_type', 'group_name']
        
    def to_representation(self, instance):
        """Transforme les données selon le type"""
        data = super().to_representation(instance)
        
        # Convertir selon le type
        if instance.setting_type == 'boolean':
            data['setting_value'] = instance.setting_value.lower() in ['true', '1', 'yes']
        elif instance.setting_type == 'number':
            try:
                data['setting_value'] = float(instance.setting_value)
            except (ValueError, TypeError):
                data['setting_value'] = 0
        
        return data


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email', 'first_name', 'last_name', 'source']
        
    def validate_email(self, value):
        """Valide l'email"""
        if NewsletterSubscriber.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("Cet email est déjà abonné.")
        return value


class NewsletterUnsubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Vérifie que l'email existe"""
        if not NewsletterSubscriber.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("Cet email n'est pas abonné.")
        return value
