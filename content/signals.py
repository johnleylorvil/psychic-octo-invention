# ======================================
# apps/content/signals.py
# ======================================

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Banner, Page, MediaContentSection
from .utils import invalidate_content_cache


@receiver([post_save, post_delete], sender=Banner)
@receiver([post_save, post_delete], sender=Page)
@receiver([post_save, post_delete], sender=MediaContentSection)
def invalidate_cache_on_content_change(sender, **kwargs):
    """Invalide le cache quand le contenu change"""
    invalidate_content_cache()
