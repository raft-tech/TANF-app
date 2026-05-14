"""Celery shared tasks for use in scheduled jobs."""

import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models import Count, Q
from django.utils import timezone

from celery import shared_task

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.submission_lifecycle import complete_datafile_av_scan
from tdpservice.email.helpers.data_file import send_stuck_file_email
from tdpservice.parsers.models import DataFileSummary
from tdpservice.scheduling import parser_task
from tdpservice.search_indexes.reparse import clean_reparse
from tdpservice.security.clients import ClamAVClient
from tdpservice.security.models import ClamAVFileScan
from tdpservice.users.models import AccountApprovalStatusChoices, User

logger = logging.getLogger(__name__)
ClamAVServiceUnavailable = ClamAVClient.ServiceUnavailable


def get_stuck_files():
    """Return a queryset containing files in a 'stuck' state."""
    stuck_files = (
        DataFile.objects.annotate(reparse_count=Count("reparses"))
        .filter(
            # non-reparse submissions over an hour old
            Q(
                reparse_count=0,
                created_at__lte=timezone.now() - timedelta(hours=1),
            )
            |  # OR
            # reparse submissions past the timeout, where the reparse did not complete
            Q(
                reparse_count__gt=0,
                reparses__timeout_at__lte=timezone.now(),
                reparse_file_metas__finished=False,
                reparse_file_metas__success=False,
            )
        )
        .filter(
            # where there is NO summary or the summary is in PENDING status
            Q(summary=None) | Q(summary__status=DataFileSummary.Status.PENDING)
        )
    )

    return stuck_files


@shared_task
def notify_stuck_files():
    """Find files stuck in 'Pending' and notify SysAdmins."""
    stuck_files = get_stuck_files()

    if stuck_files.count() > 0:
        recipients = (
            User.objects.filter(
                account_approval_status=AccountApprovalStatusChoices.APPROVED,
                groups=Group.objects.get(name="OFA System Admin"),
            )
            .values_list("username", flat=True)
            .distinct()
        )

        send_stuck_file_email(stuck_files, recipients)


@shared_task
def reparse_files(file_ids):
    """Call the clean_and_reparse management command with a list of file ids."""
    file_ids_str = ",".join(map(str, file_ids))
    clean_reparse([file_ids_str])


@shared_task
def complete_av_scan_for_datafile(data_file_id, scan_result, note=""):
    """Apply AV scan completion result and queue parsing if the scan passed."""
    try:
        data_file = DataFile.objects.get(id=data_file_id)
    except DataFile.DoesNotExist:
        logger.error(
            "DataFile with id %s not found for AV scan completion",
            data_file_id,
            extra={"data_file_id": data_file_id, "scan_result": scan_result},
        )
        return

    completion_note = note or f"AV scan completed with result: {scan_result}"
    data_file, transition_occurred = complete_datafile_av_scan(
        data_file,
        scan_result=scan_result,
        note=completion_note,
    )

    logger.info(
        "Processed AV scan completion for data_file_id=%s with result=%s, transition_occurred=%s",
        data_file_id,
        scan_result,
        transition_occurred,
        extra={
            "data_file_id": data_file_id,
            "scan_result": scan_result,
            "transition_occurred": transition_occurred,
            "current_state": data_file.state,
        },
    )

    if transition_occurred and data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED:
        logger.info(
            "AV scan passed for data_file_id=%s, queuing parse task",
            data_file_id,
            extra={"data_file_id": data_file_id, "scan_result": scan_result},
        )
        parser_task.parse.delay(data_file_id)
        logger.info("Queued parse task for datafile %s", data_file_id)
        return

    if transition_occurred and data_file.state == SubmissionState.VIRUS_SCAN_FAILED:
        logger.warning(
            "AV scan failed for data_file_id=%s; parse task not queued",
            data_file_id,
            extra={"data_file_id": data_file_id, "scan_result": scan_result},
        )
        if data_file.file:
            try:
                file_path = data_file.file.name
                data_file.file.delete(save=True)
                logger.info(
                    "Deleted failed scan file for data_file_id=%s, path=%s",
                    data_file_id,
                    file_path,
                    extra={"data_file_id": data_file_id, "file_path": file_path},
                )
            except Exception as e:
                logger.error(
                    "Failed to delete file for data_file_id=%s: %s",
                    data_file_id,
                    e,
                    exc_info=True,
                    extra={"data_file_id": data_file_id},
                )


@shared_task
def scan_datafile_for_virus(data_file_id):
    """Perform ClamAV virus scan on a DataFile and queue completion handling."""
    try:
        data_file = DataFile.objects.get(id=data_file_id)
    except DataFile.DoesNotExist:
        logger.error(
            "DataFile with id %s not found for virus scan",
            data_file_id,
            extra={"data_file_id": data_file_id},
        )
        return

    try:
        if not settings.CLAMAV_NEEDED:
            logger.debug(
                "CLAMAV_NEEDED is False, skipping virus scan for data_file_id=%s",
                data_file_id,
                extra={"data_file_id": data_file_id},
            )
            complete_av_scan_for_datafile.delay(
                data_file_id,
                scan_result="clean",
                note="Skipped AV scan (CLAMAV_NEEDED=False)",
            )
            return

        logger.debug(
            "Starting virus scan for data_file_id=%s",
            data_file_id,
            extra={"data_file_id": data_file_id},
        )
        client = ClamAVClient()
        is_file_clean = client.scan_file(
            file=data_file.file,
            file_name=data_file.original_filename,
            uploaded_by=data_file.user,
            data_file=data_file,
        )

        latest_scan = (
            ClamAVFileScan.objects.filter(data_file=data_file)
            .order_by("-scanned_at")
            .first()
        )

        if latest_scan:
            scan_result = latest_scan.result.lower()
            note = f"AV scan completed with result: {latest_scan.result}"
        else:
            scan_result = "clean" if is_file_clean else "infected"
            note = "AV scan completed"

        logger.info(
            "Virus scan completed for data_file_id=%s with result=%s",
            data_file_id,
            scan_result,
            extra={"data_file_id": data_file_id, "scan_result": scan_result},
        )

        complete_av_scan_for_datafile.delay(
            data_file_id,
            scan_result=scan_result,
            note=note,
        )

    except ClamAVServiceUnavailable:
        logger.error(
            "ClamAV service unavailable for data_file_id=%s",
            data_file_id,
            exc_info=True,
            extra={"data_file_id": data_file_id, "scan_result": "error"},
        )
        complete_av_scan_for_datafile.delay(
            data_file_id,
            scan_result="error",
            note="AV scan failed: ClamAV service unavailable",
        )
    except Exception as e:
        logger.error(
            "Unexpected error during virus scan for data_file_id=%s: %s",
            data_file_id,
            e,
            exc_info=True,
            extra={"data_file_id": data_file_id, "scan_result": "error"},
        )
        complete_av_scan_for_datafile.delay(
            data_file_id,
            scan_result="error",
            note=f"AV scan failed: {str(e)}",
        )
