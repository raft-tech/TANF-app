from __future__ import absolute_import
from celery import shared_task
import logging
#from ...scripts.db_backup import backup_database,


logger = logging.getLogger(__name__)

@shared_task
def upload(a,b):
    return a*b

# @shared_task
# def echo():
#     logger.debug("This is the echo function.")
#     return True

@shared_task
def run_backup(b):
    logger.debug("my arg was"+b)
    #db_backup.handle_args(["-b"]) # TODO: capture output and log it
    return True
