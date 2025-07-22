# ===================================================================
# Dockerfile - Afèpanou Marketplace (Railway Optimized - FIXED)
# ===================================================================

FROM python:3.11-slim

# ===================================================================
# VARIABLES D'ENVIRONNEMENT
# ===================================================================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Variables Django
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV ENVIRONMENT=production

# ===================================================================
# INSTALLATION DES DÉPENDANCES SYSTÈME
# ===================================================================

# Mise à jour et installation en une seule couche pour réduire la taille
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    build-essential \
    gcc \
    pkg-config \
    # PostgreSQL
    libpq-dev \
    postgresql-client \
    # Python dev
    python3-dev \
    # Image processing (Pillow)
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev \
    libfreetype6-dev \
    # SSL et crypto
    libssl-dev \
    libffi-dev \
    # Outils système
    curl \
    netcat-openbsd \
    wget \
    # Git pour certaines dépendances Python
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# ===================================================================
# CONFIGURATION UTILISATEUR
# ===================================================================

# Créer un utilisateur non-root
RUN groupadd -r django && useradd -r -g django -d /app django

# ===================================================================
# CONFIGURATION APPLICATION
# ===================================================================

# Créer le répertoire de travail
WORKDIR /app

# Créer les dossiers nécessaires avec bonnes permissions
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R django:django /app

# Mettre à jour pip
RUN pip install --upgrade pip setuptools wheel

# Copier et installer les dépendances Python
COPY --chown=django:django requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY --chown=django:django . .

# Copier et rendre exécutable le script d'entrée
COPY --chown=django:django entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ===================================================================
# CONFIGURATION DJANGO
# ===================================================================

# Passer à l'utilisateur django pour les opérations Django
USER django

# Génération clé secrète temporaire si nécessaire
RUN if [ ! -f .env ]; then \
        python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(50))" > .env; \
    fi

# Collecter les fichiers statiques (peut échouer sans DB, sera refait au runtime)
RUN python manage.py collectstatic --noinput --clear || echo "Collectstatic will be retried at runtime"

# ===================================================================
# CONFIGURATION FINALE
# ===================================================================

# Exposer le port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health/ || exit 1

# Script d'entrée
ENTRYPOINT ["/entrypoint.sh"]

# Commande par défaut
CMD ["web"]