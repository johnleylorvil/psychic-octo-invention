# marketplace/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum
from django.utils import timezone
from .models import *

# ============= CONFIGURATION GÉNÉRALE ADMIN =============
admin.site.site_header = "🏪 Administration Afèpanou Marketplace"
admin.site.site_title = "Afèpanou Admin"
admin.site.index_title = "Tableau de bord du Marketplace Haïtien"

