"""Celery configuration file."""
from __future__ import absolute_import
import os
import ssl
import configurations
import settings
from celery import Celery


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tdpservice.settings.cloudgov")
os.environ.setdefault("DJANGO_CONFIGURATION", "CloudGov")

configurations.setup()

app = Celery('settings')
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# disable ssl verification
if not settings.USE_LOCALSTACK:
    app.conf.update(
        broker_use_ssl={
            'ssl_cert_reqs': ssl.CERT_NONE,
        },
        redis_backend_use_ssl={
            'ssl_cert_reqs': ssl.CERT_NONE,
        },
    )

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
