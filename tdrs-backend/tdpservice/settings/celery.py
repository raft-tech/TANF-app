"""Celey configuration file."""
from __future__ import absolute_import
import os

from celery import Celery, shared_task
from django.conf import settings
from celery.schedules import crontab
from tdpservice.scheduling.tasks import run_backup
import logging
logger = logging.getLogger(__name__)


import configurations


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tdpservice.settings.local")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

configurations.setup()

app = Celery('settings')
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'pg_backup': {
        'task': 'tdpservice.scheduling.tasks.run_backup',
        'schedule': crontab(day_of_week='*', hour='0', minute='0'),
        'args': ['-b'],
    },
}
