"""Test stuck file notification queries and rendering."""

from datetime import datetime, timedelta
from datetime import timezone as datetime_timezone

from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.core import mail
from django.utils import timezone

import pytest
from pytest_mock import MockerFixture

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile, Program, Section
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.data_files.tasks import (
    get_stale_lifecycle_files,
    get_stuck_files,
    mark_stale_files_stuck,
    notify_stuck_files,
)
from tdpservice.email.helpers.data_file import send_stuck_file_email
from tdpservice.parsers.models import DataFileSummary
from tdpservice.parsers.test.factories import (
    DataFileSummaryFactory,
    ReparseMetaFactory,
)
from tdpservice.stts.models import STT
from tdpservice.users.models import User


def make_datafile(
    stt_user: User,
    stt: STT,
    version: int,
    state: SubmissionState = SubmissionState.UPLOADED,
    year: int = 2026,
) -> DataFile:
    """Create a test data file with default params."""
    return DataFileFactory.create(
        quarter=DataFile.Quarter.Q1,
        section=Section.Name.ACTIVE_CASE_DATA,
        year=year,
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


def set_created_at(datafile, created_at):
    """Set legacy creation and lifecycle timestamps for stale-query tests."""
    DataFile.objects.filter(pk=datafile.pk).update(
        created_at=created_at,
        state_changed_at=created_at,
    )


@pytest.fixture(autouse=True)
def production_stale_timeout(settings):
    """Keep day-based tests independent from any E2E process environment."""
    settings.STALE_PARSE_TIMEOUT_SECONDS = 24 * 60 * 60


def test_stale_file_checker_is_scheduled():
    """Register the stale checker with Celery beat."""
    schedule = settings.CELERY_BEAT_SCHEDULE["Mark Stale Data Files Stuck"]
    route = settings.CELERY_TASK_ROUTES[
        "tdpservice.data_files.tasks.mark_stale_files_stuck"
    ]

    assert schedule["task"] == "tdpservice.data_files.tasks.mark_stale_files_stuck"
    assert route["queue"] == settings.CELERY_LIFECYCLE_QUEUE


@pytest.mark.django_db
def test_stale_timeout_can_be_shortened_for_browser_testing(stt_user, stt, settings):
    """Honor the environment-specific timeout without changing production's day."""
    settings.STALE_PARSE_TIMEOUT_SECONDS = 60
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, timezone.now() - timedelta(seconds=61))

    assert list(get_stale_lifecycle_files().values_list("pk", flat=True)) == [
        datafile.pk
    ]


@pytest.mark.django_db
def test_stale_timeout_can_be_supplied_by_task_caller(stt_user, stt):
    """Allow an accelerated task run without changing production settings."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, timezone.now() - timedelta(seconds=61))

    marked_count = mark_stale_files_stuck(timeout_seconds=60)

    datafile.refresh_from_db()
    assert marked_count == 1
    assert datafile.state == SubmissionState.STUCK


@pytest.mark.django_db
def test_stuck_files_across_fiscal_years_are_included(stt_user: User, stt: STT) -> None:
    """Keep actionable stuck submissions from every fiscal year visible."""
    datafiles = [
        make_datafile(stt_user, stt, 1, state=SubmissionState.STUCK, year=year)
        for year in (2024, 2025, 2026, 2027)
    ]

    stuck_files = get_stuck_files()

    assert list(stuck_files.values_list("pk", flat=True)) == [
        datafile.pk for datafile in datafiles
    ]


@pytest.mark.django_db
@pytest.mark.parametrize("summary_status", [None, DataFileSummary.Status.PENDING])
def test_non_stuck_missing_or_pending_summary_is_excluded(
    stt_user,
    stt,
    summary_status,
):
    """Ignore legacy summary conditions unless the lifecycle state is STUCK."""
    non_stuck_file = make_datafile(
        stt_user,
        stt,
        2,
        state=SubmissionState.PARSE_STARTED,
    )
    if summary_status is not None:
        make_summary(non_stuck_file, summary_status)

    stuck_files = get_stuck_files()

    assert not stuck_files.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("newer_state", list(SubmissionState))
def test_newer_version_supersedes_stuck_file_regardless_of_state(
    stt_user: User, stt: STT, newer_state: SubmissionState
) -> None:
    """Only notify for the latest version, even if a newer version failed."""
    make_datafile(stt_user, stt, 1, state=SubmissionState.STUCK, year=2025)
    newer_file = make_datafile(stt_user, stt, 2, state=newer_state, year=2025)

    expected_ids = [newer_file.pk] if newer_state == SubmissionState.STUCK else []
    assert list(get_stuck_files().values_list("pk", flat=True)) == expected_ids


@pytest.mark.django_db
def test_latest_stuck_version_is_selected_by_version_number(
    stt_user: User, stt: STT
) -> None:
    """Creation and lifecycle timestamps do not determine version relevance."""
    latest_file = make_datafile(stt_user, stt, 3, state=SubmissionState.STUCK)
    set_created_at(latest_file, timezone.now() - timedelta(days=2))
    make_datafile(stt_user, stt, 1, state=SubmissionState.STUCK)
    make_datafile(stt_user, stt, 2, state=SubmissionState.STUCK)

    assert list(get_stuck_files().values_list("pk", flat=True)) == [latest_file.pk]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "series_dimension",
    ["stt", "year", "quarter", "program_type", "section", "is_program_audit"],
)
@pytest.mark.parametrize(
    "newer_state", [SubmissionState.STUCK, SubmissionState.COMPLETED]
)
def test_different_submission_series_do_not_supersede_each_other(
    stt_user: User,
    stt: STT,
    other_stt: STT,
    series_dimension: str,
    newer_state: SubmissionState,
) -> None:
    """Keep each version-series dimension independent from all the others."""
    stuck_file = make_datafile(stt_user, stt, 1, state=SubmissionState.STUCK)
    series_changes = {
        "stt": other_stt,
        "year": 2025,
        "quarter": DataFile.Quarter.Q2,
        "program_type": Program.Code.SSP,
        "section": Section.Name.CLOSED_CASE_DATA,
        "is_program_audit": True,
    }
    newer_file = DataFileFactory.create(
        user=stt_user,
        **{
            "stt": stt,
            "year": stuck_file.year,
            "quarter": stuck_file.quarter,
            "section": Section.Name.ACTIVE_CASE_DATA,
            "version": 2,
            "state": newer_state,
            series_dimension: series_changes[series_dimension],
        },
    )

    expected_ids = [stuck_file.pk]
    if newer_state == SubmissionState.STUCK:
        expected_ids.append(newer_file.pk)
    assert list(get_stuck_files().values_list("pk", flat=True)) == expected_ids


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("state", "is_stale_eligible"),
    [
        (SubmissionState.UPLOADED, True),
        (SubmissionState.VIRUS_SCAN_STARTED, True),
        (SubmissionState.VIRUS_SCAN_COMPLETED, True),
        (SubmissionState.REPARSE_REQUESTED, True),
        (SubmissionState.PARSE_STARTED, True),
        (SubmissionState.VIRUS_SCAN_FAILED, False),
        (SubmissionState.PARSE_FAILED, False),
        (SubmissionState.PARSED_WITH_ERRORS, False),
        (SubmissionState.PARSE_COMPLETED, False),
        (SubmissionState.STUCK, False),
        (SubmissionState.COMPLETED, False),
        (SubmissionState.CANCELED, False),
    ],
)
def test_stale_lifecycle_state_matrix(stt_user, stt, state, is_stale_eligible):
    """Evaluate every lifecycle state above and below the stale threshold."""
    now = timezone.now()
    old_file = make_datafile(stt_user, stt, 1, state=state)
    set_created_at(old_file, now - timedelta(days=1, minutes=1))
    recent_file = make_datafile(stt_user, stt, 2, state=state)
    set_created_at(recent_file, now - timedelta(hours=23))

    stale_file_ids = set(
        get_stale_lifecycle_files(now=now).values_list("pk", flat=True)
    )

    expected_ids = {old_file.pk} if is_stale_eligible else set()
    assert stale_file_ids == expected_ids
    assert recent_file.pk not in stale_file_ids


@pytest.mark.django_db
@pytest.mark.parametrize("summary_status", [None, DataFileSummary.Status.PENDING])
def test_stale_parse_is_ready_to_be_marked_stuck(
    stt_user,
    stt,
    summary_status,
):
    """Finds parses with missing or PENDING summaries after one day."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, timezone.now() - timedelta(days=1, minutes=1))
    if summary_status is not None:
        make_summary(datafile, summary_status)

    stale_files = get_stale_lifecycle_files()

    assert list(stale_files.values_list("pk", flat=True)) == [datafile.pk]


@pytest.mark.django_db
@pytest.mark.parametrize("summary_status", [None, DataFileSummary.Status.PENDING])
def test_parse_less_than_a_day_old_is_not_stale(
    stt_user,
    stt,
    summary_status,
):
    """Ignores parses that have not reached the one-day threshold."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, timezone.now() - timedelta(hours=23))
    if summary_status is not None:
        make_summary(datafile, summary_status)

    stale_files = get_stale_lifecycle_files()

    assert stale_files.count() == 0


@pytest.mark.django_db
def test_reparse_older_than_a_day_is_stale(stt_user, stt):
    """Apply the lifecycle timeout even before a reparse-specific deadline."""
    now = timezone.now()
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, now - timedelta(days=30))
    make_summary(datafile, DataFileSummary.Status.PENDING)
    reparse = ReparseMetaFactory.create(timeout_at=now + timedelta(days=1))
    datafile.reparses.add(
        reparse,
        through_defaults={
            "finished": False,
            "success": False,
            "started_at": now - timedelta(days=1, minutes=1),
        },
    )
    DataFile.objects.filter(pk=datafile.pk).update(
        state_changed_at=now - timedelta(days=1, minutes=1)
    )

    stale_files = get_stale_lifecycle_files(now=now)

    assert list(stale_files.values_list("pk", flat=True)) == [datafile.pk]


@pytest.mark.django_db
def test_recent_reparse_of_old_file_is_not_stale(stt_user, stt):
    """Ignore an unfinished reparse before either detection deadline."""
    now = timezone.now()
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, now - timedelta(days=30))
    make_summary(datafile, DataFileSummary.Status.PENDING)
    reparse = ReparseMetaFactory.create(timeout_at=now + timedelta(hours=1))
    datafile.reparses.add(
        reparse,
        through_defaults={
            "finished": False,
            "success": False,
            "started_at": now - timedelta(hours=23),
        },
    )
    DataFile.objects.filter(pk=datafile.pk).update(
        state_changed_at=now - timedelta(hours=23)
    )

    stale_files = get_stale_lifecycle_files(now=now)

    assert stale_files.count() == 0


@pytest.mark.django_db
def test_timed_out_unfinished_reparse_is_stale(stt_user, stt):
    """Honor ReparseMeta.timeout_at before the generic lifecycle timeout."""
    now = timezone.now()
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, now - timedelta(hours=1))
    reparse = ReparseMetaFactory.create(timeout_at=now - timedelta(minutes=1))
    datafile.reparses.add(
        reparse,
        through_defaults={
            "finished": False,
            "success": False,
            "started_at": now - timedelta(hours=1),
        },
    )

    stale_files = get_stale_lifecycle_files(now=now)

    assert list(stale_files.values_list("pk", flat=True)) == [datafile.pk]


@pytest.mark.django_db
def test_timed_out_finished_reparse_is_not_stale(stt_user, stt):
    """Do not use a completed historical reparse to mark current work stale."""
    now = timezone.now()
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(datafile, now - timedelta(hours=1))
    reparse = ReparseMetaFactory.create(timeout_at=now - timedelta(minutes=1))
    datafile.reparses.add(
        reparse,
        through_defaults={
            "finished": True,
            "success": False,
            "started_at": now - timedelta(hours=1),
            "finished_at": now - timedelta(minutes=30),
        },
    )

    stale_files = get_stale_lifecycle_files(now=now)

    assert stale_files.count() == 0


@pytest.mark.django_db
def test_old_file_with_completed_summary_is_not_stale(stt_user, stt):
    """Ignores files whose parsing completed before the stale check."""
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_COMPLETED,
    )
    set_created_at(datafile, timezone.now() - timedelta(days=2))
    make_summary(datafile, DataFileSummary.Status.ACCEPTED)

    stale_files = get_stale_lifecycle_files()

    assert stale_files.count() == 0


@pytest.mark.django_db
def test_mark_stale_files_stuck_transitions_eligible_files(stt_user, stt):
    """Persist STUCK for stale parses and leave recent parses unchanged."""
    stale_file = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(stale_file, timezone.now() - timedelta(days=2))
    make_summary(stale_file, DataFileSummary.Status.PENDING)
    recent_file = make_datafile(
        stt_user,
        stt,
        2,
        state=SubmissionState.PARSE_STARTED,
    )
    set_created_at(recent_file, timezone.now() - timedelta(hours=23))
    make_summary(recent_file, DataFileSummary.Status.PENDING)

    marked_count = mark_stale_files_stuck()

    stale_file.refresh_from_db()
    recent_file.refresh_from_db()
    assert marked_count == 1
    assert stale_file.state == SubmissionState.STUCK
    assert recent_file.state == SubmissionState.PARSE_STARTED


@pytest.mark.django_db
def test_stuck_file_remains_visible_across_fiscal_year_rollover(
    stt_user: User, stt: STT, mocker: MockerFixture
) -> None:
    """Keep prior-year work visible until it is superseded or leaves STUCK."""
    now = mocker.patch("tdpservice.data_files.tasks.timezone.now")
    now.return_value = datetime(2026, 9, 30, 23, 59, tzinfo=datetime_timezone.utc)
    datafile = make_datafile(
        stt_user,
        stt,
        1,
        state=SubmissionState.STUCK,
        year=2026,
    )

    assert list(get_stuck_files().values_list("pk", flat=True)) == [datafile.pk]

    now.return_value = datetime(2026, 10, 1, 0, 1, tzinfo=datetime_timezone.utc)
    assert list(get_stuck_files().values_list("pk", flat=True)) == [datafile.pk]

    DataFile.objects.filter(pk=datafile.pk).update(
        state=SubmissionState.REPARSE_REQUESTED
    )
    assert not get_stuck_files().exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "latest_state", [SubmissionState.STUCK, SubmissionState.COMPLETED]
)
def test_notification_sends_only_latest_actionable_submission(
    stt_user: User,
    stt: STT,
    ofa_system_admin: User,
    mocker: MockerFixture,
    latest_state: SubmissionState,
) -> None:
    """Email the selected prior-year file or stay silent when it is superseded."""
    send_email = mocker.patch("tdpservice.data_files.tasks.send_stuck_file_email")
    make_datafile(stt_user, stt, 1, state=SubmissionState.STUCK, year=2025)
    latest_file = make_datafile(stt_user, stt, 2, state=latest_state, year=2025)

    notify_stuck_files()

    if latest_state == SubmissionState.STUCK:
        send_email.assert_called_once()
        files, recipients = send_email.call_args.args
        assert list(files.values_list("pk", flat=True)) == [latest_file.pk]
        assert list(recipients) == [ofa_system_admin.username]
    else:
        send_email.assert_not_called()


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
