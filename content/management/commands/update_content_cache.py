# ======================================
# apps/content/management/commands/update_content_cache.py
# ======================================

from django.core.management.base import BaseCommand
from apps.content.utils import invalidate_content_cache


class Command(BaseCommand):
    help = 'Met à jour le cache du contenu'
    
    def handle(self, *args, **options):
        self.stdout.write('Invalidation du cache de contenu...')
        
        invalidate_content_cache()
        
        self.stdout.write(
            self.style.SUCCESS('Cache de contenu invalidé avec succès!')
        )