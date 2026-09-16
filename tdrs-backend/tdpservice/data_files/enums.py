"""Enums for the data_files app."""

from django.db import models


class ProgramCode(models.TextChoices):
    """Canonical Program codes used outside the transitional DataFile schema."""

    TANF = "TAN"
    SSP = "SSP"
    TRIBAL = "TRIBAL"
    FRA = "FRA"


class SectionName(models.TextChoices):
    """Canonical Section names used by application and parser contracts."""

    ACTIVE_CASE_DATA = "Active Case Data"
    CLOSED_CASE_DATA = "Closed Case Data"
    AGGREGATE_DATA = "Aggregate Data"
    STRATUM_DATA = "Stratum Data"
    FRA_WORK_OUTCOME_TANF_EXITERS = "Work Outcomes of TANF Exiters"
    FRA_SECONDRY_SCHOOL_ATTAINMENT = "Secondary School Attainment"
    FRA_SUPPLEMENT_WORK_OUTCOMES = "Supplemental Work Outcomes"

    @classmethod
    def is_fra(cls, section: str) -> bool:
        """Return whether a section belongs to FRA."""
        return section in {
            cls.FRA_WORK_OUTCOME_TANF_EXITERS,
            cls.FRA_SECONDRY_SCHOOL_ATTAINMENT,
            cls.FRA_SUPPLEMENT_WORK_OUTCOMES,
        }


class SubmissionState(models.TextChoices):
    """Lifecycle states for a submitted data file."""

    UPLOADED = "uploaded", "Uploaded"
    VIRUS_SCAN_STARTED = "virus_scan_started", "Virus scan started"
    VIRUS_SCAN_FAILED = "virus_scan_failed", "Virus scan failed"
    VIRUS_SCAN_COMPLETED = "virus_scan_completed", "Virus scan completed"
    REPARSE_REQUESTED = "reparse_requested", "Reparse requested"
    PARSE_STARTED = "parse_started", "Parse started"
    PARSE_FAILED = "parse_failed", "Parse failed"
    PARSED_WITH_ERRORS = "parsed_with_errors", "Parsed with errors"
    PARSE_COMPLETED = "parse_completed", "Parse completed"
    STUCK = "stuck", "Stuck"
    COMPLETED = "completed", "Completed"
    CANCELED = "canceled", "Canceled"
