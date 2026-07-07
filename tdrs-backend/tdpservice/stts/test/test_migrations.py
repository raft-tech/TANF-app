"""Migration tests for the stts app."""

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


@pytest.mark.django_db(transaction=True)
def test_ssp_program_participation_data_migration():
    """The SSP backfill creates active rows only for current SSP STTs."""
    migrate_from = [("stts", "0013_program_section_sttprogramparticipation")]
    migrate_to = [("stts", "0014_populate_ssp_program_participation")]
    executor = MigrationExecutor(connection)

    try:
        executor.migrate(migrate_from)
        old_apps = executor.loader.project_state(migrate_from).apps
        Region = old_apps.get_model("stts", "Region")
        STT = old_apps.get_model("stts", "STT")

        region = Region.objects.create(id=9999)
        active_stt = STT.objects.create(
            name="Active SSP STT",
            region=region,
            stt_code="901",
            ssp=True,
        )
        inactive_stt = STT.objects.create(
            name="Inactive SSP STT",
            region=region,
            stt_code="902",
            ssp=False,
        )
        null_stt = STT.objects.create(
            name="Null SSP STT",
            region=region,
            stt_code="903",
            ssp=None,
        )

        executor = MigrationExecutor(connection)
        executor.migrate(migrate_to)
        new_apps = executor.loader.project_state(migrate_to).apps
        Program = new_apps.get_model("stts", "Program")
        SttProgramParticipation = new_apps.get_model(
            "stts", "SttProgramParticipation"
        )

        ssp_program = Program.objects.get(slug="ssp")
        assert ssp_program.name == "SSP"
        assert SttProgramParticipation.objects.filter(
            stt_id=active_stt.id,
            program=ssp_program,
            status="ACTIVE",
        ).exists()
        assert not SttProgramParticipation.objects.filter(
            stt_id=inactive_stt.id,
            program=ssp_program,
        ).exists()
        assert not SttProgramParticipation.objects.filter(
            stt_id=null_stt.id,
            program=ssp_program,
        ).exists()
    finally:
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
