"""Test stuck file notification queries and rendering."""

from django.contrib.admin.models import LogEntry
from django.core import mail

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.tasks import get_current_fiscal_year, get_stuck_files
from tdpservice.email.helpers.data_file import send_stuck_file_email
from tdpservice.parsers.models import DataFileSummary
from tdpservice.parsers.test.factories import (
    DataFileSummaryFactory,
    ParsingFileFactory,
)


def make_datafile(stt_user, stt, version, state=SubmissionState.UPLOADED, year=None):
    """Create a test data file with default params."""
    return ParsingFileFactory.create(
        quarter=DataFile.Quarter.Q1,
        section=DataFile.Section.ACTIVE_CASE_DATA,
        year=year or get_current_fiscal_year(),
        version=version,
        user=stt_user,
        stt=stt,
        state=state,
    )


def make_summary(datafile, status):
    """Create a test data file summary given a file and status."""
    return DataFileSummaryFactory.create(
        datafile=datafile,
        status=status,
    )


@pytest.mark.django_db
def test_stuck_current_fiscal_year_file_is_included(stt_user, stt):
    """Finds current fiscal year files explicitly marked stuck."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.STUCK,
    )

    stuck_files = get_stuck_files()

    assert list(stuck_files.values_list("pk", flat=True)) == [datafile.pk]


@pytest.mark.django_db
def test_non_stuck_current_fiscal_year_files_with_missing_or_pending_summary_are_excluded(
    stt_user,
    stt,
):
    """Ignores missing or PENDING summaries unless the file state is stuck."""
    make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    pending_summary_file = make_datafile(
        stt_user,
        stt,
        2,
        state=SubmissionState.UPLOADED,
    )
    make_summary(pending_summary_file, DataFileSummary.Status.PENDING)

    stuck_files = get_stuck_files()

    assert stuck_files.count() == 0


@pytest.mark.django_db
def test_stuck_file_outside_current_fiscal_year_is_excluded(stt_user, stt):
    """Ignores stuck files outside the current fiscal year."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.STUCK,
        year=get_current_fiscal_year() - 1,
    )

    stuck_files = get_stuck_files()

    assert datafile.pk not in stuck_files.values_list("pk", flat=True)
    assert stuck_files.count() == 0


@pytest.mark.django_db
def test_stuck_file_email_rendering_includes_state(stt_user, stt):
    """Renders each stuck file's DataFile.state value."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.STUCK,
    )

    send_stuck_file_email([datafile], ["recipient@example.com"])

    assert len(mail.outbox) == 1
    html_body = mail.outbox[0].alternatives[0][0]
    assert ">State<" in html_body
    assert f">{SubmissionState.STUCK.value}<" in html_body


@pytest.mark.django_db
def test_send_stuck_file_email(mocker):
    """Test send_stuck_file_email logging."""
    mocker.patch("tdpservice.email.email.automated_email", return_value=True)

    send_stuck_file_email([], ["recipient"])
    entries = LogEntry.objects.all().order_by("pk")
    assert len(entries) == 4
    assert entries[0].change_message == (
        "Emailing stuck files to SysAdmins: ['recipient']"
    )
