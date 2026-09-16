"""Tests for shared ETL source snapshot helpers."""

from django.db import transaction

import pytest

from tdpservice.data_files.enums import ProgramCode, SectionName, SubmissionState
from tdpservice.data_files.models import DataFile, ReparseFileMeta
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.etl.models import ETLPipelineRun
from tdpservice.etl.pipelines.sources import (
    ActiveReparseDataFileOverlapError,
    DataFileSource,
    DataFileSourceSnapshot,
)
from tdpservice.etl.runner import PipelineRunFactory
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta

FISCAL_YEAR = 2026


def _datafile(stt, user, version):
    """Create a parse-completed TANF active DataFile."""
    return DataFileFactory.create(
        stt=stt,
        user=user,
        section=SectionName.ACTIVE_CASE_DATA,
        program_type=ProgramCode.TANF,
        quarter=DataFile.Quarter.Q1,
        year=FISCAL_YEAR,
        version=version,
        state=SubmissionState.PARSE_COMPLETED,
    )


def _pipeline_run():
    """Create a statistical weights pipeline run for snapshot tests."""
    return PipelineRunFactory.for_pipeline_key("statistical_weights").create(
        parameters={"fiscal_year": FISCAL_YEAR, "program": ProgramCode.TANF},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )


@pytest.mark.django_db
def test_datafile_source_snapshotter_reuses_existing_snapshot(stt, user):
    """A run keeps using its first DataFile snapshot even after newer files land."""
    _datafile(stt, user, version=1)
    current_file = _datafile(stt, user, version=2)
    pipeline_run = _pipeline_run()
    source = DataFileSource(
        key="active",
        program_type=ProgramCode.TANF,
        section=SectionName.ACTIVE_CASE_DATA,
    )
    snapshotter = DataFileSourceSnapshot()

    first_snapshot = snapshotter.snapshot(
        pipeline_run,
        fiscal_year=FISCAL_YEAR,
        sources=(source,),
    )
    _datafile(stt, user, version=3)
    second_snapshot = snapshotter.snapshot(
        pipeline_run,
        fiscal_year=FISCAL_YEAR,
        sources=(source,),
    )

    assert first_snapshot == {"active": [current_file.id]}
    assert second_snapshot == first_snapshot


@pytest.mark.django_db
def test_datafile_source_snapshotter_rejects_duplicate_source_keys(stt, user):
    """Source keys must be unique so downstream nodes receive stable contracts."""
    source = DataFileSource(
        key="active",
        program_type=ProgramCode.TANF,
        section=SectionName.ACTIVE_CASE_DATA,
    )
    snapshotter = DataFileSourceSnapshot()

    with pytest.raises(ValueError, match="source keys must be unique"):
        with transaction.atomic():
            snapshotter.snapshot(
                _pipeline_run(),
                fiscal_year=FISCAL_YEAR,
                sources=(source, source),
            )


@pytest.mark.django_db
def test_datafile_source_snapshotter_rejects_active_reparse_overlap(stt, user):
    """ETL source snapshots cannot include DataFiles being reparsed."""
    data_file = _datafile(stt, user, version=1)
    reparse = ReparseMeta.objects.create(db_backup_location="s3://backup")
    ReparseFileMeta.objects.create(data_file=data_file, reparse_meta=reparse)
    source = DataFileSource(
        key="active",
        program_type=ProgramCode.TANF,
        section=SectionName.ACTIVE_CASE_DATA,
    )
    snapshotter = DataFileSourceSnapshot()

    with pytest.raises(ActiveReparseDataFileOverlapError, match=str(data_file.id)):
        snapshotter.snapshot(
            _pipeline_run(),
            fiscal_year=FISCAL_YEAR,
            sources=(source,),
        )


@pytest.mark.django_db
def test_datafile_source_uses_canonical_classification_and_excludes_audits(stt, user):
    """Source selection uses canonical classification and excludes PIA versions."""
    standard_file = _datafile(stt, user, version=1)
    DataFileFactory.create(
        stt=stt,
        user=user,
        section=standard_file.section,
        quarter=standard_file.quarter,
        year=FISCAL_YEAR,
        version=2,
        state=SubmissionState.PARSE_COMPLETED,
        is_program_audit=True,
    )
    source = DataFileSource(
        key="active",
        program_type=ProgramCode.TANF,
        section=SectionName.ACTIVE_CASE_DATA,
    )

    result = DataFileSourceSnapshot().latest_datafile_ids(FISCAL_YEAR, source)

    assert result == [standard_file.id]
