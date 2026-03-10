"""Enums for the data_files app."""

from django.db import models


class SubmissionState(models.TextChoices):
    """Lifecycle states for a submitted data file."""

    UPLOADED = "uploaded", "Uploaded"
    VIRUS_SCANNING = "virus_scanning", "Virus scanning"
    SCAN_FAILED = "scan_failed", "Scan failed"
    VALIDATED = "validated", "Validated"
    PARSING = "parsing", "Parsing"
    PARSED_WITH_ERRORS = "parsed_with_errors", "Parsed with errors"
    PARSED_CLEAN = "parsed_clean", "Parsed clean"
    INGESTING = "ingesting", "Ingesting"
    INGEST_FAILED = "ingest_failed", "Ingest failed"
    STUCK = "stuck", "Stuck"
    COMPLETED = "completed", "Completed"
    CANCELED = "canceled", "Canceled"
