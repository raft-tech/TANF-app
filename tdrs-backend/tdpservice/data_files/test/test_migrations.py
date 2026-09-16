"""Migration tests for the data_files app."""

import importlib

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


MIGRATE_FROM = "0030_datafile_section_ref"
MIGRATE_TO = "0031_backfill_datafile_section_ref"


def _migration_targets(executor, data_files_target):
    """Target DataFiles before the dependent STTs participation backfill."""
    target_overrides = {
        "data_files": data_files_target,
        "stts": "0013_program_section_sttprogramparticipation",
        "users": "0059_reconcile_role_permissions",
    }
    return [
        (app_label, target_overrides.get(app_label, migration))
        for app_label, migration in executor.loader.graph.leaf_nodes()
    ]


def _create_data_file(
    DataFile,
    user,
    stt,
    *,
    slug,
    program_type,
    section,
    section_ref=None,
    audit=False,
    version=1,
):
    return DataFile.objects.create(
        original_filename=f"{slug}.txt",
        slug=slug,
        extension="txt",
        quarter="Q1",
        year=2020,
        program_type=program_type,
        section=section,
        section_ref=section_ref,
        is_program_audit=audit,
        version=version,
        state="uploaded",
        user=user,
        stt=stt,
    )


@pytest.mark.django_db(transaction=True)
def test_data_file_section_ref_backfill():
    """The backfill maps all legacy programs, sections, and PIA files."""
    executor = MigrationExecutor(connection)
    migrate_from = _migration_targets(executor, MIGRATE_FROM)
    migrate_to = _migration_targets(executor, MIGRATE_TO)

    try:
        executor.migrate(migrate_from)
        old_apps = executor.loader.project_state(migrate_from).apps
        DataFile = old_apps.get_model("data_files", "DataFile")
        Program = old_apps.get_model("data_files", "Program")
        STT = old_apps.get_model("stts", "STT")
        User = old_apps.get_model("users", "User")

        Program.objects.all().delete()

        stt = STT.objects.create(name="DataFile migration STT")
        user = User.objects.create(username="datafile-migration@example.com")
        expected_files = [
            (
                _create_data_file(
                    DataFile,
                    user,
                    stt,
                    slug="tanf-active",
                    program_type="TAN",
                    section="Active Case Data",
                ),
                "TAN",
                "Active Case Data",
                False,
            ),
            (
                _create_data_file(
                    DataFile,
                    user,
                    stt,
                    slug="ssp-closed",
                    program_type="SSP",
                    section="Closed Case Data",
                ),
                "SSP",
                "Closed Case Data",
                False,
            ),
            (
                _create_data_file(
                    DataFile,
                    user,
                    stt,
                    slug="tribal-aggregate",
                    program_type="TRIBAL",
                    section="Aggregate Data",
                ),
                "TRIBAL",
                "Aggregate Data",
                False,
            ),
            (
                _create_data_file(
                    DataFile,
                    user,
                    stt,
                    slug="fra-outcomes",
                    program_type="FRA",
                    section="Work Outcomes of TANF Exiters",
                ),
                "FRA",
                "Work Outcomes of TANF Exiters",
                False,
            ),
            (
                _create_data_file(
                    DataFile,
                    user,
                    stt,
                    slug="tanf-pia",
                    program_type="TAN",
                    section="Closed Case Data",
                    audit=True,
                ),
                "TAN",
                "Closed Case Data",
                True,
            ),
            (
                _create_data_file(
                    DataFile,
                    user,
                    stt,
                    slug="tribal-pia",
                    program_type="TRIBAL",
                    section="Active Case Data",
                    audit=True,
                ),
                "TRIBAL",
                "Active Case Data",
                True,
            ),
        ]

        executor = MigrationExecutor(connection)
        executor.migrate(migrate_to)
        new_apps = executor.loader.project_state(migrate_to).apps
        DataFile = new_apps.get_model("data_files", "DataFile")
        Program = new_apps.get_model("data_files", "Program")
        Section = new_apps.get_model("data_files", "Section")

        for old_data_file, program_code, section_name, audit in expected_files:
            data_file = DataFile.objects.get(id=old_data_file.id)
            assert data_file.section_ref.program.code == program_code
            assert data_file.section_ref.name == section_name
            assert data_file.is_program_audit is audit

        assert set(Program.objects.values_list("code", flat=True)) == {
            "TAN",
            "SSP",
            "TRIBAL",
            "FRA",
        }
        expected_sections = {
            "TAN": {
                "Active Case Data",
                "Closed Case Data",
                "Aggregate Data",
                "Stratum Data",
            },
            "SSP": {
                "Active Case Data",
                "Closed Case Data",
                "Aggregate Data",
                "Stratum Data",
            },
            "TRIBAL": {
                "Active Case Data",
                "Closed Case Data",
                "Aggregate Data",
                "Stratum Data",
            },
            "FRA": {
                "Work Outcomes of TANF Exiters",
                "Secondary School Attainment",
                "Supplemental Work Outcomes",
            },
        }
        for program_code, section_names in expected_sections.items():
            assert set(
                Section.objects.filter(program__code=program_code).values_list(
                    "name", flat=True
                )
            ) == section_names
        assert not Program.objects.filter(code="PIA").exists()

        migration = importlib.import_module(
            "tdpservice.data_files.migrations.0031_backfill_datafile_section_ref"
        )
        migration.backfill_datafile_section_ref(new_apps, None)
        assert DataFile.objects.filter(section_ref__isnull=True).count() == 0
    finally:
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())


@pytest.mark.django_db(transaction=True)
def test_data_file_section_ref_backfill_rejects_unmapped_values():
    """The backfill fails rather than silently skipping unknown legacy values."""
    executor = MigrationExecutor(connection)
    migrate_from = _migration_targets(executor, MIGRATE_FROM)
    migrate_to = _migration_targets(executor, MIGRATE_TO)
    invalid_data_file_id = None

    try:
        executor.migrate(migrate_from)
        old_apps = executor.loader.project_state(migrate_from).apps
        DataFile = old_apps.get_model("data_files", "DataFile")
        STT = old_apps.get_model("stts", "STT")
        User = old_apps.get_model("users", "User")

        stt = STT.objects.create(name="Invalid DataFile migration STT")
        user = User.objects.create(username="invalid-datafile-migration@example.com")
        invalid_data_file = _create_data_file(
            DataFile,
            user,
            stt,
            slug="unknown-section",
            program_type="UNKNOWN",
            section="Unknown Section",
        )
        invalid_data_file_id = invalid_data_file.id

        executor = MigrationExecutor(connection)
        with pytest.raises(RuntimeError, match="UNKNOWN.*Unknown Section"):
            executor.migrate(migrate_to)
    finally:
        if invalid_data_file_id is not None:
            DataFile.objects.filter(id=invalid_data_file_id).delete()
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())


@pytest.mark.django_db(transaction=True)
def test_data_file_contract_migration_handles_empty_table():
    """The contract migration succeeds when no DataFiles exist."""
    executor = MigrationExecutor(connection)
    migrate_from = _migration_targets(
        executor, "0033_alter_shadowdatafile_file_and_more"
    )
    migrate_to = _migration_targets(
        executor, "0034_contract_datafile_canonical_section"
    )

    try:
        executor.migrate(migrate_from)
        old_apps = executor.loader.project_state(migrate_from).apps
        backfill_migration = importlib.import_module(
            "tdpservice.data_files.migrations.0031_backfill_datafile_section_ref"
        )
        backfill_migration.ensure_canonical_sections(old_apps)
        old_apps.get_model("data_files", "DataFile").objects.all().delete()

        executor = MigrationExecutor(connection)
        executor.migrate(migrate_to)
        new_apps = executor.loader.project_state(migrate_to).apps

        assert not new_apps.get_model("data_files", "DataFile").objects.exists()
    finally:
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())


@pytest.mark.django_db(transaction=True)
def test_data_file_contract_migration_preserves_canonical_classification():
    """The contract migration removes only production scalar classification."""
    executor = MigrationExecutor(connection)
    migrate_from = _migration_targets(
        executor, "0033_alter_shadowdatafile_file_and_more"
    )
    migrate_to = _migration_targets(
        executor, "0034_contract_datafile_canonical_section"
    )

    try:
        executor.migrate(migrate_from)
        old_apps = executor.loader.project_state(migrate_from).apps
        DataFile = old_apps.get_model("data_files", "DataFile")
        ShadowDataFile = old_apps.get_model("data_files", "ShadowDataFile")
        Section = old_apps.get_model("data_files", "Section")
        STT = old_apps.get_model("stts", "STT")
        User = old_apps.get_model("users", "User")
        backfill_migration = importlib.import_module(
            "tdpservice.data_files.migrations.0031_backfill_datafile_section_ref"
        )
        backfill_migration.ensure_canonical_sections(old_apps)

        stt = STT.objects.create(name="Contract migration STT")
        user = User.objects.create(username="contract-migration@example.com")
        classifications = [
            ("TAN", "Active Case Data", False),
            ("SSP", "Closed Case Data", False),
            ("TRIBAL", "Aggregate Data", False),
            ("FRA", "Work Outcomes of TANF Exiters", False),
            ("FRA", "Secondary School Attainment", False),
            ("FRA", "Supplemental Work Outcomes", False),
            ("TAN", "Closed Case Data", True),
            ("TRIBAL", "Active Case Data", True),
        ]
        expected = []
        for version, (program_code, section_name, audit) in enumerate(
            classifications, start=1
        ):
            canonical_section = Section.objects.get(
                program__code=program_code,
                name=section_name,
            )
            data_file = _create_data_file(
                DataFile,
                user,
                stt,
                slug=f"contract-{version}",
                program_type=program_code,
                section=section_name,
                section_ref=canonical_section,
                audit=audit,
                version=version,
            )
            expected.append((data_file.id, canonical_section.id))

        ShadowDataFile.objects.create(
            id=999999,
            original_filename="shadow.txt",
            slug="contract-shadow",
            extension="txt",
            quarter="Q1",
            year=2020,
            program_type="TAN",
            section="Active Case Data",
            is_program_audit=False,
            version=1,
            state="uploaded",
            user=user,
            stt=stt,
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE VIEW tanf_t1 AS "
                "SELECT id, program_type, section FROM data_files_datafile"
            )
            cursor.execute(
                "CREATE VIEW latest_tanf_exiters_view_prod AS SELECT * FROM tanf_t1"
            )

        executor = MigrationExecutor(connection)
        executor.migrate(migrate_to)
        new_apps = executor.loader.project_state(migrate_to).apps
        DataFile = new_apps.get_model("data_files", "DataFile")
        ShadowDataFile = new_apps.get_model("data_files", "ShadowDataFile")

        assert list(
            DataFile.objects.order_by("id").values_list("id", "section_id")
        ) == expected
        assert not DataFile._meta.get_field("section").null
        assert DataFile._meta.get_field("section").db_column == "section_ref_id"
        assert ShadowDataFile.objects.get(id=999999).program_type == "TAN"
        assert ShadowDataFile.objects.get(id=999999).section == "Active Case Data"

        table_columns = {
            column.name
            for column in connection.introspection.get_table_description(
                connection.cursor(), "data_files_datafile"
            )
        }
        shadow_columns = {
            column.name
            for column in connection.introspection.get_table_description(
                connection.cursor(), "shadow_data_files_datafile"
            )
        }
        assert "section_ref_id" in table_columns
        assert "section" not in table_columns
        assert "program_type" not in table_columns
        assert {"section", "program_type"} <= shadow_columns
        table_names = connection.introspection.table_names(include_views=True)
        assert "tanf_t1" not in table_names
        assert "latest_tanf_exiters_view_prod" not in table_names
    finally:
        with connection.cursor() as cursor:
            cursor.execute("DROP VIEW IF EXISTS latest_tanf_exiters_view_prod")
            cursor.execute("DROP VIEW IF EXISTS tanf_t1")
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "invalid_case, expected_error",
    [
        ("null", "null section_ref"),
        ("mismatch", "legacy/canonical mismatch"),
        ("noncanonical", "noncanonical section"),
        ("invalid_audit", "invalid program audit"),
        ("duplicate", "canonical duplicates"),
    ],
)
def test_data_file_contract_migration_rejects_invalid_data(
    invalid_case, expected_error
):
    """Each contract precondition fails before destructive operations."""
    executor = MigrationExecutor(connection)
    migrate_from = _migration_targets(
        executor, "0033_alter_shadowdatafile_file_and_more"
    )
    migrate_to = _migration_targets(
        executor, "0034_contract_datafile_canonical_section"
    )

    try:
        executor.migrate(migrate_from)
        old_apps = executor.loader.project_state(migrate_from).apps
        DataFile = old_apps.get_model("data_files", "DataFile")
        Program = old_apps.get_model("data_files", "Program")
        Section = old_apps.get_model("data_files", "Section")
        STT = old_apps.get_model("stts", "STT")
        User = old_apps.get_model("users", "User")
        backfill_migration = importlib.import_module(
            "tdpservice.data_files.migrations.0031_backfill_datafile_section_ref"
        )
        backfill_migration.ensure_canonical_sections(old_apps)

        stt = STT.objects.create(name="Invalid contract migration STT")
        user = User.objects.create(username="invalid-contract@example.com")
        program_type = "TAN"
        section_name = "Active Case Data"
        section_ref = Section.objects.get(
            program__code=program_type, name=section_name
        )
        audit = False

        if invalid_case == "null":
            section_ref = None
        elif invalid_case == "mismatch":
            program_type = "SSP"
        elif invalid_case == "noncanonical":
            program = Program.objects.create(
                code="OTHER", slug="other", name="Other"
            )
            section_ref = Section.objects.create(
                program=program, name="Other Section"
            )
            program_type = program.code
            section_name = section_ref.name
        elif invalid_case == "invalid_audit":
            program_type = "SSP"
            section_ref = Section.objects.get(
                program__code=program_type, name=section_name
            )
            audit = True
        elif invalid_case == "duplicate":
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE data_files_datafile "
                    "DROP CONSTRAINT constraint_name"
                )

        copies = 2 if invalid_case == "duplicate" else 1
        for index in range(copies):
            _create_data_file(
                DataFile,
                user,
                stt,
                slug=f"invalid-contract-{invalid_case}-{index}",
                program_type=program_type,
                section=section_name,
                section_ref=section_ref,
                audit=audit,
            )

        executor = MigrationExecutor(connection)
        with pytest.raises(RuntimeError, match=expected_error):
            executor.migrate(migrate_to)

        table_columns = {
            column.name
            for column in connection.introspection.get_table_description(
                connection.cursor(), "data_files_datafile"
            )
        }
        assert {"section", "program_type", "section_ref_id"} <= table_columns
    finally:
        DataFile.objects.all().delete()
        if invalid_case == "duplicate":
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE data_files_datafile ADD CONSTRAINT constraint_name "
                    "UNIQUE (program_type, section, version, quarter, year, "
                    "stt_id, is_program_audit)"
                )
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())


@pytest.mark.django_db(transaction=True)
def test_data_file_contract_migration_rejects_unknown_dependent_view():
    """The migration refuses to cascade through an unrecognized view."""
    executor = MigrationExecutor(connection)
    migrate_from = _migration_targets(
        executor, "0033_alter_shadowdatafile_file_and_more"
    )
    migrate_to = _migration_targets(
        executor, "0034_contract_datafile_canonical_section"
    )

    try:
        executor.migrate(migrate_from)
        old_apps = executor.loader.project_state(migrate_from).apps
        backfill_migration = importlib.import_module(
            "tdpservice.data_files.migrations.0031_backfill_datafile_section_ref"
        )
        backfill_migration.ensure_canonical_sections(old_apps)
        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE VIEW unexpected_legacy_view AS "
                "SELECT program_type FROM data_files_datafile"
            )

        executor = MigrationExecutor(connection)
        with pytest.raises(RuntimeError, match="unknown dependent views"):
            executor.migrate(migrate_to)
    finally:
        with connection.cursor() as cursor:
            cursor.execute("DROP VIEW IF EXISTS unexpected_legacy_view")
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
