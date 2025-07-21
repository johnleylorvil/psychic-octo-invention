#!/usr/bin/env python3
# scripts/test_celery_complete.py

"""
🧪 SCRIPT DE TEST COMPLET CELERY - AFÈPANOU MARKETPLACE

Tests toutes les tâches Celery développées :
- Payment tasks
- Email tasks  
- Stock tasks
- Configuration Celery

Usage:
    python scripts/test_celery_complete.py
    python scripts/test_celery_complete.py --quick
    python scripts/test_celery_complete.py --payment-only
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path

# Configuration Django
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# Imports Django/Celery
import redis
from django.conf import settings
from django.contrib.auth import get_user_model
from celery import current_app
from config.celery import app as celery_app

# Imports des tâches
from marketplace.tasks.payment_tasks import (
    process_payment_webhook,
    cleanup_expired_carts,
    monitor_stuck_payments
)
from marketplace.tasks.email_tasks import (
    send_order_confirmation_email,
    send_low_stock_alert_email,
    send_welcome_email,
    send_newsletter_email
)
from marketplace.tasks.stock_tasks import (
    daily_stock_audit,
    cleanup_expired_stock_reservations,
    update_product_popularity_scores
)

User = get_user_model()

class CeleryTaskTester:
    """Testeur complet pour toutes les tâches Celery"""
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'details': {}
        }
        print("🧪 AFÈPANOU CELERY TASK TESTER")
        print("=" * 50)
    
    def run_all_tests(self, quick=False, payment_only=False):
        """Exécuter tous les tests selon les options"""
        
        # Tests de base (toujours)
        self.test_redis_connection()
        self.test_celery_config()
        
        if payment_only:
            print("\n💳 TESTS PAYMENT TASKS SEULEMENT")
            self.test_payment_tasks()
        elif quick:
            print("\n⚡ TESTS RAPIDES")
            self.test_payment_tasks()
            self.test_basic_email_task()
        else:
            print("\n🔄 TESTS COMPLETS")
            self.test_payment_tasks()
            self.test_email_tasks()
            self.test_stock_tasks()
        
        # Résultats finaux
        self.print_final_results()
    
    def test_redis_connection(self):
        """Test 1: Connexion Redis"""
        self.test_results['total_tests'] += 1
        print("\n📊 Test 1: Connexion Redis")
        
        try:
            redis_url = settings.CELERY_BROKER_URL
            r = redis.from_url(redis_url)
            result = r.ping()
            
            if result:
                print("✅ Redis ping: OK")
                info = r.info()
                print(f"   Version: {info.get('redis_version')}")
                print(f"   Mémoire: {info.get('used_memory_human')}")
                self._test_passed("redis_connection")
            else:
                self._test_failed("redis_connection", "Ping failed")
                
        except Exception as e:
            self._test_failed("redis_connection", str(e))
    
    def test_celery_config(self):
        """Test 2: Configuration Celery"""
        self.test_results['total_tests'] += 1
        print("\n⚙️ Test 2: Configuration Celery")
        
        try:
            # Test broker URL
            if celery_app.conf.broker_url:
                print("✅ Broker URL: Configuré")
            else:
                raise Exception("Broker URL manquant")
            
            # Test routes
            routes = celery_app.conf.task_routes
            if routes:
                print(f"✅ Task Routes: {len(routes)} configurées")
            
            # Test beat schedule
            beat_schedule = celery_app.conf.beat_schedule
            if beat_schedule:
                print(f"✅ Beat Schedule: {len(beat_schedule)} tâches")
            
            self._test_passed("celery_config")
            
        except Exception as e:
            self._test_failed("celery_config", str(e))
    
    def test_payment_tasks(self):
        """Test 3: Tâches Payment"""
        print("\n💳 Test 3: Payment Tasks")
        
        # Test 3a: Webhook MonCash
        self._test_webhook_processing()
        
        # Test 3b: Cleanup carts
        self._test_cleanup_carts()
        
        # Test 3c: Monitor payments
        self._test_monitor_payments()
    
    def _test_webhook_processing(self):
        """Test process_payment_webhook"""
        self.test_results['total_tests'] += 1
        print("\n   🔄 Test 3a: Webhook MonCash")
        
        try:
            # Données webhook de test
            test_webhook = {
                'transactionId': f'TEST_{int(time.time())}',
                'orderId': f'AF_TEST_{int(time.time())}',
                'amount': '100.00',
                'message': 'successful',
                'payer': 'test@example.com',
                'reference': 'REF_TEST'
            }
            
            print(f"   📤 Envoi webhook: {test_webhook['transactionId']}")
            result = process_payment_webhook.delay(test_webhook)
            
            try:
                webhook_result = result.get(timeout=self.timeout)
                print(f"   ✅ Résultat: {webhook_result.get('status', 'unknown')}")
                self._test_passed("webhook_processing", webhook_result)
            except Exception as timeout_e:
                print(f"   ⚠️ Timeout: {timeout_e}")
                self._test_failed("webhook_processing", f"Timeout: {timeout_e}")
                
        except Exception as e:
            self._test_failed("webhook_processing", str(e))
    
    def _test_cleanup_carts(self):
        """Test cleanup_expired_carts"""
        self.test_results['total_tests'] += 1
        print("\n   🧹 Test 3b: Cleanup Carts")
        
        try:
            result = cleanup_expired_carts.delay()
            cleanup_result = result.get(timeout=self.timeout)
            
            print(f"   ✅ Cleanup: {cleanup_result.get('status', 'unknown')}")
            print(f"   📊 Paniers nettoyés: {cleanup_result.get('cleaned_count', 0)}")
            self._test_passed("cleanup_carts", cleanup_result)
            
        except Exception as e:
            self._test_failed("cleanup_carts", str(e))
    
    def _test_monitor_payments(self):
        """Test monitor_stuck_payments"""
        self.test_results['total_tests'] += 1
        print("\n   📊 Test 3c: Monitor Payments")
        
        try:
            result = monitor_stuck_payments.delay()
            monitor_result = result.get(timeout=self.timeout)
            
            print(f"   ✅ Monitor: {monitor_result.get('status', 'unknown')}")
            stuck_count = monitor_result.get('stuck_count', 0)
            print(f"   🔍 Paiements bloqués: {stuck_count}")
            self._test_passed("monitor_payments", monitor_result)
            
        except Exception as e:
            self._test_failed("monitor_payments", str(e))
    
    def test_email_tasks(self):
        """Test 4: Tâches Email"""
        print("\n📧 Test 4: Email Tasks")
        
        # Test 4a: Welcome email
        self._test_welcome_email()
        
        # Test 4b: Low stock alert
        self._test_low_stock_alert()
        
        # Test 4c: Newsletter
        self._test_newsletter()
    
    def test_basic_email_task(self):
        """Test email simple pour mode quick"""
        print("\n📧 Test 4: Email Task (Quick)")
        self._test_welcome_email()
    
    def _test_welcome_email(self):
        """Test send_welcome_email"""
        self.test_results['total_tests'] += 1
        print("\n   👋 Test 4a: Welcome Email")
        
        try:
            # Créer utilisateur test si nécessaire
            user = self._get_or_create_test_user()
            
            result = send_welcome_email.delay(user.id)
            email_result = result.get(timeout=self.timeout)
            
            print(f"   ✅ Email: {email_result.get('status', 'unknown')}")
            print(f"   📧 Destinataire: {email_result.get('email', 'N/A')}")
            self._test_passed("welcome_email", email_result)
            
        except Exception as e:
            self._test_failed("welcome_email", str(e))
    
    def _test_low_stock_alert(self):
        """Test send_low_stock_alert_email"""
        self.test_results['total_tests'] += 1
        print("\n   📦 Test 4b: Low Stock Alert")
        
        try:
            # Trouver un produit pour test
            from marketplace.models import Product
            product = Product.objects.first()
            
            if not product:
                print("   ⚠️ Aucun produit trouvé pour test")
                self._test_failed("low_stock_alert", "No products available")
                return
            
            result = send_low_stock_alert_email.delay(product.id, 2)
            alert_result = result.get(timeout=self.timeout)
            
            print(f"   ✅ Alerte: {alert_result.get('status', 'unknown')}")
            print(f"   📦 Produit: {alert_result.get('product_slug', 'N/A')}")
            self._test_passed("low_stock_alert", alert_result)
            
        except Exception as e:
            self._test_failed("low_stock_alert", str(e))
    
    def _test_newsletter(self):
        """Test send_newsletter_email"""
        self.test_results['total_tests'] += 1
        print("\n   📰 Test 4c: Newsletter")
        
        try:
            test_emails = ['test@example.com']
            
            result = send_newsletter_email.delay(
                subject="Test Newsletter Afèpanou",
                message="Ceci est un test de newsletter pour Afèpanou Marketplace.",
                recipient_list=test_emails
            )
            newsletter_result = result.get(timeout=self.timeout)
            
            print(f"   ✅ Newsletter: {newsletter_result.get('status', 'unknown')}")
            print(f"   📧 Recipients: {newsletter_result.get('recipients_count', 0)}")
            self._test_passed("newsletter", newsletter_result)
            
        except Exception as e:
            self._test_failed("newsletter", str(e))
    
    def test_stock_tasks(self):
        """Test 5: Tâches Stock"""
        print("\n📦 Test 5: Stock Tasks")
        
        # Test 5a: Stock audit
        self._test_stock_audit()
        
        # Test 5b: Stock reservations cleanup
        self._test_stock_cleanup()
        
        # Test 5c: Popularity scores
        self._test_popularity_scores()
    
    def _test_stock_audit(self):
        """Test daily_stock_audit"""
        self.test_results['total_tests'] += 1
        print("\n   🔍 Test 5a: Stock Audit")
        
        try:
            result = daily_stock_audit.delay()
            audit_result = result.get(timeout=self.timeout)
            
            print(f"   ✅ Audit: {audit_result.get('status', 'unknown')}")
            if 'audit_results' in audit_result:
                audit_data = audit_result['audit_results']
                print(f"   📊 Produits vérifiés: {audit_data.get('total_products_checked', 0)}")
                print(f"   ⚠️ Problèmes: {audit_data.get('issues_found', 0)}")
            
            self._test_passed("stock_audit", audit_result)
            
        except Exception as e:
            self._test_failed("stock_audit", str(e))
    
    def _test_stock_cleanup(self):
        """Test cleanup_expired_stock_reservations"""
        self.test_results['total_tests'] += 1
        print("\n   🧹 Test 5b: Stock Cleanup")
        
        try:
            result = cleanup_expired_stock_reservations.delay()
            cleanup_result = result.get(timeout=self.timeout)
            
            print(f"   ✅ Cleanup: {cleanup_result.get('status', 'unknown')}")
            if 'cleanup_stats' in cleanup_result:
                stats = cleanup_result['cleanup_stats']
                print(f"   🔄 Paniers traités: {stats.get('expired_carts_processed', 0)}")
                print(f"   📦 Stock libéré: {stats.get('stock_released_total', 0)}")
            
            self._test_passed("stock_cleanup", cleanup_result)
            
        except Exception as e:
            self._test_failed("stock_cleanup", str(e))
    
    def _test_popularity_scores(self):
        """Test update_product_popularity_scores"""
        self.test_results['total_tests'] += 1
        print("\n   ⭐ Test 5c: Popularity Scores")
        
        try:
            result = update_product_popularity_scores.delay()
            popularity_result = result.get(timeout=self.timeout)
            
            print(f"   ✅ Scores: {popularity_result.get('status', 'unknown')}")
            if 'update_stats' in popularity_result:
                stats = popularity_result['update_stats']
                print(f"   📊 Produits analysés: {stats.get('products_updated', 0)}")
                print(f"   🌟 Top produits: {len(stats.get('top_products', []))}")
            
            self._test_passed("popularity_scores", popularity_result)
            
        except Exception as e:
            self._test_failed("popularity_scores", str(e))
    
    def _get_or_create_test_user(self):
        """Créer ou récupérer utilisateur de test"""
        try:
            user, created = User.objects.get_or_create(
                username='test_celery_user',
                defaults={
                    'email': 'test.celery@afepanou.com',
                    'first_name': 'Test',
                    'last_name': 'Celery',
                    'is_active': True,
                }
            )
            return user
        except Exception as e:
            print(f"   ⚠️ Erreur création utilisateur test: {e}")
            return None
    
    def _test_passed(self, test_name, result=None):
        """Marquer test comme réussi"""
        self.test_results['passed'] += 1
        self.test_results['details'][test_name] = {
            'status': 'passed',
            'result': result
        }
    
    def _test_failed(self, test_name, error):
        """Marquer test comme échoué"""
        self.test_results['failed'] += 1
        self.test_results['errors'].append(f"{test_name}: {error}")
        self.test_results['details'][test_name] = {
            'status': 'failed',
            'error': error
        }
        print(f"   ❌ Échec: {error}")
    
    def print_final_results(self):
        """Afficher résultats finaux"""
        print("\n" + "=" * 50)
        print("📋 RÉSULTATS FINAUX - TESTS CELERY")
        print("=" * 50)
        
        total = self.test_results['total_tests']
        passed = self.test_results['passed']
        failed = self.test_results['failed']
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 Total tests: {total}")
        print(f"✅ Réussis: {passed}")
        print(f"❌ Échecs: {failed}")
        print(f"📈 Taux de réussite: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            print(f"\n❌ ERREURS ({len(self.test_results['errors'])}):")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        # Recommandations
        print("\n🎯 RECOMMANDATIONS:")
        if success_rate >= 90:
            print("✅ Configuration Celery excellente ! Prêt pour production.")
        elif success_rate >= 70:
            print("🟡 Configuration Celery fonctionnelle. Quelques ajustements mineurs.")
        else:
            print("🔴 Configuration Celery nécessite des corrections importantes.")
            print("   Vérifiez Redis, workers et configuration avant production.")
        
        # Instructions démarrage
        print("\n🚀 POUR DÉMARRER CELERY EN PRODUCTION:")
        print("   Terminal 1: python manage.py runserver")
        print("   Terminal 2: python manage.py celery_worker")
        print("   Terminal 3: python manage.py celery_beat")
        print("   Terminal 4: celery -A config.celery:app flower --port=5555")


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Test Celery Tasks Afèpanou')
    parser.add_argument('--quick', action='store_true', help='Tests rapides seulement')
    parser.add_argument('--payment-only', action='store_true', help='Tests payment seulement')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout par test (secondes)')
    
    args = parser.parse_args()
    
    tester = CeleryTaskTester(timeout=args.timeout)
    tester.run_all_tests(
        quick=args.quick,
        payment_only=args.payment_only
    )

if __name__ == '__main__':
    main()