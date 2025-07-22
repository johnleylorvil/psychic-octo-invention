#!/bin/bash
# ===================================================================
# entrypoint.sh - Afèpanou Marketplace Entrypoint
# ===================================================================

set -euo pipefail

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# ===================================================================
# FONCTIONS UTILITAIRES
# ===================================================================

# Attendre que PostgreSQL soit prêt
wait_for_postgres() {
    log "Waiting for PostgreSQL to be ready..."
    
    if [ -z "${DATABASE_URL:-}" ]; then
        log_warning "DATABASE_URL not set, skipping PostgreSQL check"
        return 0
    fi
    
    # Extraire les infos de connexion depuis DATABASE_URL
    # Format: postgresql://user:pass@host:port/dbname
    DB_HOST=$(python -c "
import urllib.parse as up
import os
url = os.environ.get('DATABASE_URL', '')
if url:
    result = up.urlparse(url)
    print(result.hostname or 'localhost')
else:
    print('localhost')
")
    
    DB_PORT=$(python -c "
import urllib.parse as up
import os
url = os.environ.get('DATABASE_URL', '')
if url:
    result = up.urlparse(url)
    print(result.port or 5432)
else:
    print('5432')
")
    
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
            log_success "PostgreSQL is ready on $DB_HOST:$DB_PORT"
            return 0
        fi
        
        log "PostgreSQL not ready yet... attempt $attempt/$max_attempts"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "PostgreSQL connection timeout after $max_attempts attempts"
    exit 1
}

# Attendre que Redis soit prêt
wait_for_redis() {
    log "Checking Redis connection..."
    
    if [ -z "${REDIS_URL:-}" ]; then
        log_warning "REDIS_URL not set, skipping Redis check"
        return 0
    fi
    
    # Extraire host et port depuis REDIS_URL
    REDIS_HOST=$(python -c "
import urllib.parse as up
import os
url = os.environ.get('REDIS_URL', '')
if url:
    result = up.urlparse(url)
    print(result.hostname or 'localhost')
else:
    print('localhost')
")
    
    REDIS_PORT=$(python -c "
import urllib.parse as up
import os
url = os.environ.get('REDIS_URL', '')
if url:
    result = up.urlparse(url)
    print(result.port or 6379)
else:
    print('6379')
")
    
    max_attempts=15
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z "$REDIS_HOST" "$REDIS_PORT" 2>/dev/null; then
            log_success "Redis is ready on $REDIS_HOST:$REDIS_PORT"
            return 0
        fi
        
        log "Redis not ready yet... attempt $attempt/$max_attempts"
        sleep 1
        attempt=$((attempt + 1))
    done
    
    log_warning "Redis connection timeout, continuing anyway"
}

# Vérifier la configuration Django
check_django_config() {
    log "Checking Django configuration..."
    
    if ! python manage.py check --deploy; then
        log_error "Django configuration check failed!"
        exit 1
    fi
    
    log_success "Django configuration is valid"
}

# Exécuter les migrations
run_migrations() {
    log "Running database migrations..."
    
    if python manage.py migrate --noinput; then
        log_success "Database migrations completed"
    else
        log_error "Database migrations failed!"
        exit 1
    fi
}

# Collecter les fichiers statiques
collect_static() {
    log "Collecting static files..."
    
    if python manage.py collectstatic --noinput --clear; then
        log_success "Static files collected successfully"
    else
        log_warning "Static files collection failed, but continuing..."
    fi
}

# Créer un superuser si les variables d'environnement sont définies
create_superuser() {
    if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
        log "Creating superuser..."
        
        python manage.py shell << EOF
from marketplace.models import User
import os

email = os.environ['DJANGO_SUPERUSER_EMAIL']
username = os.environ['DJANGO_SUPERUSER_USERNAME']
password = os.environ['DJANGO_SUPERUSER_PASSWORD']

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(username, email, password)
    print(f"✅ Superuser {username} created successfully")
else:
    print(f"ℹ️ Superuser {email} already exists")
EOF
        
        log_success "Superuser setup completed"
    else
        log "Superuser environment variables not set, skipping..."
    fi
}

# Initialiser les données de base (optionnel)
load_initial_data() {
    if [ -f "fixtures/initial_data.json" ]; then
        log "Loading initial data..."
        if python manage.py loaddata fixtures/initial_data.json; then
            log_success "Initial data loaded successfully"
        else
            log_warning "Failed to load initial data, but continuing..."
        fi
    else
        log "No initial data fixtures found, skipping..."
    fi
}

# Warm up de l'application
warm_up_application() {
    log "Warming up Django application..."
    
    python -c "
import django
from django.conf import settings
django.setup()

# Test database connection
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('✅ Database connection OK')

# Test cache connection (if Redis available)
try:
    from django.core.cache import cache
    cache.set('warmup_test', 'ok', 30)
    if cache.get('warmup_test') == 'ok':
        print('✅ Cache connection OK')
    else:
        print('⚠️ Cache connection issue')
except Exception as e:
    print(f'⚠️ Cache not available: {e}')

print('🔥 Application warmed up successfully')
" || log_warning "Application warmup had issues, but continuing..."
}

# Afficher les informations de démarrage
show_startup_info() {
    log_success "=== AFÈPANOU MARKETPLACE STARTUP ==="
    log "Environment: ${ENVIRONMENT:-development}"
    log "Django Settings: ${DJANGO_SETTINGS_MODULE:-config.settings}"
    log "Debug Mode: ${DEBUG:-True}"
    log "Port: ${PORT:-8000}"
    log "Workers: ${WEB_CONCURRENCY:-3}"
    
    if [ -n "${RAILWAY_ENVIRONMENT:-}" ]; then
        log "Railway Environment: ${RAILWAY_ENVIRONMENT}"
    fi
    
    if [ -n "${RAILWAY_DEPLOYMENT_ID:-}" ]; then
        log "Railway Deployment: ${RAILWAY_DEPLOYMENT_ID}"
    fi
    
    log "========================================"
}

# ===================================================================
# COMMANDES PRINCIPALES
# ===================================================================

# Fonction de setup commune
common_setup() {
    show_startup_info
    wait_for_postgres
    wait_for_redis
    check_django_config
}

# Démarrage du serveur web
start_web() {
    log "🚀 Starting Afèpanou Web Server..."
    
    common_setup
    run_migrations
    collect_static
    create_superuser
    load_initial_data
    warm_up_application
    
    log_success "Web server initialization completed!"
    log "Starting Gunicorn server on port ${PORT:-8000}..."
    
    # Configuration Gunicorn optimisée pour Railway
    exec gunicorn config.wsgi:application \
        --bind "0.0.0.0:${PORT:-8000}" \
        --workers "${WEB_CONCURRENCY:-3}" \
        --worker-class "sync" \
        --worker-connections 1000 \
        --timeout "${GUNICORN_TIMEOUT:-120}" \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --preload \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --capture-output
}

# Démarrage du worker Celery
start_worker() {
    log "👷 Starting Afèpanou Celery Worker..."
    
    common_setup
    
    log_success "Worker initialization completed!"
    log "Starting Celery worker..."
    
    exec celery -A config worker \
        --loglevel=info \
        --concurrency="${CELERY_WORKER_CONCURRENCY:-2}" \
        --max-tasks-per-child=50 \
        --max-memory-per-child=200000 \
        --time-limit=600 \
        --soft-time-limit=300
}

# Démarrage du scheduler Celery Beat
start_beat() {
    log "⏰ Starting Afèpanou Celery Beat Scheduler..."
    
    common_setup
    
    log_success "Beat scheduler initialization completed!"
    log "Starting Celery beat..."
    
    exec celery -A config beat \
        --loglevel=info \
        --scheduler django_celery_beat.schedulers:DatabaseScheduler \
        --pidfile=
}

# Démarrage de Flower (monitoring Celery)
start_flower() {
    log "🌸 Starting Afèpanou Celery Flower Monitor..."
    
    wait_for_redis
    
    log_success "Flower initialization completed!"
    log "Starting Flower on port ${PORT:-5555}..."
    
    exec celery -A config flower \
        --port="${PORT:-5555}" \
        --basic_auth="${FLOWER_USER:-admin}:${FLOWER_PASSWORD:-admin123}" \
        --url_prefix="${FLOWER_URL_PREFIX:-}"
}

# Shell Django
start_shell() {
    log "🐚 Starting Django Shell..."
    common_setup
    exec python manage.py shell
}

# Commandes de management
run_command() {
    log "🔧 Running Django management command: $*"
    common_setup
    exec python manage.py "$@"
}

# ===================================================================
# POINT D'ENTRÉE PRINCIPAL
# ===================================================================

case "${1:-web}" in
    web)
        start_web
        ;;
    worker)
        start_worker
        ;;
    beat)
        start_beat
        ;;
    flower)
        start_flower
        ;;
    shell)
        start_shell
        ;;
    manage)
        shift
        run_command "$@"
        ;;
    *)
        log "🎯 Available commands:"
        log "  web     - Start web server (default)"
        log "  worker  - Start Celery worker"
        log "  beat    - Start Celery beat scheduler"  
        log "  flower  - Start Celery Flower monitor"
        log "  shell   - Start Django shell"
        log "  manage  - Run Django management command"
        log ""
        log "Usage examples:"
        log "  docker run afepanou web"
        log "  docker run afepanou worker"
        log "  docker run afepanou manage createsuperuser"
        log ""
        log_error "Unknown command: $1"
        exit 1
        ;;
esac