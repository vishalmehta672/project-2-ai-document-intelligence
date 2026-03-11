#celery worker command
celery -A app.workers.celery_app worker --loglevel=debug