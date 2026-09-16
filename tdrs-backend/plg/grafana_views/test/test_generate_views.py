"""PostgreSQL tests for generated Grafana views."""

from django.db import connection

import pytest

from plg.grafana_views.generate_views import query_template
from tdpservice.data_files.test.factories import (
    DataFileFactory,
    canonical_section_for,
)
from tdpservice.search_indexes.models.tanf import TANF_T1
from tdpservice.stts.test.factories import STTFactory
from tdpservice.users.test.factories import UserFactory


def _view_query():
    """Return a representative generated TANF view query."""
    return query_template.format(
        fields='"RecordType",',
        table=TANF_T1._meta.db_table,
        record_type="T1",
        custom_where_clause="",
    )


def test_generated_query_uses_canonical_classification_and_audit_identity():
    """Generated SQL retains aliases without reading legacy DataFile columns."""
    query = _view_query()

    assert "canonical_section.name::varchar(32) AS section" in query
    assert "canonical_program.code::varchar(32) AS program_type" in query
    assert "data_files_section canonical_section" in query
    assert "data_files_program canonical_program" in query
    assert "section_ref_id" in query
    assert "is_program_audit" in query
    assert "data_files.section," not in query
    assert "data_files.program_type" not in query


@pytest.mark.django_db(transaction=True)
def test_generated_view_has_no_legacy_column_dependencies_and_preserves_grants():
    """A replaced view keeps grants/downstream views and drops legacy dependencies."""
    section = canonical_section_for("TAN", "Active Case Data")
    stt = STTFactory.create()
    user = UserFactory.create()
    files = [
        DataFileFactory.create(
            section_ref=section,
            stt=stt,
            user=user,
            year=2026,
            quarter="Q1",
            version=version,
            is_program_audit=is_program_audit,
        )
        for version, is_program_audit in ((1, False), (2, False), (1, True), (3, True))
    ]
    for datafile in files:
        TANF_T1.objects.create(
            datafile=datafile,
            RecordType="T1",
            RPT_MONTH_YEAR=202601,
            CASE_NUMBER=f"{datafile.id:011d}",
        )

    view_name = "test_canonical_grafana_view"
    downstream_view_name = "latest_tanf_exiters_view_prod_test"
    create_view = f'CREATE OR REPLACE VIEW "{view_name}" AS {_view_query()}'
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_view)
            cursor.execute(f'GRANT SELECT ON "{view_name}" TO PUBLIC')
            cursor.execute(
                f'CREATE VIEW "{downstream_view_name}" AS '
                f'SELECT * FROM "{view_name}"'
            )
            cursor.execute(create_view)
            cursor.execute(
                f'SELECT version, section, program_type FROM "{view_name}" '
                "ORDER BY version"
            )
            rows = cursor.fetchall()
            cursor.execute(
                """
                SELECT referenced_attribute.attname
                FROM pg_depend dependency
                INNER JOIN pg_rewrite rewrite ON rewrite.oid = dependency.objid
                INNER JOIN pg_class dependent ON dependent.oid = rewrite.ev_class
                INNER JOIN pg_attribute referenced_attribute
                    ON referenced_attribute.attrelid = dependency.refobjid
                    AND referenced_attribute.attnum = dependency.refobjsubid
                WHERE dependent.relname = %s
                    AND dependency.refobjid = 'data_files_datafile'::regclass
                    AND referenced_attribute.attname IN ('section', 'program_type')
                """,
                [view_name],
            )
            legacy_dependencies = cursor.fetchall()
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM pg_class view_relation,
                        LATERAL aclexplode(
                            COALESCE(
                                view_relation.relacl,
                                acldefault('r', view_relation.relowner)
                            )
                        ) acl
                    WHERE view_relation.relname = %s
                        AND acl.grantee = 0
                        AND acl.privilege_type = 'SELECT'
                )
                """,
                [view_name],
            )
            public_can_select = cursor.fetchone()[0]
            cursor.execute(f'SELECT COUNT(*) FROM "{downstream_view_name}"')
            downstream_count = cursor.fetchone()[0]
    finally:
        with connection.cursor() as cursor:
            cursor.execute(f'DROP VIEW IF EXISTS "{downstream_view_name}"')
            cursor.execute(f'DROP VIEW IF EXISTS "{view_name}"')

    assert rows == [
        (2, "Active Case Data", "TAN"),
        (3, "Active Case Data", "TAN"),
    ]
    assert legacy_dependencies == []
    assert public_can_select is True
    assert downstream_count == 2
