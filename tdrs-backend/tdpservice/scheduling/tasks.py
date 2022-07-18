from __future__ import absolute_import
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def upload(a,b):
    return a*b

@shared_task
def echo():
    logger.debug("This is the echo function.")
    return True
