"""Celery hook for parsing tasks."""
from __future__ import absolute_import
from celery import shared_task
import logging
from django.contrib.auth.models import Group
from tdpservice.users.models import AccountApprovalStatusChoices, User
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.parse import parse_datafile
from tdpservice.parsers.models import DataFileSummary
from tdpservice.parsers.aggregates import case_aggregates_by_month, total_errors_by_month
from tdpservice.email.helpers.data_file import send_data_submitted_email


logger = logging.getLogger(__name__)


@shared_task
def parse(data_file_id):
    """Send data file for processing."""
    # passing the data file FileField across redis was rendering non-serializable failures, doing the below lookup
    # to avoid those. I suppose good practice to not store/serializer large file contents in memory when stored in redis
    # for undetermined amount of time.
    data_file = DataFile.objects.get(id=data_file_id)

    logger.info(f"DataFile parsing started for file {data_file.filename}")

    dfs = DataFileSummary.objects.create(datafile=data_file, status=DataFileSummary.Status.PENDING)
    errors = parse_datafile(data_file, dfs)
    dfs.status = dfs.get_status()

    if "Case Data" in data_file.section:
        dfs.case_aggregates = case_aggregates_by_month(data_file, dfs.status)
    else:
        dfs.case_aggregates = total_errors_by_month(data_file, dfs.status)

    dfs.save()

    logger.info(f"Parsing finished for file -> {repr(data_file)} with status {dfs.status} and {len(errors)} errors.")

    recipients = User.objects.filter(
        stt=data_file.stt,
        account_approval_status=AccountApprovalStatusChoices.APPROVED,
        groups=Group.objects.get(name='Data Analyst')
    ).values_list('username', flat=True).distinct()

    send_data_submitted_email(dfs, recipients)
