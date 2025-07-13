# ======================================
# config/settings.py - Configuration Django complète pour Railway
# ======================================

import os
import dj_database_url
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================================
# SECURITY SETTINGS
# ===========================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-development-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.railway.app',
    'afepanou.com',
    'www.afepanou.com',
    '.vercel.app',
    '.netlify.app'
]

# ===========================================
# APPLICATION DEFINITION
# ===========================================

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'storages',
]

LOCAL_APPS = [
    'core',
    'users',
    'products',
    'orders',
    'payments',
    'content',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ===========================================
# MIDDLEWARE CONFIGURATION
# ===========================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ===========================================
# TEMPLATES CONFIGURATION
# ===========================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ===========================================
# DATABASE CONFIGURATION (RAILWAY POSTGRESQL)
# ===========================================

# Configuration automatique via DATABASE_URL (Railway)
DATABASES = {
    'default': dj_database_url.parse(
        os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ===========================================
# CACHE CONFIGURATION (RAILWAY REDIS)
# ===========================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': 'afepanou',
        'TIMEOUT': 300,  # 5 minutes par défaut
    }
}

# Configuration du cache de sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ===========================================
# AUTHENTIFICATION & PERMISSIONS
# ===========================================

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ===========================================
# REST FRAMEWORK CONFIGURATION
# ===========================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': int(os.getenv('DEFAULT_PAGE_SIZE', 20)),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}

# ===========================================
# JWT CONFIGURATION
# ===========================================

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME', 60))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME', 7))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.getenv('JWT_SECRET_KEY', SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ===========================================
# CORS CONFIGURATION
# ===========================================

# CORS pour Next.js frontend
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://afepanou.com",
    "https://www.afepanou.com",
] + [origin.strip() for origin in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_ALL_ORIGINS = False  # Toujours sécurisé

# ===========================================
# INTERNATIONALIZATION
# ===========================================

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'fr-ht')
TIME_ZONE = os.getenv('TIME_ZONE', 'America/Port-au-Prince')
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ===========================================
# STATIC FILES CONFIGURATION
# ===========================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Configuration WhiteNoise pour servir les fichiers statiques
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ===========================================
# MEDIA FILES & BACKBLAZE B2 CONFIGURATION
# ===========================================

# Configuration Backblaze B2
AWS_ACCESS_KEY_ID = os.getenv('B2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('B2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('B2_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('B2_ENDPOINT_URL')
AWS_S3_REGION_NAME = os.getenv('B2_REGION_NAME', 'us-west-001')

# Configuration S3/B2
AWS_DEFAULT_ACL = None
AWS_BUCKET_ACL = None
AWS_QUERYSTRING_AUTH = False  # URLs publiques
AWS_S3_FILE_OVERWRITE = False
AWS_LOCATION = 'media'
AWS_S3_SIGNATURE_VERSION = 's3v4'

# Configuration URL publique
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.backblazeb2.com'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'

# Configuration des storages - Utiliser Backblaze B2
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "access_key": AWS_ACCESS_KEY_ID,
            "secret_key": AWS_SECRET_ACCESS_KEY,
            "file_overwrite": AWS_S3_FILE_OVERWRITE,
            "default_acl": AWS_DEFAULT_ACL,
            "location": AWS_LOCATION,
            "querystring_auth": AWS_QUERYSTRING_AUTH,
        }
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}

# ===========================================
# EMAIL CONFIGURATION
# ===========================================

# Configuration SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Emails par défaut
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@afepanou.com')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'admin@afepanou.com')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@afepanou.com')

# ===========================================
# MONCASH CONFIGURATION
# ===========================================

# Configuration MonCash
MONCASH_CLIENT_ID = os.getenv('MONCASH_CLIENT_ID', '')
MONCASH_SECRET_KEY = os.getenv('MONCASH_SECRET_KEY', '')
MONCASH_MODE = os.getenv('MONCASH_MODE', 'sandbox')  # 'sandbox' ou 'live'

# URLs MonCash
if MONCASH_MODE == 'sandbox':
    MONCASH_API_BASE = 'https://sandbox.moncashbutton.digicelgroup.com/Api'
    MONCASH_GATEWAY_BASE = 'https://sandbox.moncashbutton.digicelgroup.com/Moncash-middleware'
else:
    MONCASH_API_BASE = 'https://moncashbutton.digicelgroup.com/Api'
    MONCASH_GATEWAY_BASE = 'https://moncashbutton.digicelgroup.com/Moncash-middleware'

# ===========================================
# BUSINESS CONFIGURATION
# ===========================================

# Configuration du site
SITE_NAME = os.getenv('SITE_NAME', 'Afèpanou')
SITE_TAGLINE = os.getenv('SITE_TAGLINE', 'Marketplace Haïtien')
SITE_URL = os.getenv('SITE_URL', 'https://afepanou.com')
CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', 'contact@afepanou.com')
SUPPORT_PHONE = os.getenv('SUPPORT_PHONE', '+509 1234-5678')

# Configuration commerce
DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'HTG')
CURRENCY_SYMBOL = os.getenv('CURRENCY_SYMBOL', 'HTG')
DEFAULT_TAX_RATE = float(os.getenv('DEFAULT_TAX_RATE', '0.0'))
DEFAULT_SHIPPING_COST = float(os.getenv('DEFAULT_SHIPPING_COST', '0.0'))

# Configuration cache timeouts
CACHE_TIMEOUT_PRODUCTS = int(os.getenv('CACHE_TIMEOUT_PRODUCTS', 900))      # 15 minutes
CACHE_TIMEOUT_CATEGORIES = int(os.getenv('CACHE_TIMEOUT_CATEGORIES', 3600)) # 1 heure  
CACHE_TIMEOUT_BANNERS = int(os.getenv('CACHE_TIMEOUT_BANNERS', 1800))       # 30 minutes
CACHE_TIMEOUT_SETTINGS = int(os.getenv('CACHE_TIMEOUT_SETTINGS', 86400))    # 24 heures

# Configuration pagination
DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', 20))
MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', 100))

# ===========================================
# SECURITY CONFIGURATION
# ===========================================

# Configuration HTTPS - Toujours activée
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Configuration des cookies sécurisés
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Configuration des sessions
SESSION_COOKIE_AGE = 86400  # 24 heures
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ===========================================
# LOGGING CONFIGURATION
# ===========================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'afepanou.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.payments': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.orders': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Créer le dossier logs s'il n'existe pas
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ===========================================
# RAILWAY SPECIFIC CONFIGURATION
# ===========================================

# Port pour Railway
PORT = int(os.getenv('PORT', 8000))

# Configuration Railway - Toujours en mode production
DEBUG = False
ALLOWED_HOSTS.append('.railway.app')

# Forcer HTTPS
SECURE_SSL_REDIRECT = True

# Logs pour Railway
LOGGING['handlers']['console']['level'] = 'INFO'

# ===========================================
# ADDITIONAL SETTINGS
# ===========================================

# Configuration file uploads
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuration admin
ADMIN_URL = os.getenv('ADMIN_URL', 'admin/')

