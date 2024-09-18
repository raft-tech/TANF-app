"""
Discover files stuck in a 'Pending' status and notify System Administrators.
"""

from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import Group
from tdpservice.core.utils import log
from django.contrib.admin.models import ADDITION
from tdpservice.users.models import AccountApprovalStatusChoices, User
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.models import DataFileSummary
from tdpservice.email.helpers.data_file import send_stuck_file_email


class Command(BaseCommand):
    """Find files stuck in 'Pending' and notify SysAdmins."""

    def handle(self, *args, **options):
        recipients = User.objects.filter(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
            groups=Group.objects.get(name='OFA System Admin')
        ).values_list('username', flat=True).distinct()

        stuck_files = DataFile.objects.filter(
            created_at__lte=datetime.now(tz=timezone.utc) - timedelta(hours=0, seconds=10),
            summary__status=DataFileSummary.Status.PENDING,
        )

        # where no summary created?
        # where celery task not still running?

        for file in stuck_files:
            print(f'file {file.pk} stuck')

        send_stuck_file_email(stuck_files, recipients)
