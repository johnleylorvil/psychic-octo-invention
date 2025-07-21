#!/usr/bin/env python3
# scripts/start_all_services.py

"""
🚀 SCRIPT DE DÉMARRAGE COMPLET - DJANGO + CELERY

Démarre tous les services nécessaires pour Afèpanou :
- Django development server
- Celery workers (tous types)
- Celery beat scheduler
- Flower monitoring

Usage:
    python scripts/start_all_services.py
    python scripts/start_all_services.py --production
    python scripts/start_all_services.py --dev-only
"""

import os
import sys
import time
import signal
import argparse
import subprocess
import threading
from pathlib import Path

# Configuration
PROJECT_DIR = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_DIR)

class AferanouServiceManager:
    """Gestionnaire de tous les services Afèpanou"""
    
    def __init__(self, production_mode=False):
        self.production_mode = production_mode
        self.processes = {}
        self.running = True
        
        print("🚀 AFÈPANOU SERVICE MANAGER")
        print("=" * 40)
        print(f"Mode: {'Production' if production_mode else 'Développement'}")
        print(f"Projet: {PROJECT_DIR}")
        print("=" * 40)
        
        # Configuration des services
        self.services = {
            'django': {
                'name': 'Django Server',
                'cmd': ['python', 'manage.py', 'runserver', '0.0.0.0:8000'],
                'essential': True,
                'port': 8000
            },
            'celery_payments': {
                'name': 'Celery Worker (Payments)',
                'cmd': [
                    'python', 'manage.py', 'celery_worker',
                    '--queue=payments_high_priority',
                    '--concurrency=2',
                    '--hostname=payments@%h'
                ],
                'essential': True,
                'delay': 2
            },
            'celery_default': {
                'name': 'Celery Worker (Default)',
                'cmd': [
                    'python', 'manage.py', 'celery_worker',
                    '--queue=default,emails_medium_priority,monitoring_medium_priority',
                    '--concurrency=4',
                    '--hostname=default@%h'
                ],
                'essential': True,
                'delay': 3
            },
            'celery_maintenance': {
                'name': 'Celery Worker (Maintenance)',
                'cmd': [
                    'python', 'manage.py', 'celery_worker',
                    '--queue=maintenance_low_priority',
                    '--concurrency=1',
                    '--hostname=maintenance@%h'
                ],
                'essential': False,
                'delay': 4
            },
            'celery_beat': {
                'name': 'Celery Beat Scheduler',
                'cmd': ['python', 'manage.py', 'celery_beat'],
                'essential': True,
                'delay': 5
            },
            'flower': {
                'name': 'Flower Monitoring',
                'cmd': [
                    'celery', '-A', 'config.celery:app', 'flower',
                    '--port=5555',
                    '--url_prefix=flower'
                ],
                'essential': False,
                'delay': 6,
                'port': 5555
            }
        }
    
    def start_all_services(self, dev_only=False):
        """Démarrer tous les services"""
        print("🔄 Démarrage des services...")
        
        # Pré-vérifications
        if not self.pre_flight_check():
            print("❌ Pré-vérifications échouées. Arrêt.")
            return False
        
        # Gestionnaire de signaux
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Démarrer services dans l'ordre
        for service_name, config in self.services.items():
            if dev_only and service_name not in ['django', 'celery_payments', 'celery_beat']:
                print(f"⏭️  Skipping {config['name']} (dev-only mode)")
                continue
                
            if not config.get('essential', True) and not self.production_mode:
                print(f"⏭️  Skipping {config['name']} (non-essential)")
                continue
            
            success = self.start_service(service_name, config)
            if not success and config.get('essential', True):
                print(f"❌ Service essentiel {config['name']} a échoué. Arrêt.")
                self.stop_all_services()
                return False
            
            # Délai entre démarrages
            if 'delay' in config:
                time.sleep(config['delay'])
        
        # Affichage des URLs
        self.show_service_urls()
        
        # Boucle principale
        print("\n✅ Tous les services sont démarrés !")
        print("📝 Appuyez sur Ctrl+C pour arrêter tous les services")
        
        try:
            while self.running:
                self.monitor_services()
                time.sleep(5)
        except KeyboardInterrupt:
            pass
        
        self.stop_all_services()
        return True
    
    def start_service(self, service_name, config):
        """Démarrer un service individuel"""
        print(f"🚀 Démarrage: {config['name']}")
        
        try:
            # Configuration logs
            log_file = PROJECT_DIR / 'logs' / f'{service_name}.log'
            log_file.parent.mkdir(exist_ok=True)
            
            # Démarrer processus
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    config['cmd'],
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=PROJECT_DIR
                )
            
            self.processes[service_name] = {
                'process': process,
                'config': config,
                'log_file': log_file
            }
            
            # Vérifier démarrage
            time.sleep(1)
            if process.poll() is None:
                print(f"   ✅ {config['name']}: Démarré (PID: {process.pid})")
                if 'port' in config:
                    print(f"   🌐 Port: {config['port']}")
                return True
            else:
                print(f"   ❌ {config['name']}: Échec démarrage")
                return False
                
        except Exception as e:
            print(f"   ❌ {config['name']}: Erreur - {e}")
            return False
    
    def pre_flight_check(self):
        """Vérifications avant démarrage"""
        print("🔍 Pré-vérifications...")
        
        checks = [
            ('Python', lambda: sys.version_info >= (3, 8)),
            ('Django', self.check_django),
            ('Redis', self.check_redis),
            ('Celery', self.check_celery),
            ('Migrations', self.check_migrations)
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                if check_func():
                    print(f"   ✅ {check_name}: OK")
                else:
                    print(f"   ❌ {check_name}: ÉCHEC")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {check_name}: ERREUR - {e}")
                all_passed = False
        
        return all_passed
    
    def check_django(self):
        """Vérifier Django"""
        result = subprocess.run(
            ['python', 'manage.py', 'check'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def check_redis(self):
        """Vérifier Redis"""
        try:
            import redis
            from django.conf import settings
            
            # Charger Django settings
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
            import django
            django.setup()
            
            redis_url = settings.CELERY_BROKER_URL
            r = redis.from_url(redis_url)
            return r.ping()
        except:
            return False
    
    def check_celery(self):
        """Vérifier configuration Celery"""
        try:
            from config.celery import app
            return app is not None
        except:
            return False
    
    def check_migrations(self):
        """Vérifier migrations Django"""
        result = subprocess.run(
            ['python', 'manage.py', 'showmigrations', '--plan'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    
    def monitor_services(self):
        """Surveiller l'état des services"""
        dead_services = []
        
        for service_name, service_info in self.processes.items():
            process = service_info['process']
            if process.poll() is not None:
                dead_services.append(service_name)
        
        for service_name in dead_services:
            config = self.processes[service_name]['config']
            print(f"⚠️  Service mort détecté: {config['name']}")
            
            if config.get('essential', True):
                print("🔄 Redémarrage service essentiel...")
                self.restart_service(service_name)
    
    def restart_service(self, service_name):
        """Redémarrer un service"""
        if service_name in self.processes:
            config = self.processes[service_name]['config']
            del self.processes[service_name]
            time.sleep(2)
            self.start_service(service_name, config)
    
    def show_service_urls(self):
        """Afficher les URLs des services"""
        print("\n🌐 SERVICES ACCESSIBLES:")
        print("   📊 Django Admin: http://localhost:8000/admin/")
        print("   🔧 Django API: http://localhost:8000/api/")
        print("   🌸 Flower Monitor: http://localhost:5555/")
        print("   📋 API Docs: http://localhost:8000/api/schema/swagger-ui/")
    
    def stop_all_services(self):
        """Arrêter tous les services"""
        print("\n🛑 Arrêt des services...")
        
        for service_name, service_info in self.processes.items():
            config = service_info['config']
            process = service_info['process']
            
            print(f"   🛑 Arrêt: {config['name']}")
            process.terminate()
        
        # Attendre arrêt gracieux
        time.sleep(3)
        
        # Force kill si nécessaire
        for service_name, service_info in self.processes.items():
            process = service_info['process']
            if process.poll() is None:
                print(f"   💀 Force kill: {service_info['config']['name']}")
                process.kill()
        
        print("✅ Tous les services sont arrêtés")
    
    def signal_handler(self, signum, frame):
        """Gestionnaire de signal pour arrêt propre"""
        print(f"\n🛑 Signal reçu: {signum}")
        self.running = False


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Afèpanou Service Manager')
    parser.add_argument('--production', action='store_true', help='Mode production')
    parser.add_argument('--dev-only', action='store_true', help='Services dev seulement')
    
    args = parser.parse_args()
    
    # Créer dossier logs
    os.makedirs('logs', exist_ok=True)
    
    manager = AferanouServiceManager(production_mode=args.production)
    success = manager.start_all_services(dev_only=args.dev_only)
    
    if success:
        print("🎉 Session terminée avec succès")
    else:
        print("❌ Session terminée avec erreurs")
        sys.exit(1)

if __name__ == '__main__':
    main()