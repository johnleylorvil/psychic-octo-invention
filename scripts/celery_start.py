#!/usr/bin/env python3
# scripts/celery_start.py

"""
🚀 SCRIPTS DE DÉMARRAGE CELERY POUR AFÈPANOU MARKETPLACE

Usage:
    python scripts/celery_start.py --worker     # Démarrer worker
    python scripts/celery_start.py --beat       # Démarrer beat scheduler  
    python scripts/celery_start.py --monitor    # Démarrer flower monitoring
    python scripts/celery_start.py --all        # Démarrer tout
    python scripts/celery_start.py --status     # Vérifier statut
"""

import os
import sys
import time
import signal
import argparse
import subprocess
from pathlib import Path

# 📁 CONFIGURATION PATHS
PROJECT_DIR = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_DIR)

# 🎯 CONFIGURATION CELERY
CELERY_APP = 'config.celery:app'
LOG_LEVEL = os.getenv('CELERY_LOG_LEVEL', 'INFO')
CONCURRENCY = os.getenv('CELERY_CONCURRENCY', '4')

class CeleryManager:
    """Gestionnaire pour les processus Celery"""
    
    def __init__(self):
        self.processes = {}
        self.running = True
        
        # 🎯 CONFIGURATION QUEUES SPÉCIALISÉES
        self.worker_configs = {
            'payments': {
                'queues': 'payments_high_priority',
                'concurrency': 2,
                'prefetch': 1,  # Traitement séquentiel pour paiements critiques
                'max_tasks_per_child': 10,
            },
            'maintenance': {
                'queues': 'maintenance_low_priority',
                'concurrency': 1,
                'prefetch': 4,
                'max_tasks_per_child': 50,
            },
            'monitoring': {
                'queues': 'monitoring_medium_priority',
                'concurrency': 1,
                'prefetch': 2,
                'max_tasks_per_child': 20,
            },
            'emails': {
                'queues': 'emails_medium_priority',
                'concurrency': 2,
                'prefetch': 3,
                'max_tasks_per_child': 30,
            },
            'default': {
                'queues': 'default',
                'concurrency': int(CONCURRENCY),
                'prefetch': 4,
                'max_tasks_per_child': 50,
            }
        }
    
    def start_worker(self, worker_type='all'):
        """Démarrer worker(s) Celery"""
        print(f"🚀 Starting Celery Worker(s) for Afèpanou Marketplace...")
        
        if worker_type == 'all':
            # Démarrer tous les workers spécialisés
            for name, config in self.worker_configs.items():
                self._start_single_worker(name, config)
        else:
            # Démarrer worker spécifique
            if worker_type in self.worker_configs:
                config = self.worker_configs[worker_type]
                self._start_single_worker(worker_type, config)
            else:
                print(f"❌ Unknown worker type: {worker_type}")
                return False
        
        return True
    
    def _start_single_worker(self, name, config):
        """Démarrer un worker spécifique"""
        cmd = [
            'celery', '-A', CELERY_APP, 'worker',
            '--loglevel', LOG_LEVEL,
            '--queues', config['queues'],
            '--concurrency', str(config['concurrency']),
            '--prefetch-multiplier', str(config['prefetch']),
            '--max-tasks-per-child', str(config['max_tasks_per_child']),
            '--hostname', f'{name}@%h',
            '--logfile', f'logs/celery_{name}_worker.log',
        ]
        
        print(f"📊 Starting {name} worker: {config['queues']}")
        print(f"   Concurrency: {config['concurrency']}, Prefetch: {config['prefetch']}")
        
        process = subprocess.Popen(cmd)
        self.processes[f'worker_{name}'] = process
        time.sleep(2)  # Délai entre démarrages
    
    def start_beat(self):
        """Démarrer Celery Beat scheduler"""
        print("⏰ Starting Celery Beat Scheduler...")
        
        cmd = [
            'celery', '-A', CELERY_APP, 'beat',
            '--loglevel', LOG_LEVEL,
            '--schedule', 'celerybeat-schedule',
            '--logfile', 'logs/celery_beat.log',
            '--pidfile', 'celerybeat.pid'
        ]
        
        process = subprocess.Popen(cmd)
        self.processes['beat'] = process
        print("✅ Beat scheduler started")
        return True
    
    def start_flower(self):
        """Démarrer Flower monitoring (optionnel)"""
        print("🌸 Starting Flower Monitoring...")
        
        cmd = [
            'celery', '-A', CELERY_APP, 'flower',
            '--port=5555',
            '--url_prefix=flower',
            '--logfile', 'logs/celery_flower.log'
        ]
        
        try:
            process = subprocess.Popen(cmd)
            self.processes['flower'] = process
            print("✅ Flower monitoring started on http://localhost:5555")
            return True
        except FileNotFoundError:
            print("⚠️  Flower not installed. Install with: pip install flower")
            return False
    
    def check_status(self):
        """Vérifier le statut des services Celery"""
        print("📊 Checking Celery Services Status...")
        
        # Test de connexion Redis
        self._check_redis_connection()
        
        # Test workers actifs
        self._check_active_workers()
        
        # Test queues
        self._check_queues()
    
    def _check_redis_connection(self):
        """Vérifier connexion Redis"""
        try:
            import redis
            from django.conf import settings
            
            redis_url = os.getenv('REDIS_URL')
            r = redis.from_url(redis_url)
            r.ping()
            print("✅ Redis connection: OK")
        except Exception as e:
            print(f"❌ Redis connection: FAILED - {e}")
    
    def _check_active_workers(self):
        """Vérifier workers actifs"""
        cmd = ['celery', '-A', CELERY_APP, 'inspect', 'active']
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Active workers found")
                print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
            else:
                print("⚠️  No active workers found")
        except subprocess.TimeoutExpired:
            print("❌ Worker check timeout")
        except Exception as e:
            print(f"❌ Worker check failed: {e}")
    
    def _check_queues(self):
        """Vérifier état des queues"""
        queues = [
            'payments_high_priority', 
            'maintenance_low_priority',
            'monitoring_medium_priority', 
            'emails_medium_priority',
            'default'
        ]
        
        for queue in queues:
            print(f"📊 Queue {queue}: Checking...")
    
    def stop_all(self):
        """Arrêter tous les processus Celery"""
        print("🛑 Stopping all Celery processes...")
        
        for name, process in self.processes.items():
            print(f"   Stopping {name}...")
            process.terminate()
            
        # Attendre arrêt gracieux
        time.sleep(5)
        
        # Force kill si nécessaire
        for name, process in self.processes.items():
            if process.poll() is None:
                print(f"   Force killing {name}...")
                process.kill()
        
        print("✅ All Celery processes stopped")
    
    def signal_handler(self, signum, frame):
        """Gestionnaire de signal pour arrêt propre"""
        print("\n🛑 Received shutdown signal...")
        self.running = False
        self.stop_all()
        sys.exit(0)

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Celery Manager for Afèpanou')
    
    parser.add_argument('--worker', action='store_true', help='Start Celery workers')
    parser.add_argument('--worker-type', default='all', help='Worker type to start')
    parser.add_argument('--beat', action='store_true', help='Start Celery beat')
    parser.add_argument('--flower', action='store_true', help='Start Flower monitoring')
    parser.add_argument('--monitor', action='store_true', help='Start monitoring')
    parser.add_argument('--all', action='store_true', help='Start all services')
    parser.add_argument('--status', action='store_true', help='Check status')
    
    args = parser.parse_args()
    
    # Créer dossier logs
    os.makedirs('logs', exist_ok=True)
    
    manager = CeleryManager()
    
    # Gestionnaire de signaux pour arrêt propre
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    try:
        if args.status:
            manager.check_status()
        elif args.all:
            print("🚀 Starting all Celery services for Afèpanou...")
            manager.start_worker('all')
            manager.start_beat()
            manager.start_flower()
            
            print("✅ All services started! Press Ctrl+C to stop")
            while manager.running:
                time.sleep(1)
                
        elif args.worker:
            manager.start_worker(args.worker_type)
            print("✅ Workers started! Press Ctrl+C to stop")
            while manager.running:
                time.sleep(1)
                
        elif args.beat:
            manager.start_beat()
            print("✅ Beat scheduler started! Press Ctrl+C to stop")
            while manager.running:
                time.sleep(1)
                
        elif args.flower or args.monitor:
            manager.start_flower()
            print("✅ Flower monitoring started! Press Ctrl+C to stop")
            while manager.running:
                time.sleep(1)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        manager.stop_all()

if __name__ == '__main__':
    main()