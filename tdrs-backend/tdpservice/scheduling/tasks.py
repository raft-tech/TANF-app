from __future__ import absolute_import
from celery import shared_task
from django.conf import settings

import paramiko

'''

from django.utils import timezone
last_24 = timezone.now()-timezone.timedelta(hours=24)
DataFile.objects.filter(created_at__gt=last_24)

# what should the filename be?
with open('write.txt','wb') as f1:
     ...:     with df.file.file.open() as f2:
     ...:         f1.write(f2.read())


# ssh connect and command
_stdin, _stdout,_stderr = transport.exec_command("ls")
print(_stdout.read().decode())

1) try to create directory
if successful, then good,
if not, then either directory exists, or something else happened.
    in case of error, we can list the directories, and confirm if it exists, or we can do this first

2) Query DISTINCT values based on year, STT

NEW: Do not need this anymore. Should schedule an upload to the server as soon as the file is uploaded.
However, we will need the file information, to know where it is being uploaded.
'''

import logging
logger = logging.getLogger(__name__)

@shared_task
def run_backup(b):
    """    No params, setup for actual backup call. """
    logger.debug("my arg was" + b)
