from __future__ import absolute_import
import os
from celery import Celery, shared_task

from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tdpservice.settings.local")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

import configurations
configurations.setup()
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
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



'''
Uses "tdrs-backend/scripts/db_backup.py" to perform a pg_dump of the existing PostGres database to a standard
location within our S3 bucket for this instance.
'''
# schedule, _ = CrontabSchedule.objects.get_or_create(
#     minute='5',
#     hour='*',
#     day_of_week='*',
#     day_of_month='*',
#     month_of_year='*',
# )
# PeriodicTask.objects.create(
#     crontab=schedule,
#     name="db_test",
#     task='tdpservice.scheduling.tasks.db_backup',
# )
