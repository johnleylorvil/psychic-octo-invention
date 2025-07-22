# ===================================================================
# Dockerfile - Afèpanou Marketplace (Railway Optimized)
# ===================================================================

# Utiliser une image Python slim officielle
FROM python:3.11-slim as base

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
# STAGE 1: DEPENDENCIES BUILDER
# ===================================================================
FROM base as builder

# Installer les dépendances système pour compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Outils de build essentiels
    build-essential \
    pkg-config \
    gcc \
    g++ \
    # PostgreSQL dependencies
    libpq-dev \
    python3-dev \
    # Image processing (Pillow)
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    # SSL et cryptographie
    libssl-dev \
    libffi-dev \
    # Redis (optionnel pour outils)
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Créer un environnement virtuel
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Mettre à jour pip dans le venv
RUN pip install --upgrade pip setuptools wheel

# Copier et installer les dépendances Python
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# ===================================================================
# STAGE 2: RUNTIME
# ===================================================================
FROM base as runtime

# Installer uniquement les dépendances runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    # PostgreSQL client
    libpq5 \
    postgresql-client \
    # Image processing runtime libs
    libjpeg62-turbo \
    libpng16-16 \
    libwebp7 \
    libfreetype6 \
    liblcms2-2 \
    libopenjp2-7 \
    libtiff5 \
    # SSL runtime
    libssl3 \
    libffi8 \
    # Outils système utiles
    curl \
    netcat-traditional \
    wget \
    # Redis client (pour debugging)
    redis-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copier l'environnement virtuel depuis builder
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r django && useradd -r -g django django

# Créer et définir le répertoire de travail
WORKDIR /app

# Créer les dossiers nécessaires
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R django:django /app

# Copier les fichiers de l'application
COPY --chown=django:django . .

# Copier le script d'entrée
COPY --chown=django:django entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ===================================================================
# CONFIGURATION DJANGO
# ===================================================================

# Générer une clé secrète temporaire si nécessaire (sera overridée en production)
RUN if [ ! -f .env ]; then \
    python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(50))" > .env; \
    fi

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput --clear || echo "Collectstatic failed, will retry at runtime"

# Vérifier la configuration Django
RUN python manage.py check --deploy || echo "Deploy check failed, will retry at runtime"

# ===================================================================
# CONFIGURATION UTILISATEUR ET PERMISSIONS
# ===================================================================

# Ajuster les permissions
RUN chown -R django:django /app
USER django

# ===================================================================
# PORTS
# ===================================================================

# Exposer le port (Railway utilise la variable PORT)
EXPOSE 8000

# ===================================================================
# HEALTH CHECK
# ===================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health/ || exit 1

# ===================================================================
# COMMANDE DE DÉMARRAGE
# ===================================================================

# Script d'entrée pour gérer les migrations et le démarrage
ENTRYPOINT ["/entrypoint.sh"]

# Commande par défaut (peut être overridée)
CMD ["web"]