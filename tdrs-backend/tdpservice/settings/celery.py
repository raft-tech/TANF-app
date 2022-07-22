from __future__ import absolute_import
import os
from celery import Celery, shared_task
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tdpservice.settings.local")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

import configurations
configurations.setup()

app = Celery('settings')
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


from celery.schedules import crontab
from tdpservice.scheduling.tasks import run_backup

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour='*', minute='*/1', day_of_week='*'),
        run_backup.s('Happy Mondays!'),
    )

@app.task
def run_backup(b):
    
    logger.debug("my arg was" + b)

