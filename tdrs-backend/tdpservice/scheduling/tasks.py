from __future__ import absolute_import
from tdpservice.users.models import User

from django.utils import timezone
from celery import shared_task
from datetime import datetime, timedelta
import logging
from tdpservice.email.email import send_deactivation_warning_email


logger = logging.getLogger(__name__)

@shared_task
def check_for_accounts_needing_deactivation_warning():
    deactivate_in_10_days = User.objects.filter(last_login__lte=datetime.now(tz=timezone.utc) - timedelta(days=170)).filter(last_login__gte=datetime.now(tz=timezone.utc) - timedelta(days=171))
    deactivate_in_3_days = User.objects.filter(last_login__lte=datetime.now(tz=timezone.utc) - timedelta(days=177)).filter(last_login__gte=datetime.now(tz=timezone.utc) - timedelta(days=178))
    deactivate_in_1_day = User.objects.filter(last_login__lte=datetime.now(tz=timezone.utc) - timedelta(days=179)).filter(last_login__gte=datetime.now(tz=timezone.utc) - timedelta(days=180))

    if deactivate_in_10_days:
        send_deactivation_warning_email(deactivate_in_10_days, 10)
    if deactivate_in_3_days:
        send_deactivation_warning_email(deactivate_in_3_days, 3)
    if deactivate_in_1_day:
        send_deactivation_warning_email(deactivate_in_1_day, 1)
