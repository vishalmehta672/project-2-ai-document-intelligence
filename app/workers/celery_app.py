from celery import Celery

from app.core.config import CELERY_BROKER_URL,CELERY_RESULT_BACKEND

# Initialize Celery app
celery_app = Celery(
    "document_intelligence",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
)
# Auto-discover tasks from all registered apps
celery_app.autodiscover_tasks(["app.workers"])


