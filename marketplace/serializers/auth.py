from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from marketplace.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les informations utilisateur"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'phone', 'address', 'city', 'country',
            'is_seller', 'profile_image', 'birth_date', 'gender',
            'email_verified', 'date_joined', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'updated_at', 'email_verified']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription utilisateur"""
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'address', 
            'city', 'country', 'is_seller', 'birth_date', 'gender'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'city': {'default': 'Port-au-Prince'},
            'country': {'default': 'Haïti'},
        }
    
    def validate(self, attrs):
        """Validation des mots de passe"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password_confirm": "Les mots de passe ne correspondent pas."}
            )
        return attrs
    
    def validate_email(self, value):
        """Validation unicité email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Un utilisateur avec cet email existe déjà."
            )
        return value
    
    def validate_username(self, value):
        """Validation unicité username"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Ce nom d'utilisateur est déjà pris."
            )
        return value
    
    def create(self, validated_data):
        """Création utilisateur avec mot de passe hashé"""
        # Supprimer password_confirm des données
        validated_data.pop('password_confirm', None)
        
        # Créer l'utilisateur
        user = User.objects.create_user(**validated_data)
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personnalisé pour JWT avec infos utilisateur"""
    
    def validate(self, attrs):
        # Authentification de base
        data = super().validate(attrs)
        
        # Ajouter les infos utilisateur au token
        user_data = UserSerializer(self.user).data
        data['user'] = user_data
        
        return data


class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Permettre connexion avec email ou username
            if '@' in username:
                # Connexion avec email
                try:
                    user_obj = User.objects.get(email=username)
                    username = user_obj.username
                except User.DoesNotExist:
                    pass
            
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Identifiants invalides. Veuillez réessayer.'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'Ce compte est désactivé.'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Le nom d\'utilisateur et le mot de passe sont requis.'
            )


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour du profil"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'address', 
            'city', 'country', 'profile_image', 'birth_date', 'gender'
        ]
    
    def validate_phone(self, value):
        """Validation format téléphone haïtien"""
        if value and not value.startswith(('+509', '509')):
            # Format automatique si ce n'est que des chiffres
            if value.isdigit() and len(value) == 8:
                value = f'+509 {value[:4]}-{value[4:]}'
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changement de mot de passe"""
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        """Validation ancien mot de passe"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'L\'ancien mot de passe est incorrect.'
            )
        return value
    
    def validate(self, attrs):
        """Validation nouveaux mots de passe"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {"new_password_confirm": "Les nouveaux mots de passe ne correspondent pas."}
            )
        return attrs
    
    def save(self):
        """Mise à jour du mot de passe"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user