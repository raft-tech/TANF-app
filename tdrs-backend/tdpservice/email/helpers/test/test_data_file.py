"""Test functions for data_file email helper."""

from datetime import datetime, timezone

from django.core import mail

import pytest

from tdpservice.data_files.enums import ProgramCode, SectionName
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.test.factories import canonical_section_for
from tdpservice.email.helpers.data_file import (
    get_pia_quarter_label,
    get_tanf_aggregates_context_count,
    get_tanf_total_errors_context_count,
    send_data_submitted_email,
    send_stuck_file_email,
)
from tdpservice.parsers.models import DataFileSummary


@pytest.mark.django_db
def test_send_data_submitted_email_no_email_for_pending(user, stt):
    """Test that send_data_submitted_email sends nothing for PENDING datafiles."""
    df = DataFile(
        user=user,
        section=canonical_section_for("TAN", SectionName.ACTIVE_CASE_DATA),
        quarter="Q1",
        year=2021,
        stt=stt,
    )

    dfs = DataFileSummary(
        datafile=df,
        status=DataFileSummary.Status.PENDING,
    )

    recipients = ["test@not-real.com"]

    send_data_submitted_email(dfs, recipients)

    assert len(mail.outbox) == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "section,status,subject,friendly_program_type,program_type,is_reprocessed",
    [
        # tribal
        (
            SectionName.CLOSED_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"Tribal {SectionName.CLOSED_CASE_DATA} Successfully Submitted Without Errors",
            "Tribal TANF",
            ProgramCode.TRIBAL,
            False,
        ),
        (
            SectionName.CLOSED_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"Tribal {SectionName.CLOSED_CASE_DATA} Submission Errors Resolved",
            "Tribal TANF",
            ProgramCode.TRIBAL,
            True,
        ),
        (
            SectionName.ACTIVE_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"Tribal {SectionName.ACTIVE_CASE_DATA} Successfully Submitted Without Errors",
            "Tribal TANF",
            ProgramCode.TRIBAL,
            False,
        ),
        (
            SectionName.ACTIVE_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"Tribal {SectionName.ACTIVE_CASE_DATA} Submission Errors Resolved",
            "Tribal TANF",
            ProgramCode.TRIBAL,
            True,
        ),
        (
            SectionName.AGGREGATE_DATA,
            DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
            f"Action Required: Tribal {SectionName.AGGREGATE_DATA} Contains Errors",
            "Tribal TANF",
            ProgramCode.TRIBAL,
            False,
        ),
        (
            SectionName.AGGREGATE_DATA,
            DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
            f"Action Required: Error Report Available for Tribal {SectionName.AGGREGATE_DATA} Submission",
            "Tribal TANF",
            ProgramCode.TRIBAL,
            True,
        ),
        (
            SectionName.STRATUM_DATA,
            DataFileSummary.Status.PARTIALLY_ACCEPTED,
            f"Action Required: Tribal {SectionName.STRATUM_DATA} Contains Errors",
            "Tribal TANF",
            ProgramCode.TRIBAL,
            False,
        ),
        (
            SectionName.STRATUM_DATA,
            DataFileSummary.Status.PARTIALLY_ACCEPTED,
            f"Action Required: Error Report Available for Tribal {SectionName.STRATUM_DATA} Submission",
            "Tribal TANF",
            ProgramCode.TRIBAL,
            True,
        ),
        (
            SectionName.STRATUM_DATA,
            DataFileSummary.Status.REJECTED,
            f"Action Required: Tribal {SectionName.STRATUM_DATA} Contains Errors",
            "Tribal TANF",
            ProgramCode.TRIBAL,
            False,
        ),
        (
            SectionName.STRATUM_DATA,
            DataFileSummary.Status.REJECTED,
            f"Action Required: Error Report Available for Tribal {SectionName.STRATUM_DATA} Submission",
            "Tribal TANF",
            ProgramCode.TRIBAL,
            True,
        ),
        # ssp
        (
            SectionName.AGGREGATE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"SSP {SectionName.AGGREGATE_DATA} Successfully Submitted Without Errors",
            "SSP",
            ProgramCode.SSP,
            False,
        ),
        (
            SectionName.AGGREGATE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"SSP {SectionName.AGGREGATE_DATA} Submission Errors Resolved",
            "SSP",
            ProgramCode.SSP,
            True,
        ),
        (
            SectionName.CLOSED_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"SSP {SectionName.CLOSED_CASE_DATA} Successfully Submitted Without Errors",
            "SSP",
            ProgramCode.SSP,
            False,
        ),
        (
            SectionName.CLOSED_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"SSP {SectionName.CLOSED_CASE_DATA} Submission Errors Resolved",
            "SSP",
            ProgramCode.SSP,
            True,
        ),
        (
            SectionName.ACTIVE_CASE_DATA,
            DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
            f"Action Required: SSP {SectionName.ACTIVE_CASE_DATA} Contains Errors",
            "SSP",
            ProgramCode.SSP,
            False,
        ),
        (
            SectionName.ACTIVE_CASE_DATA,
            DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
            f"Action Required: Error Report Available for SSP {SectionName.ACTIVE_CASE_DATA} Submission",
            "SSP",
            ProgramCode.SSP,
            True,
        ),
        (
            SectionName.STRATUM_DATA,
            DataFileSummary.Status.PARTIALLY_ACCEPTED,
            f"Action Required: SSP {SectionName.STRATUM_DATA} Contains Errors",
            "SSP",
            ProgramCode.SSP,
            False,
        ),
        (
            SectionName.STRATUM_DATA,
            DataFileSummary.Status.PARTIALLY_ACCEPTED,
            f"Action Required: Error Report Available for SSP {SectionName.STRATUM_DATA} Submission",
            "SSP",
            ProgramCode.SSP,
            True,
        ),
        (
            SectionName.STRATUM_DATA,
            DataFileSummary.Status.REJECTED,
            f"Action Required: SSP {SectionName.STRATUM_DATA} Contains Errors",
            "SSP",
            ProgramCode.SSP,
            False,
        ),
        (
            SectionName.STRATUM_DATA,
            DataFileSummary.Status.REJECTED,
            f"Action Required: Error Report Available for SSP {SectionName.STRATUM_DATA} Submission",
            "SSP",
            ProgramCode.SSP,
            True,
        ),
        # tanf
        (
            SectionName.ACTIVE_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"{SectionName.ACTIVE_CASE_DATA} Successfully Submitted Without Errors",
            "TANF",
            ProgramCode.TANF,
            False,
        ),
        (
            SectionName.ACTIVE_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"{SectionName.ACTIVE_CASE_DATA} Submission Errors Resolved",
            "TANF",
            ProgramCode.TANF,
            True,
        ),
        (
            SectionName.CLOSED_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"{SectionName.CLOSED_CASE_DATA} Successfully Submitted Without Errors",
            "TANF",
            ProgramCode.TANF,
            False,
        ),
        (
            SectionName.CLOSED_CASE_DATA,
            DataFileSummary.Status.ACCEPTED,
            f"{SectionName.CLOSED_CASE_DATA} Submission Errors Resolved",
            "TANF",
            ProgramCode.TANF,
            True,
        ),
        (
            SectionName.AGGREGATE_DATA,
            DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
            f"Action Required: {SectionName.AGGREGATE_DATA} Contains Errors",
            "TANF",
            ProgramCode.TANF,
            False,
        ),
        (
            SectionName.AGGREGATE_DATA,
            DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
            f"Action Required: Error Report Available for {SectionName.AGGREGATE_DATA} Submission",
            "TANF",
            ProgramCode.TANF,
            True,
        ),
        (
            SectionName.STRATUM_DATA,
            DataFileSummary.Status.PARTIALLY_ACCEPTED,
            f"Action Required: {SectionName.STRATUM_DATA} Contains Errors",
            "TANF",
            ProgramCode.TANF,
            False,
        ),
        (
            SectionName.STRATUM_DATA,
            DataFileSummary.Status.PARTIALLY_ACCEPTED,
            f"Action Required: Error Report Available for {SectionName.STRATUM_DATA} Submission",
            "TANF",
            ProgramCode.TANF,
            True,
        ),
        (
            SectionName.STRATUM_DATA,
            DataFileSummary.Status.REJECTED,
            f"Action Required: {SectionName.STRATUM_DATA} Contains Errors",
            "TANF",
            ProgramCode.TANF,
            False,
        ),
        (
            SectionName.STRATUM_DATA,
            DataFileSummary.Status.REJECTED,
            f"Action Required: Error Report Available for {SectionName.STRATUM_DATA} Submission",
            "TANF",
            ProgramCode.TANF,
            True,
        ),
        # fra
        (
            SectionName.FRA_WORK_OUTCOME_TANF_EXITERS,
            DataFileSummary.Status.ACCEPTED,
            f"{SectionName.FRA_WORK_OUTCOME_TANF_EXITERS} Successfully Submitted Without Errors",
            "FRA",
            ProgramCode.FRA,
            False,
        ),
        (
            SectionName.FRA_WORK_OUTCOME_TANF_EXITERS,
            DataFileSummary.Status.ACCEPTED,
            f"{SectionName.FRA_WORK_OUTCOME_TANF_EXITERS} Submission Errors Resolved",
            "FRA",
            ProgramCode.FRA,
            True,
        ),
        (
            SectionName.FRA_WORK_OUTCOME_TANF_EXITERS,
            DataFileSummary.Status.REJECTED,
            f"Action Required: {SectionName.FRA_WORK_OUTCOME_TANF_EXITERS} Contains Errors",
            "FRA",
            ProgramCode.FRA,
            False,
        ),
        (
            SectionName.FRA_WORK_OUTCOME_TANF_EXITERS,
            DataFileSummary.Status.REJECTED,
            f"Action Required: Error Report Available for {SectionName.FRA_WORK_OUTCOME_TANF_EXITERS} Submission",
            "FRA",
            ProgramCode.FRA,
            True,
        ),
    ],
)
def test_send_data_submitted_email(
    user,
    stt,
    section,
    status,
    subject,
    friendly_program_type,
    program_type,
    is_reprocessed,
):
    """Test that the send_data_submitted_email function runs."""
    df = DataFile(
        user=user,
        section=canonical_section_for(program_type, section),
        quarter="Q1",
        year=2021,
        stt=stt,
    )

    dfs = DataFileSummary(
        datafile=df,
        status=status,
    )

    recipients = ["test@not-real.com"]

    send_data_submitted_email(dfs, recipients, is_reprocessed)

    has_errors = status != DataFileSummary.Status.ACCEPTED
    has_errors_msg = (
        f"{friendly_program_type} has been submitted and processed with errors."
    )
    no_errors_msg = (
        f"{friendly_program_type} has been submitted and processed without errors."
    )
    msg = has_errors_msg if has_errors else no_errors_msg

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == subject
    assert mail.outbox[0].body == msg


_PIA_Q1_LABEL = "Quarter 1 (October - December)"
_PIA_FILE_TYPE = "TANF Program Integrity Audit"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status,expected_subject,expected_text,is_reprocessed",
    [
        (
            DataFileSummary.Status.ACCEPTED,
            f"{_PIA_FILE_TYPE}: {_PIA_Q1_LABEL} Successfully Submitted Without Errors",
            f"{_PIA_FILE_TYPE} has been submitted and processed without errors.",
            False,
        ),
        (
            DataFileSummary.Status.ACCEPTED,
            f"{_PIA_FILE_TYPE}: {_PIA_Q1_LABEL} Submission Errors Resolved",
            f"{_PIA_FILE_TYPE} has been submitted and processed without errors.",
            True,
        ),
        (
            DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
            f"Action Required: {_PIA_FILE_TYPE}: {_PIA_Q1_LABEL} Contains Errors",
            f"{_PIA_FILE_TYPE} has been submitted and processed with errors.",
            False,
        ),
        (
            DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
            f"Action Required: Error Report Available for {_PIA_FILE_TYPE}: {_PIA_Q1_LABEL} Submission",
            f"{_PIA_FILE_TYPE} has been submitted and processed with errors.",
            True,
        ),
        (
            DataFileSummary.Status.PARTIALLY_ACCEPTED,
            f"Action Required: {_PIA_FILE_TYPE}: {_PIA_Q1_LABEL} Contains Errors",
            f"{_PIA_FILE_TYPE} has been submitted and processed with errors.",
            False,
        ),
        (
            DataFileSummary.Status.PARTIALLY_ACCEPTED,
            f"Action Required: Error Report Available for {_PIA_FILE_TYPE}: {_PIA_Q1_LABEL} Submission",
            f"{_PIA_FILE_TYPE} has been submitted and processed with errors.",
            True,
        ),
        (
            DataFileSummary.Status.REJECTED,
            f"Action Required: {_PIA_FILE_TYPE}: {_PIA_Q1_LABEL} Contains Errors",
            f"{_PIA_FILE_TYPE} has been submitted and processed with errors.",
            False,
        ),
        (
            DataFileSummary.Status.REJECTED,
            f"Action Required: Error Report Available for {_PIA_FILE_TYPE}: {_PIA_Q1_LABEL} Submission",
            f"{_PIA_FILE_TYPE} has been submitted and processed with errors.",
            True,
        ),
    ],
)
def test_send_data_submitted_email_pia(
    user, stt, status, expected_subject, expected_text, is_reprocessed
):
    """Test that PIA submissions use distinct subjects, text, and quarter-based templates."""
    df = DataFile(
        user=user,
        section=canonical_section_for(
            ProgramCode.TANF,
            SectionName.ACTIVE_CASE_DATA,
        ),
        quarter=DataFile.Quarter.Q1,
        year=2021,
        stt=stt,
        is_program_audit=True,
    )

    dfs = DataFileSummary(datafile=df, status=status)

    send_data_submitted_email(dfs, ["test@not-real.com"], is_reprocessed)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == expected_subject
    assert mail.outbox[0].body == expected_text


class TestGetPiaQuarterLabel:
    """Tests for get_pia_quarter_label."""

    @pytest.mark.parametrize(
        "quarter,expected",
        [
            (DataFile.Quarter.Q1, "Quarter 1 (October - December)"),
            (DataFile.Quarter.Q2, "Quarter 2 (January - March)"),
            (DataFile.Quarter.Q3, "Quarter 3 (April - June)"),
            (DataFile.Quarter.Q4, "Quarter 4 (July - September)"),
        ],
    )
    def test_quarter_labels(self, quarter, expected):
        """Test that all quarters map to correct human-readable labels."""
        assert get_pia_quarter_label(quarter) == expected


class TestGetTanfAggregatesContextCount:
    """Tests for get_tanf_aggregates_context_count."""

    def test_with_case_data(self):
        """Test aggregation with typical case data months."""
        dfs = DataFileSummary()
        dfs.case_aggregates = {
            "months": [
                {
                    "month": "Jan",
                    "accepted_without_errors": 10,
                    "accepted_with_errors": 2,
                },
                {
                    "month": "Feb",
                    "accepted_without_errors": 8,
                    "accepted_with_errors": 3,
                },
                {
                    "month": "Mar",
                    "accepted_without_errors": 12,
                    "accepted_with_errors": 1,
                },
            ],
            "rejected": 5,
        }
        result = get_tanf_aggregates_context_count(dfs)
        assert result == {
            "cases_without_errors": 30,
            "cases_with_errors": 6,
            "records_unable_to_process": 5,
        }

    def test_with_na_values(self):
        """Test aggregation handles N/A values from rejected status."""
        dfs = DataFileSummary()
        dfs.case_aggregates = {
            "months": [
                {
                    "month": "Jan",
                    "accepted_without_errors": "N/A",
                    "accepted_with_errors": "N/A",
                },
            ],
            "rejected": 0,
        }
        result = get_tanf_aggregates_context_count(dfs)
        assert result == {
            "cases_without_errors": 0,
            "cases_with_errors": 0,
            "records_unable_to_process": 0,
        }

    def test_with_empty_aggregates(self):
        """Test aggregation handles empty/None case_aggregates."""
        dfs = DataFileSummary()
        dfs.case_aggregates = None
        result = get_tanf_aggregates_context_count(dfs)
        assert result == {
            "cases_without_errors": 0,
            "cases_with_errors": 0,
            "records_unable_to_process": 0,
        }


class TestGetTanfTotalErrorsContextCount:
    """Tests for get_tanf_total_errors_context_count."""

    def test_with_total_errors_data(self):
        """Test aggregation sums total_errors across months."""
        dfs = DataFileSummary()
        dfs.case_aggregates = {
            "months": [
                {"month": "Jan", "total_errors": 5},
                {"month": "Feb", "total_errors": 3},
                {"month": "Mar", "total_errors": 7},
            ],
        }
        result = get_tanf_total_errors_context_count(dfs)
        assert result == {"total_errors": 15}

    def test_with_na_values(self):
        """Test aggregation handles N/A values from rejected status."""
        dfs = DataFileSummary()
        dfs.case_aggregates = {
            "months": [
                {"month": "Jan", "total_errors": "N/A"},
                {"month": "Feb", "total_errors": "N/A"},
            ],
        }
        result = get_tanf_total_errors_context_count(dfs)
        assert result == {"total_errors": 0}

    def test_with_empty_aggregates(self):
        """Test aggregation handles empty/None case_aggregates."""
        dfs = DataFileSummary()
        dfs.case_aggregates = None
        result = get_tanf_total_errors_context_count(dfs)
        assert result == {"total_errors": 0}

    def test_with_mixed_values(self):
        """Test aggregation handles mix of numeric and N/A values."""
        dfs = DataFileSummary()
        dfs.case_aggregates = {
            "months": [
                {"month": "Jan", "total_errors": 5},
                {"month": "Feb", "total_errors": "N/A"},
                {"month": "Mar", "total_errors": 10},
            ],
        }
        result = get_tanf_total_errors_context_count(dfs)
        assert result == {"total_errors": 15}


@pytest.mark.django_db
def test_send_stuck_file_email(user, stt):
    """Test that the send_stuck_file_email function runs."""

    df1 = DataFile(
        user=user,
        section=canonical_section_for(
            ProgramCode.TANF,
            SectionName.ACTIVE_CASE_DATA,
        ),
        quarter="Q1",
        year=2025,
        stt=stt,
    )
    df2 = DataFile(
        user=user,
        section=canonical_section_for(
            ProgramCode.TANF,
            SectionName.CLOSED_CASE_DATA,
        ),
        quarter="Q1",
        year=2025,
        stt=stt,
    )
    stuck_files = [df1, df2]

    recipients = ["test@not-real.com"]

    send_stuck_file_email(stuck_files, recipients)

    assert len(mail.outbox) == 1
    assert (
        mail.outbox[0].subject
        == "List of submitted files with pending status after 1 hour"
    )
    assert mail.outbox[0].body == "The system has detected stuck files."


@pytest.mark.django_db
def test_submission_date_formatted_in_stt_timezone(user, stt):
    """Test that the email submission_date is formatted in the STT's timezone."""
    stt.timezone = "America/Chicago"
    stt.save()

    df = DataFile.objects.create(
        user=user,
        section=canonical_section_for("TAN", SectionName.ACTIVE_CASE_DATA),
        quarter="Q1",
        year=2021,
        version=1,
        stt=stt,
    )
    # Override created_at to a known UTC time (2024-01-15 18:00 UTC = 12:00 PM CST)
    DataFile.objects.filter(pk=df.pk).update(
        created_at=datetime(2024, 1, 15, 18, 0, 0, tzinfo=timezone.utc)
    )
    df.refresh_from_db()

    dfs = DataFileSummary.objects.create(
        datafile=df,
        status=DataFileSummary.Status.ACCEPTED,
    )

    send_data_submitted_email(dfs, ["test@not-real.com"])

    assert len(mail.outbox) == 1
    body = mail.outbox[0].alternatives[0][0]  # HTML body
    assert "01/15/2024 12:00 PM CST" in body


@pytest.mark.django_db
def test_submission_date_formatted_in_eastern_timezone(user, stt):
    """Test that Eastern timezone formatting includes EST/EDT label."""
    stt.timezone = "America/New_York"
    stt.save()

    df = DataFile.objects.create(
        user=user,
        section=canonical_section_for("TAN", SectionName.ACTIVE_CASE_DATA),
        quarter="Q1",
        year=2021,
        version=1,
        stt=stt,
    )
    # 2024-01-15 18:00 UTC = 1:00 PM EST (January, so EST not EDT)
    DataFile.objects.filter(pk=df.pk).update(
        created_at=datetime(2024, 1, 15, 18, 0, 0, tzinfo=timezone.utc)
    )
    df.refresh_from_db()

    dfs = DataFileSummary.objects.create(
        datafile=df,
        status=DataFileSummary.Status.ACCEPTED,
    )

    send_data_submitted_email(dfs, ["test@not-real.com"])

    assert len(mail.outbox) == 1
    body = mail.outbox[0].alternatives[0][0]
    assert "01/15/2024 01:00 PM EST" in body


@pytest.mark.django_db
def test_submission_date_utc_fallback_when_no_timezone(user, stt):
    """Test that submission_date falls back to UTC when STT has no timezone."""
    stt.timezone = ""
    stt.save()

    df = DataFile.objects.create(
        user=user,
        section=canonical_section_for("TAN", SectionName.ACTIVE_CASE_DATA),
        quarter="Q1",
        year=2021,
        version=1,
        stt=stt,
    )
    DataFile.objects.filter(pk=df.pk).update(
        created_at=datetime(2024, 1, 15, 18, 0, 0, tzinfo=timezone.utc)
    )
    df.refresh_from_db()

    dfs = DataFileSummary.objects.create(
        datafile=df,
        status=DataFileSummary.Status.ACCEPTED,
    )

    send_data_submitted_email(dfs, ["test@not-real.com"])

    assert len(mail.outbox) == 1
    body = mail.outbox[0].alternatives[0][0]
    assert "01/15/2024 06:00 PM UTC" in body
