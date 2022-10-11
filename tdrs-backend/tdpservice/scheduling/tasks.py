from tdpservice.users.models import User

from __future__ import absolute_import
from celery import shared_task
from datetime import datetime
import logging


logger = logging.getLogger(__name__)

@shared_task
def check_for_accounts_needing_deactivation_warning(*args):
    arg = ''.join(args)
    logger.debug("We have nightly registered w/ arg: " + arg)
    users = User.objects.filter(last_login__lte=datetime.now())
    return True