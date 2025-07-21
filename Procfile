web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
worker: celery -A config worker --loglevel=info --max-tasks-per-child=50
beat: celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler