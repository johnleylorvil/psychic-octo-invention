# config/__init__.py

# 🚀 AUTO-CHARGEMENT CELERY AU DÉMARRAGE DJANGO
from .celery import app as celery_app

# 🎯 EXPORT CELERY POUR ACCÈS GLOBAL
__all__ = ('celery_app',)

# 📊 LOGGING DÉMARRAGE
import logging
logger = logging.getLogger(__name__)
logger.info("🚀 Django + Celery Integration Loaded Successfully")