# marketplace/management/commands/celery_worker.py

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys
import subprocess

class Command(BaseCommand):
    """
    Commande Django pour démarrer Celery Worker
    
    Usage:
        python manage.py celery_worker
        python manage.py celery_worker --queue=payments
        python manage.py celery_worker --concurrency=2
    """
    help = 'Start Celery Worker for Afèpanou Marketplace'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--queue',
            type=str,
            default='default',
            help='Queue name to process (default: default)'
        )
        parser.add_argument(
            '--concurrency',
            type=int,
            default=4,
            help='Number of concurrent worker processes (default: 4)'
        )
        parser.add_argument(
            '--loglevel',
            type=str,
            default='INFO',
            help='Logging level (default: INFO)'
        )
        parser.add_argument(
            '--hostname',
            type=str,
            help='Custom hostname for worker'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Celery Worker for Afèpanou...')
        )
        
        # Configuration worker
        queue = options['queue']
        concurrency = options['concurrency']
        loglevel = options['loglevel']
        hostname = options.get('hostname')
        
        # Commande Celery
        cmd = [
            'celery', '-A', 'config.celery:app', 'worker',
            '--loglevel', loglevel,
            '--queues', queue,
            '--concurrency', str(concurrency),
        ]
        
        if hostname:
            cmd.extend(['--hostname', hostname])
        
        self.stdout.write(f"📊 Queue: {queue}")
        self.stdout.write(f"🔄 Concurrency: {concurrency}")
        self.stdout.write(f"📝 Log Level: {loglevel}")
        
        try:
            # Exécuter Celery worker
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n🛑 Worker stopped by user')
            )
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Worker failed: {e}')
            )

# ==============================================

# marketplace/management/commands/celery_beat.py

from django.core.management.base import BaseCommand
import subprocess

class Command(BaseCommand):
    """
    Commande Django pour démarrer Celery Beat
    
    Usage:
        python manage.py celery_beat
        python manage.py celery_beat --loglevel=DEBUG
    """
    help = 'Start Celery Beat Scheduler for Afèpanou Marketplace'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--loglevel',
            type=str,
            default='INFO',
            help='Logging level (default: INFO)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('⏰ Starting Celery Beat Scheduler...')
        )
        
        loglevel = options['loglevel']
        
        cmd = [
            'celery', '-A', 'config.celery:app', 'beat',
            '--loglevel', loglevel,
            '--schedule', 'celerybeat-schedule',
        ]
        
        self.stdout.write(f"📝 Log Level: {loglevel}")
        self.stdout.write("📅 Periodic tasks will be executed according to schedule")
        
        try:
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n🛑 Beat scheduler stopped by user')
            )
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Beat scheduler failed: {e}')
            )

# ==============================================

# marketplace/management/commands/celery_status.py

from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import redis
import json

class Command(BaseCommand):
    """
    Commande Django pour vérifier le statut Celery
    
    Usage:
        python manage.py celery_status
        python manage.py celery_status --detailed
    """
    help = 'Check Celery status for Afèpanou Marketplace'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('📊 Checking Celery Status for Afèpanou...')
        )
        
        detailed = options['detailed']
        
        # 1. Vérifier connexion Redis
        self.check_redis_connection()
        
        # 2. Vérifier workers actifs
        self.check_active_workers(detailed)
        
        # 3. Vérifier queues
        self.check_queues(detailed)
        
        # 4. Vérifier tâches en cours
        if detailed:
            self.check_running_tasks()
    
    def check_redis_connection(self):
        """Vérifier connexion Redis"""
        try:
            redis_url = settings.CELERY_BROKER_URL
            r = redis.from_url(redis_url)
            r.ping()
            self.stdout.write("✅ Redis Connection: OK")
            
            # Info Redis
            info = r.info()
            self.stdout.write(f"   📊 Redis Version: {info.get('redis_version')}")
            self.stdout.write(f"   💾 Used Memory: {info.get('used_memory_human')}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Redis Connection: FAILED - {e}")
            )
    
    def check_active_workers(self, detailed=False):
        """Vérifier workers actifs"""
        try:
            cmd = ['celery', '-A', 'config.celery:app', 'inspect', 'active']
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                self.stdout.write("✅ Active Workers: Found")
                if detailed:
                    self.stdout.write(result.stdout)
            else:
                self.stdout.write("⚠️  Active Workers: None found")
                
        except subprocess.TimeoutExpired:
            self.stdout.write(
                self.style.ERROR("❌ Worker Check: Timeout")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Worker Check: Failed - {e}")
            )
    
    def check_queues(self, detailed=False):
        """Vérifier état des queues"""
        queues = [
            'payments_high_priority',
            'maintenance_low_priority', 
            'monitoring_medium_priority',
            'emails_medium_priority',
            'default'
        ]
        
        self.stdout.write("📊 Queue Status:")
        
        for queue in queues:
            try:
                cmd = [
                    'celery', '-A', 'config.celery:app', 
                    'inspect', 'reserved', '-d', f'celery@{queue}'
                ]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=5
                )
                
                if result.returncode == 0:
                    status = "✅ Active" if result.stdout.strip() else "💤 Idle"
                else:
                    status = "❌ Unavailable"
                    
                self.stdout.write(f"   {queue}: {status}")
                
            except:
                self.stdout.write(f"   {queue}: ❓ Unknown")
    
    def check_running_tasks(self):
        """Vérifier tâches en cours d'exécution"""
        try:
            cmd = ['celery', '-A', 'config.celery:app', 'inspect', 'active']
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                self.stdout.write("🔄 Running Tasks:")
                self.stdout.write(result.stdout)
            else:
                self.stdout.write("🔄 Running Tasks: None")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Task Check Failed: {e}")
            )

# ==============================================

# marketplace/management/commands/celery_purge.py

from django.core.management.base import BaseCommand
import subprocess

class Command(BaseCommand):
    """
    Commande Django pour purger les queues Celery
    
    Usage:
        python manage.py celery_purge
        python manage.py celery_purge --queue=payments_high_priority
    """
    help = 'Purge Celery queues for Afèpanou Marketplace'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--queue',
            type=str,
            help='Specific queue to purge (purges all if not specified)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force purge without confirmation'
        )
    
    def handle(self, *args, **options):
        queue = options.get('queue')
        force = options['force']
        
        if queue:
            message = f"⚠️  Purging queue: {queue}"
        else:
            message = "⚠️  Purging ALL queues"
        
        self.stdout.write(self.style.WARNING(message))
        
        if not force:
            confirm = input("Are you sure? This will delete all pending tasks! (y/N): ")
            if confirm.lower() != 'y':
                self.stdout.write("❌ Purge cancelled")
                return
        
        try:
            cmd = ['celery', '-A', 'config.celery:app', 'purge']
            if queue:
                cmd.extend(['-Q', queue])
            
            if force:
                cmd.append('-f')
            
            result = subprocess.run(cmd, check=True)
            self.stdout.write(
                self.style.SUCCESS('✅ Queues purged successfully')
            )
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Purge failed: {e}')
            )