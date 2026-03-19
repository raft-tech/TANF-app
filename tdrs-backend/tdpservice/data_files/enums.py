"""Enums for the data_files app."""

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
    STUCK = "stuck", "Stuck"
    COMPLETED = "completed", "Completed"
    CANCELED = "canceled", "Canceled"
