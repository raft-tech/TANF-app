"""PostgreSQL permission tests for Grafana feedback report metadata access."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4

from django.db import ProgrammingError, connection, transaction

import pytest

from scripts.create_grafana_postgres_role import run as create_grafana_role
from tdpservice.reports.models import ReportFile
from tdpservice.reports.test.factories import ReportFileFactory

pytestmark = pytest.mark.django_db


@contextmanager
def use_role(role: str) -> Iterator[None]:
    """Temporarily query as a restricted role within the test transaction."""
    with connection.cursor() as cursor:
        cursor.execute(f"SET LOCAL ROLE {connection.ops.quote_name(role)}")
        try:
            yield
        finally:
            cursor.execute("RESET ROLE")


@pytest.fixture
def grafana_role(db: None) -> str:
    """Create a disposable reporting role without report-file access."""
    role = f"grafana_feedback_{uuid4().hex}"
    create_grafana_role(role, "stts_stt")
    return role


@pytest.fixture
def report_files() -> list[ReportFile]:
    """Create downloaded, pending, and unassigned reports without S3 writes."""
    downloaded = ReportFileFactory.create(
        file=None,
        user=None,
        downloaded_at=datetime(2026, 11, 23, 12, tzinfo=timezone.utc),
    )
    pending = ReportFileFactory.create(
        file=None, user=None, stt=downloaded.stt, version=2
    )
    unassigned = ReportFileFactory.create(
        file=None, user=None, stt=None, source=None, version=3
    )
    return [downloaded, pending, unassigned]


def test_ungranted_reporting_role_cannot_read_reports(grafana_role: str) -> None:
    """An ordinary reporting role cannot query the report-file table."""
    with use_role(grafana_role), connection.cursor() as cursor:
        with pytest.raises(ProgrammingError, match="permission denied"), transaction.atomic():
            cursor.execute("SELECT id FROM public.reports_reportfile LIMIT 1")


@pytest.mark.parametrize("grant_count", [1, 2])
def test_report_grant_exposes_download_metadata(
    grafana_role: str, report_files: list[ReportFile], grant_count: int
) -> None:
    """Initial and repeated grants allow reads without changing null metadata."""
    for _ in range(grant_count):
        create_grafana_role(grafana_role, "reports_reportfile")

    with use_role(grafana_role), connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, stt_id, source_id, downloaded_at
            FROM public.reports_reportfile
            WHERE id IN (%s, %s, %s)
            ORDER BY id
            """,
            [report.pk for report in report_files],
        )
        assert cursor.fetchall() == [
            (report.pk, report.stt_id, report.source_id, report.downloaded_at)
            for report in report_files
        ]
        cursor.execute("SELECT id FROM public.reports_reportfile WHERE FALSE")
        assert cursor.fetchall() == []


def test_report_grant_has_only_select_privilege(grafana_role: str) -> None:
    """The metadata grant does not permit table mutation or definition changes."""
    create_grafana_role(grafana_role, "reports_reportfile")

    with use_role(grafana_role), connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT privilege,
                   has_table_privilege(current_user, 'public.reports_reportfile', privilege)
            FROM (VALUES ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'),
                         ('TRUNCATE'), ('REFERENCES'), ('TRIGGER')) AS p(privilege)
            """
        )
        assert dict(cursor.fetchall()) == {
            "SELECT": True,
            "INSERT": False,
            "UPDATE": False,
            "DELETE": False,
            "TRUNCATE": False,
            "REFERENCES": False,
            "TRIGGER": False,
        }


@pytest.mark.parametrize(
    "statement",
    [
        "INSERT INTO public.reports_reportfile (id) "
        "SELECT id FROM public.reports_reportfile WHERE FALSE",
        "UPDATE public.reports_reportfile SET downloaded_at = NULL WHERE FALSE",
        "DELETE FROM public.reports_reportfile WHERE FALSE",
    ],
    ids=["insert", "update", "delete"],
)
def test_report_grant_denies_writes(
    grafana_role: str, report_files: list[ReportFile], statement: str
) -> None:
    """Actual write attempts fail even when their predicates match no rows."""
    create_grafana_role(grafana_role, "reports_reportfile")
    original_rows = list(ReportFile.objects.order_by("pk").values())

    with use_role(grafana_role), connection.cursor() as cursor:
        with pytest.raises(ProgrammingError, match="permission denied"), transaction.atomic():
            cursor.execute(statement)

    assert list(ReportFile.objects.order_by("pk").values()) == original_rows


def test_report_grant_does_not_extend_other_roles(grafana_role: str) -> None:
    """Granting DIGIT-equivalent access leaves other reporting roles restricted."""
    other_role = f"grafana_ordinary_{uuid4().hex}"
    create_grafana_role(other_role, "stts_stt")
    create_grafana_role(grafana_role, "reports_reportfile")

    with use_role(other_role), connection.cursor() as cursor:
        with pytest.raises(ProgrammingError, match="permission denied"), transaction.atomic():
            cursor.execute("SELECT id FROM public.reports_reportfile LIMIT 1")
