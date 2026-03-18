"""Enums for the data_files app."""

from typing import Dict, Iterable

from django.db import models


class SubmissionState(models.TextChoices):
    """Lifecycle states for a submitted data file."""

    UPLOADED = "uploaded", "Uploaded"
    VIRUS_SCAN_STARTED = "virus_scan_started", "Virus scan started"
    VIRUS_SCAN_FAILED = "virus_scan_failed", "Virus scan failed"
    VIRUS_SCAN_SUCCESSFUL = "virus_scan_successful", "Virus scan successful"
    PARSE_STARTED = "parse_started", "Parse started"
    PARSED_WITH_ERRORS = "parsed_with_errors", "Parsed with errors"
    PARSE_COMPLETED = "parse_completed", "Parse completed"
    # Alias used in transition map naming for backward compatibility.
    PARSED_COMPLETED = "parse_completed", "Parse completed"
    STUCK = "stuck", "Stuck"
    COMPLETED = "completed", "Completed"
    CANCELED = "canceled", "Canceled"


ALLOWED_TRANSITIONS: Dict[SubmissionState, Iterable[SubmissionState]] = {
    SubmissionState.UPLOADED: {
        SubmissionState.VIRUS_SCAN_STARTED,
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_STARTED: {
        SubmissionState.VIRUS_SCAN_FAILED,
        SubmissionState.VIRUS_SCAN_SUCCESSFUL,
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_FAILED: {
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_SUCCESSFUL: {
        SubmissionState.PARSE_STARTED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSE_STARTED: {
        SubmissionState.PARSED_WITH_ERRORS,
        SubmissionState.PARSED_COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSED_WITH_ERRORS: {
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSED_COMPLETED: {
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.STUCK: {
        SubmissionState.CANCELED,
    },
    SubmissionState.COMPLETED: set(),
    SubmissionState.CANCELED: set(),
}
