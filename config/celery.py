# config/celery.py

import os
import logging
from celery import Celery
from django.conf import settings

# 🔧 CONFIGURATION ENVIRONNEMENT
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 🎯 CRÉATION INSTANCE CELERY
app = Celery('afepanou_api')

# 🔧 CONFIGURATION CELERY DEPUIS DJANGO SETTINGS
app.config_from_object('django.conf:settings', namespace='CELERY')

# 🔍 AUTO-DISCOVERY DES TÂCHES DANS TOUTES LES APPS
app.autodiscover_tasks()

# 📊 LOGGING CELERY
logger = logging.getLogger(__name__)

@app.task(bind=True)
def debug_task(self):
    """Tâche de debug pour tester Celery"""
    print(f'Request: {self.request!r}')
    logger.info('Celery debug task executed successfully')
    return 'Debug task completed'

# 🚨 CONFIGURATION AVANCÉE CELERY
app.conf.update(
    # 🎯 BROKER & BACKEND CONFIGURATION
    broker_url=os.getenv('REDIS_URL'),
    result_backend=os.getenv('REDIS_URL'),
    
    # ⚡ PERFORMANCE SETTINGS
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Port-au-Prince',
    enable_utc=True,
    
    # 🚨 SÉCURITÉ & LIMITE RESSOURCES
    task_soft_time_limit=300,         # 5 minutes soft limit
    task_time_limit=600,              # 10 minutes hard limit
    worker_max_tasks_per_child=50,    # Redémarre worker après 50 tâches
    worker_max_memory_per_child=200000,  # 200MB limite mémoire
    
    # 🔄 RETRY CONFIGURATION
    task_default_retry_delay=60,      # 60 secondes entre retries
    task_max_retries=3,               # Maximum 3 retries global
    
    # 📈 MONITORING & EVENTS
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # 🚀 OPTIMISATION CONCURRENCE
    worker_prefetch_multiplier=4,     # Optimisation pour I/O bound tasks
    task_compression='gzip',          # Compression messages
    result_compression='gzip',
    
    # 🎯 ROUTES & QUEUES SPÉCIALISÉES
    task_routes={
        # 💳 QUEUE PAIEMENTS (PRIORITÉ HAUTE)
        'marketplace.tasks.payment_tasks.process_payment_webhook': {
            'queue': 'payments_high_priority',
            'routing_key': 'payments.webhook',
        },
        
        # 🧹 QUEUE MAINTENANCE (PRIORITÉ BASSE)
        'marketplace.tasks.payment_tasks.cleanup_expired_carts': {
            'queue': 'maintenance_low_priority',
            'routing_key': 'maintenance.cleanup',
        },
        
        # 📊 QUEUE MONITORING (PRIORITÉ MOYENNE)
        'marketplace.tasks.payment_tasks.monitor_stuck_payments': {
            'queue': 'monitoring_medium_priority',
            'routing_key': 'monitoring.payments',
        },
        
        # 📧 QUEUE EMAILS (PRIORITÉ MOYENNE)
        'marketplace.tasks.*email*': {
            'queue': 'emails_medium_priority',
            'routing_key': 'emails.notifications',
        },
        
        # 🔄 QUEUE DEFAULT (PRIORITÉ NORMALE)
        '*': {
            'queue': 'default',
            'routing_key': 'default',
        }
    },
    
    # 🕐 CONFIGURATION BEAT (TÂCHES PÉRIODIQUES)
    beat_schedule={
        # 🧹 NETTOYAGE PANIERS EXPIRÉS (toutes les 30 minutes)
        'cleanup-expired-carts': {
            'task': 'marketplace.tasks.payment_tasks.cleanup_expired_carts',
            'schedule': 1800.0,  # 30 minutes
            'options': {
                'queue': 'maintenance_low_priority',
                'expires': 1200,  # Expire après 20 min si pas exécutée
            }
        },
        
        # 📊 MONITORING PAIEMENTS BLOQUÉS (toutes les 15 minutes)
        'monitor-stuck-payments': {
            'task': 'marketplace.tasks.payment_tasks.monitor_stuck_payments',
            'schedule': 900.0,  # 15 minutes
            'options': {
                'queue': 'monitoring_medium_priority',
                'expires': 600,  # Expire après 10 min
            }
        },
        
        # 🔍 HEALTH CHECK CELERY (toutes les 5 minutes)
        'celery-health-check': {
            'task': 'config.celery.debug_task',
            'schedule': 300.0,  # 5 minutes
            'options': {
                'queue': 'default',
                'expires': 120,  # Expire après 2 min
            }
        },
    },
)

# 🎯 CONFIGURATION QUEUES AVANCÉE
app.conf.task_create_missing_queues = True
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'afepanou'
app.conf.task_default_exchange_type = 'direct'

# 📊 LOGGING CONFIGURATION CELERY
@app.task(bind=True)
def log_celery_startup(self):
    """Log du démarrage Celery avec infos système"""
    logger.info("🚀 Celery Worker Started for Afèpanou Marketplace")
    logger.info(f"📊 Broker: {app.conf.broker_url[:50]}...")
    logger.info(f"🎯 Queues configured: payments, maintenance, monitoring, emails, default")
    logger.info(f"⏰ Beat scheduler: {'ENABLED' if app.conf.beat_schedule else 'DISABLED'}")
    return "Celery startup logged successfully"

# 🔧 SIGNAL HANDLERS POUR MONITORING
from celery.signals import worker_ready, worker_shutdown, task_failure

@worker_ready.connect
def worker_ready_handler(sender=None, **kwargs):
    """Signal quand worker est prêt"""
    logger.info(f"🟢 Celery Worker Ready: {sender}")

@worker_shutdown.connect  
def worker_shutdown_handler(sender=None, **kwargs):
    """Signal quand worker s'arrête"""
    logger.info(f"🔴 Celery Worker Shutdown: {sender}")

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwargs):
    """Signal en cas d'échec de tâche"""
    logger.error(f"❌ Task Failed: {sender} (ID: {task_id}) - {exception}")

# 🎯 EXPORT POUR DJANGO
__all__ = ['app']