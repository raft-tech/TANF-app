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
            Q(summary=None)
            | Q(summary__status=DataFileSummary.Status.PENDING)
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
<<<<<<< HEAD
    """Apply AV scan completion result and queue parsing if scan passed.

    This task updates the DataFile state based on the scan result and
    automatically queues the parsing task if the scan completed successfully.

    Args:
        data_file_id: ID of the DataFile to update
        scan_result: Scan result (CLEAN, INFECTED, ERROR, etc.)
        note: Optional note for logging
=======
    """Apply AV completion result for a DataFile from async callbacks/tasks.
    
    When a DataFile successfully completes AV scanning (transitions to VIRUS_SCAN_COMPLETED),
    this task will automatically queue the parsing task to continue the submission workflow.
>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b
    """
    try:
        data_file = DataFile.objects.get(id=data_file_id)
    except DataFile.DoesNotExist:
<<<<<<< HEAD
        logger.error(f"DataFile with id {data_file_id} not found for AV scan completion")
        return

    completion_note = note or f"AV scan completed with result: {scan_result}"

    # Apply the scan result to the DataFile state
    data_file, transition_occurred = complete_datafile_av_scan(
=======
        logger.error(f"DataFile with id {data_file_id} not found")
        return

    completion_note = note or "AV completion task received scan result"

    complete_datafile_av_scan(
>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b
        data_file,
        scan_result=scan_result,
        note=completion_note,
    )

    logger.info(
<<<<<<< HEAD
        "Processed AV scan completion for data_file_id=%s with result=%s, transition_occurred=%s",
        data_file_id,
        scan_result,
        transition_occurred,
    )

    # Only queue parse if we actually transitioned to VIRUS_SCAN_COMPLETED
    # This prevents duplicate parse queueing from duplicate or out-of-order scan results
    if transition_occurred and data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED:
        logger.info(
            f"AV scan passed for data_file_id={data_file_id}, queuing parse task"
        )
        parser_task.parse.delay(data_file_id)
        logger.info("Queued parse task for datafile %s", data_file_id)
    elif data_file.state == SubmissionState.VIRUS_SCAN_FAILED:
        logger.warning(
            f"AV scan failed for data_file_id={data_file_id}, state is {data_file.state}. "
            "Parse task not queued."
        )
        
        # Delete the infected/unsafe file from storage to prevent persistence of malicious content
        if transition_occurred and data_file.file:
            try:
                file_path = data_file.file.name
                data_file.file.delete(save=True)
                logger.info(
                    f"Deleted failed scan file for data_file_id={data_file_id}, path={file_path}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to delete file for data_file_id={data_file_id}: {e}",
                    exc_info=True,
                )
=======
        "Processed AV completion task for data_file_id=%s with scan_result=%s",
        data_file_id,
        scan_result,
    )

    # Refresh the state after transition
    data_file.refresh_from_db(fields=["state"])

    # If scan passed, queue the parse task to continue the workflow
    if data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED:
        logger.info(
            f"AV scan passed for data_file_id={data_file_id}, queuing parse task."
        )
        parser_task.parse.delay(data_file_id)
        logger.info("Submitted parse task to queue for datafile %s.", data_file_id)
    else:
        logger.warning(
            f"AV scan failed for data_file_id={data_file_id}, state is {data_file.state}. "
            f"Parse task not queued."
        )

>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b


@shared_task
def scan_datafile_for_virus(data_file_id):
<<<<<<< HEAD
    """Perform ClamAV virus scan on a DataFile and queue completion task.

    This task performs the actual virus scanning and then queues the
    completion task to apply the scan result to the DataFile state.

    Args:
        data_file_id: ID of the DataFile to scan
=======
    """Perform ClamAV virus scan on a DataFile and apply the result to submission state.
    
    This task performs the actual virus scan and transitions the DataFile state
    based on the scan result. The scan result is recorded in ClamAVFileScan and
    the completion is handled via complete_av_scan_for_datafile.
>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b
    """
    try:
        data_file = DataFile.objects.get(id=data_file_id)
    except DataFile.DoesNotExist:
<<<<<<< HEAD
        logger.error(f"DataFile with id {data_file_id} not found for virus scan")
        return

    try:
        # Check if ClamAV scanning is enabled
=======
        logger.error(f"DataFile with id {data_file_id} not found")
        return

    try:
>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b
        if not settings.CLAMAV_NEEDED:
            logger.debug(
                f"CLAMAV_NEEDED is False, skipping virus scan for data_file_id={data_file_id}"
            )
            complete_av_scan_for_datafile.delay(
                data_file_id,
                scan_result="clean",
<<<<<<< HEAD
                note="Skipped AV scan (CLAMAV_NEEDED=False)",
=======
                note="Skipping AV scan (CLAMAV_NEEDED=False)",
>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b
            )
            return

        logger.debug(f"Starting virus scan for data_file_id={data_file_id}")
<<<<<<< HEAD

        # Perform the actual ClamAV scan
=======
        
>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b
        client = ClamAVClient()
        is_file_clean = client.scan_file(
            file=data_file.file,
            file_name=data_file.original_filename,
            uploaded_by=data_file.user,
            data_file=data_file,
        )

<<<<<<< HEAD
        # Retrieve the most recent scan result from the database
        latest_scan = (
            ClamAVFileScan.objects.filter(data_file=data_file)
            .order_by("-scanned_at")
            .first()
        )
=======
        # Retrieve the most recent scan result for this data file
        latest_scan = ClamAVFileScan.objects.filter(
            data_file=data_file
        ).order_by("-scanned_at").first()
>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b

        if latest_scan:
            scan_result = latest_scan.result.lower()
            note = f"AV scan completed with result: {latest_scan.result}"
        else:
            # Fallback if scan record not found (shouldn't happen)
            scan_result = "clean" if is_file_clean else "infected"
            note = "AV scan completed"

        logger.info(
            f"Virus scan completed for data_file_id={data_file_id} with result={scan_result}"
        )

        # Queue the completion task to apply state transition
        complete_av_scan_for_datafile.delay(
            data_file_id,
            scan_result=scan_result,
            note=note,
        )

    except ClamAVClient.ServiceUnavailable:
        logger.error(
<<<<<<< HEAD
            f"ClamAV service unavailable for data_file_id={data_file_id}, marking scan as error"
=======
            f"ClamAV service unavailable for data_file_id={data_file_id}",
            exc_info=True,
>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b
        )
        complete_av_scan_for_datafile.delay(
            data_file_id,
            scan_result="error",
<<<<<<< HEAD
            note="ClamAV service unavailable",
        )

    except Exception as e:
        logger.exception(
            f"Unexpected error during virus scan for data_file_id={data_file_id}: {e}"
        )
        complete_av_scan_for_datafile.delay(
            data_file_id,
            scan_result="error",
            note=f"Scan error: {str(e)}",
        )
=======
            note="AV scan failed: ClamAV service unavailable",
        )
    except Exception as e:
        logger.error(
            f"Unexpected error during virus scan for data_file_id={data_file_id}: {e}",
            exc_info=True,
        )
        complete_av_scan_for_datafile.delay(
            data_file_id,
            scan_result="error",
            note=f"AV scan failed: {str(e)}",
        )

>>>>>>> 374a0a78b84497f675ca930ce9fc1d6900b8b18b
