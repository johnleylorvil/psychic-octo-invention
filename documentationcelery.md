# 🚀 **GUIDE CONFIGURATION CELERY - AFÈPANOU MARKETPLACE**

## ✅ **ÉTAPES DE CONFIGURATION (15 MINUTES)**

### **1. Installation des Dépendances**

```bash
# 📦 Installation Celery + dépendances
pip install celery[redis]==5.3.4 django-celery-beat==2.5.0 flower==2.0.1

# 🔄 Mise à jour requirements.txt
pip freeze > requirements.txt
```

### **2. Modification INSTALLED_APPS dans `config/settings.py`**

```python
THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'storages',
    
    # ✅ AJOUTER CES LIGNES
    'django_celery_beat',         # Tâches périodiques
    'django_celery_results',      # Résultats en DB (optionnel)
]
```

### **3. Ajout Configuration Celery dans `config/settings.py`**

Ajouter la configuration Celery fournie dans l'artifact précédent à la fin du fichier settings.py.

### **4. Migrations Django-Celery-Beat**

```bash
# 📊 Créer tables pour tâches périodiques
python manage.py makemigrations django_celery_beat
python manage.py migrate django_celery_beat

# 📊 Créer tables pour résultats (optionnel)
python manage.py makemigrations django_celery_results  
python manage.py migrate django_celery_results
```

### **5. Création des Dossiers**

```bash
# 📁 Créer dossiers nécessaires
mkdir -p logs scripts marketplace/management/commands

# 📝 Permissions logs
chmod 755 logs
```

---

## 🚀 **MÉTHODES DE DÉMARRAGE**

### **Méthode 1: Commandes Django (Recommandé)**

```bash
# 📊 Vérifier statut
python manage.py celery_status

# 🚀 Démarrer worker principal (Terminal 1)
python manage.py celery_worker --queue=default --concurrency=4

# 🚀 Démarrer worker paiements (Terminal 2)  
python manage.py celery_worker --queue=payments_high_priority --concurrency=2

# ⏰ Démarrer beat scheduler (Terminal 3)
python manage.py celery_beat

# 🌸 Démarrer monitoring (Terminal 4 - optionnel)
celery -A config.celery:app flower --port=5555
```

### **Méthode 2: Script Python Automatisé**

```bash
# 🚀 Démarrer tous les services
python scripts/celery_start.py --all

# 🚀 Démarrer seulement workers
python scripts/celery_start.py --worker

# ⏰ Démarrer seulement beat
python scripts/celery_start.py --beat

# 📊 Vérifier statut
python scripts/celery_start.py --status
```

### **Méthode 3: Commandes Celery Directes**

```bash
# 🚀 Worker toutes queues
celery -A config.celery:app worker --loglevel=INFO --concurrency=4

# 🚀 Worker queue spécifique  
celery -A config.celery:app worker --queues=payments_high_priority --concurrency=2

# ⏰ Beat scheduler
celery -A config.celery:app beat --loglevel=INFO

# 🌸 Flower monitoring
celery -A config.celery:app flower --port=5555
```

---

## 🎯 **CONFIGURATION QUEUES SPÉCIALISÉES**

### **Architecture des Queues :**

```python
payments_high_priority     # 🚨 Paiements critiques (concurrency=2, prefetch=1)
monitoring_medium_priority # 📊 Monitoring système (concurrency=1, prefetch=2)  
emails_medium_priority     # 📧 Notifications email (concurrency=2, prefetch=3)
maintenance_low_priority   # 🧹 Nettoyage données (concurrency=1, prefetch=4)
default                   # 🔄 Tâches générales (concurrency=4, prefetch=4)
```

### **Workers Optimaux en Production :**

```bash
# 💳 Worker haute priorité paiements
celery -A config.celery:app worker \
  --queues=payments_high_priority \
  --concurrency=2 \
  --prefetch-multiplier=1 \
  --max-tasks-per-child=10 \
  --hostname=payments@%h

# 📊 Worker monitoring système
celery -A config.celery:app worker \
  --queues=monitoring_medium_priority \
  --concurrency=1 \
  --prefetch-multiplier=2 \
  --max-tasks-per-child=20 \
  --hostname=monitoring@%h

# 🔄 Worker général
celery -A config.celery:app worker \
  --queues=default,emails_medium_priority,maintenance_low_priority \
  --concurrency=4 \
  --prefetch-multiplier=4 \
  --max-tasks-per-child=50 \
  --hostname=general@%h
```

---

## 🧪 **TESTS DE VALIDATION**

### **1. Test Connexion Redis**

```python
# Dans Django shell
python manage.py shell

import redis
from django.conf import settings
r = redis.from_url(settings.CELERY_BROKER_URL)
r.ping()  # Doit retourner True
```

### **2. Test Tâche Simple**

```python
# Dans Django shell
from config.celery import debug_task
result = debug_task.delay()
print(result.get())  # Doit afficher "Debug task completed"
```

### **3. Test Tâche Paiement**

```python
# Dans Django shell  
from marketplace.tasks.payment_tasks import process_payment_webhook

# Test données webhook
webhook_data = {
    'transactionId': 'test123',
    'orderId': 'AF12345678', 
    'amount': '100.00',
    'message': 'successful'
}

result = process_payment_webhook.delay(webhook_data)
print(result.get())  # Vérifier traitement
```

### **4. Test Beat Schedule**

```bash
# Vérifier tâches périodiques configurées
celery -A config.celery:app inspect scheduled

# Forcer exécution tâche immédiate
python manage.py shell
from marketplace.tasks.payment_tasks import cleanup_expired_carts
cleanup_expired_carts.delay()
```

---

## 📊 **MONITORING ET DEBUGGING**

### **Flower Web Interface**

```bash
# Démarrer Flower
celery -A config.celery:app flower --port=5555

# Accéder interface web
http://localhost:5555

# Features disponibles :
# - Workers actifs et statuts
# - Queues et tâches en attente  
# - Historique tâches exécutées
# - Métriques performance temps réel
# - Retry/kill tâches manuellement
```

### **Commandes de Debug**

```bash
# 📊 Statut workers
celery -A config.celery:app inspect active
celery -A config.celery:app inspect reserved
celery -A config.celery:app inspect scheduled

# 🔄 Contrôle workers
celery -A config.celery:app control shutdown  # Arrêt gracieux
celery -A config.celery:app control cancel_consumer queue_name
celery -A config.celery:app control add_consumer queue_name

# 📝 Logs détaillés
celery -A config.celery:app worker --loglevel=DEBUG
celery -A config.celery:app events --loglevel=DEBUG
```

### **Fichiers de Logs**

```bash
# 📂 Localisation logs
logs/celery_payments_worker.log     # Worker paiements
logs/celery_default_worker.log      # Worker général  
logs/celery_beat.log                # Beat scheduler
logs/celery_flower.log              # Flower monitoring

# 🔍 Surveillance temps réel
tail -f logs/celery_payments_worker.log
tail -f logs/celery_beat.log
```

---

## ⚡ **OPTIMISATIONS PRODUCTION**

### **Variables d'Environnement Production**

```env
# .env - Configuration production
CELERY_LOG_LEVEL=INFO
CELERY_CONCURRENCY=4
CELERY_MAX_TASKS_PER_CHILD=50
CELERY_WORKER_MAX_MEMORY=200000

# Redis optimizations
REDIS_MAX_CONNECTIONS=50
REDIS_RETRY_ON_TIMEOUT=True
```

### **Supervision avec Supervisor (Production)**

```ini
# /etc/supervisor/conf.d/afepanou_celery.conf
[program:afepanou_celery_worker]
command=celery -A config.celery:app worker --loglevel=INFO
directory=/path/to/afepanou_api
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log

[program:afepanou_celery_beat]
command=celery -A config.celery:app beat --loglevel=INFO
directory=/path/to/afepanou_api
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
```

### **Systemd Services (Alternative)**

```ini
# /etc/systemd/system/afepanou-celery.service
[Unit]
Description=Afepanou Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/afepanou_api
ExecStart=celery -A config.celery:app worker --detach
ExecStop=celery -A config.celery:app control shutdown
ExecReload=celery -A config.celery:app control cancel_consumer default

[Install]
WantedBy=multi-user.target
```

---

## ⚠️ **DÉPANNAGE COURANT**

### **Problème : Redis Connection Failed**

```bash
# Vérifier Redis running
redis-cli ping  # Doit retourner PONG

# Vérifier URL Redis dans .env
echo $REDIS_URL

# Test connexion Python
python -c "import redis; r=redis.from_url('$REDIS_URL'); print(r.ping())"
```

### **Problème : No Workers Active**

```bash
# Vérifier processus Celery
ps aux | grep celery

# Vérifier logs erreurs
tail -50 logs/celery_default_worker.log

# Redémarrer worker
python manage.py celery_worker --queue=default
```

### **Problème : Tasks Not Executing**

```bash
# Vérifier queue routing
celery -A config.celery:app inspect reserved

# Purger queues bloquées
python manage.py celery_purge --force

# Vérifier configuration routing dans celery.py
```

### **Problème : Beat Not Scheduling**

```bash
# Vérifier processus beat
ps aux | grep "celery.*beat"

# Supprimer fichier schedule corrompu
rm celerybeat-schedule celerybeat.pid

# Redémarrer beat
python manage.py celery_beat
```

---

## ✅ **CHECKLIST FINAL**

- [ ] ✅ Redis accessible et ping OK
- [ ] ✅ Migrations django-celery-beat appliquées  
- [ ] ✅ Workers démarrent sans erreur
- [ ] ✅ Beat scheduler actif et schedule visible
- [ ] ✅ Test tâche simple s'exécute
- [ ] ✅ Flower monitoring accessible
- [ ] ✅ Logs générés dans dossier logs/
- [ ] ✅ Queues spécialisées configurées
- [ ] ✅ Configuration production optimisée

**🎯 Avec cette configuration, Celery est prêt pour traiter les webhooks MonCash et toutes les tâches asynchrones d'Afèpanou !**