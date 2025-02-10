# isort:skip_file
# flake8: noqa

import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fbr.settings")

from dbt_copilot_python.celery_health_check import healthcheck

celery_app = Celery("fbr_celery")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()
celery_app = healthcheck.setup(celery_app)

celery_app.conf.beat_schedule = {
    "schedule-fbr-cache-task": {
        "task": "celery_worker.tasks.rebuild_cache",
        "schedule": crontab(hour="1", minute="00"),  # Runs daily at 1:00 AM
    },
}
