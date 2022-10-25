"""Shared celery tasks file for beat."""
from __future__ import absolute_import
from celery import shared_task
import logging
from .db_backup import run_backup

logger = logging.getLogger(__name__)

@shared_task
def postgres_backup(*args):
    """Run nightly postgres backup."""
    arg = ''.join(args)
    logger.debug("We have nightly registered w/ arg: " + arg)
    run_backup(arg)
    return True
