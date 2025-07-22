web: python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A config.celery worker --loglevel=info
beat: celery -A config.celery beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler