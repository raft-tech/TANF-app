"""Tests for statistical weights ETL nodes."""

from decimal import Decimal

from django.core import mail

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.etl.models import (
    ETLIntermediateOutput,
    ETLOutput,
    ETLPipelineRun,
    ETLQAResult,
    StatisticalWeight,
)
from tdpservice.etl.pipelines.sources import SOURCE_DATAFILE_IDS_KEY
from tdpservice.etl.pipelines.statistical_weights import StatisticalWeightsPipeline
from tdpservice.etl.registry import get_pipeline_definition
from tdpservice.etl.runner import NodeContext, PipelineRunCreator
from tdpservice.search_indexes.models.ssp import SSP_M1, SSP_M6, SSP_M7
from tdpservice.search_indexes.models.tanf import TANF_T1, TANF_T6, TANF_T7
from tdpservice.search_indexes.models.tribal import (
    Tribal_TANF_T1,
    Tribal_TANF_T6,
    Tribal_TANF_T7,
)
from tdpservice.stts.models import STT

FISCAL_YEAR = 2026
REPORTING_MONTH = 202501
PIPELINE = StatisticalWeightsPipeline()
NODES = PIPELINE.node_handlers
TANF_PROGRAM = DataFile.ProgramType.TANF


def _datafile(stt, user, section, version=1, program_type=TANF_PROGRAM):
    """Create a parse-completed DataFile in the weights fiscal year."""
    return DataFileFactory.create(
        stt=stt,
        user=user,
        section=section,
        program_type=program_type,
        quarter=DataFile.Quarter.Q1,
        year=FISCAL_YEAR,
        version=version,
        state=SubmissionState.PARSE_COMPLETED,
    )


def _node_context(pipeline_run, node_key):
    """Build a node context for direct node execution."""
    definition = get_pipeline_definition(pipeline_run.pipeline_key)
    return NodeContext(
        pipeline_run=pipeline_run,
        node=definition.node_map[node_key],
        upstream_outputs={
            output.output_key: output for output in pipeline_run.outputs.all()
        },
        intermediate_outputs={
            output.output_key: output
            for output in pipeline_run.intermediate_outputs.all()
        },
    )


def _create_pipeline_run(program=TANF_PROGRAM):
    """Create a statistical weights pipeline run."""
    return PipelineRunCreator.for_pipeline_key(StatisticalWeightsPipeline.key).create(
        parameters={"fiscal_year": FISCAL_YEAR, "program": program},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )


@pytest.fixture
def parsed_weights_data(stt, user):
    """Create parsed T1/T6/T7 rows for statistical weights tests."""
    stt.sample = True
    stt.save()

    old_active_file = _datafile(
        stt,
        user,
        DataFile.Section.ACTIVE_CASE_DATA,
        version=1,
    )
    current_active_file = _datafile(
        stt,
        user,
        DataFile.Section.ACTIVE_CASE_DATA,
        version=2,
    )
    aggregate_file = _datafile(stt, user, DataFile.Section.AGGREGATE_DATA)
    stratum_file = _datafile(stt, user, DataFile.Section.STRATUM_DATA)

    TANF_T1.objects.create(
        datafile=old_active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="OLD0000001",
        STRATUM="9",
    )
    TANF_T1.objects.create(
        datafile=current_active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="CASE000001",
        STRATUM="1",
    )
    TANF_T1.objects.create(
        datafile=current_active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="CASE000002",
        STRATUM="1",
    )
    TANF_T1.objects.create(
        datafile=current_active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="CASE000002",
        STRATUM="1",
    )
    TANF_T1.objects.create(
        datafile=current_active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="CASE000003",
        STRATUM="2",
    )

    TANF_T6.objects.create(
        datafile=aggregate_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        NUM_FAMILIES=10,
    )
    TANF_T7.objects.create(
        datafile=stratum_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        TDRS_SECTION_IND="1",
        STRATUM="1",
        FAMILIES_MONTH=8,
    )

    return stt


@pytest.mark.django_db
def test_validate_parameters_rejects_missing_source_datafiles():
    """Runs fail early when there are no accepted source files to snapshot."""
    pipeline_run = _create_pipeline_run()

    with pytest.raises(ValueError, match="active, aggregate, stratum"):
        NODES.validate_parameters(_node_context(pipeline_run, "validate_parameters"))

    pipeline_run.refresh_from_db()
    assert pipeline_run.metadata[SOURCE_DATAFILE_IDS_KEY] == {
        "active": [],
        "aggregate": [],
        "stratum": [],
    }


@pytest.mark.django_db
def test_build_candidates_uses_latest_files_and_stratum_fallback(parsed_weights_data):
    """Weights use latest accepted files and prefer T7 stratum counts over T6."""
    source_ids = PIPELINE.node_handlers.sources.snapshot_source_datafile_ids(
        FISCAL_YEAR,
        TANF_PROGRAM,
    )
    candidates = PIPELINE.node_handlers.candidates.build(
        FISCAL_YEAR,
        PIPELINE.node_handlers.extractor.active_family_counts(
            source_ids[PIPELINE.source_keys["active"]],
            TANF_PROGRAM,
        ),
        PIPELINE.node_handlers.extractor.aggregate_case_counts(
            source_ids[PIPELINE.source_keys["aggregate"]],
            TANF_PROGRAM,
        ),
        PIPELINE.node_handlers.extractor.stratum_section_case_counts(
            source_ids[PIPELINE.source_keys["stratum"]],
            TANF_PROGRAM,
        ),
        TANF_PROGRAM,
    )

    assert len(candidates) == 2
    assert {candidate.stratum for candidate in candidates} == {"1", "2"}

    stratum_one = next(
        candidate for candidate in candidates if candidate.stratum == "1"
    )
    assert stratum_one.case_count == 2
    assert stratum_one.cases == 8
    assert stratum_one.weight == Decimal("4.0000")

    stratum_two = next(
        candidate for candidate in candidates if candidate.stratum == "2"
    )
    assert stratum_two.case_count == 1
    assert stratum_two.cases == 10
    assert stratum_two.weight == Decimal("10.0000")


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "program",
        "program_type",
        "active_model",
        "aggregate_model",
        "stratum_model",
        "aggregate_field",
    ),
    [
        (
            DataFile.ProgramType.SSP,
            DataFile.ProgramType.SSP,
            SSP_M1,
            SSP_M6,
            SSP_M7,
            "SSPMOE_FAMILIES",
        ),
        (
            DataFile.ProgramType.TRIBAL,
            DataFile.ProgramType.TRIBAL,
            Tribal_TANF_T1,
            Tribal_TANF_T6,
            Tribal_TANF_T7,
            "NUM_FAMILIES",
        ),
    ],
)
def test_program_adapters_build_non_tanf_candidates(
    stt,
    user,
    program,
    program_type,
    active_model,
    aggregate_model,
    stratum_model,
    aggregate_field,
):
    """SSP and Tribal runs use program-specific parsed models and fields."""
    active_file = _datafile(
        stt,
        user,
        DataFile.Section.ACTIVE_CASE_DATA,
        program_type=program_type,
    )
    aggregate_file = _datafile(
        stt,
        user,
        DataFile.Section.AGGREGATE_DATA,
        program_type=program_type,
    )
    stratum_file = _datafile(
        stt,
        user,
        DataFile.Section.STRATUM_DATA,
        program_type=program_type,
    )

    active_model.objects.create(
        datafile=active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="CASE000001",
        STRATUM="1",
    )
    active_model.objects.create(
        datafile=active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="CASE000002",
        STRATUM="1",
    )
    aggregate_model.objects.create(
        datafile=aggregate_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        **{aggregate_field: 12},
    )
    stratum_model.objects.create(
        datafile=stratum_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        TDRS_SECTION_IND="1",
        STRATUM="1",
        FAMILIES_MONTH=6,
    )

    source_ids = PIPELINE.node_handlers.sources.snapshot_source_datafile_ids(
        FISCAL_YEAR,
        program,
    )
    candidates = PIPELINE.node_handlers.candidates.build(
        FISCAL_YEAR,
        PIPELINE.node_handlers.extractor.active_family_counts(
            source_ids[PIPELINE.source_keys["active"]],
            program,
        ),
        PIPELINE.node_handlers.extractor.aggregate_case_counts(
            source_ids[PIPELINE.source_keys["aggregate"]],
            program,
        ),
        PIPELINE.node_handlers.extractor.stratum_section_case_counts(
            source_ids[PIPELINE.source_keys["stratum"]],
            program,
        ),
        program,
    )

    assert len(candidates) == 1
    assert candidates[0].program == program
    assert candidates[0].case_count == 2
    assert candidates[0].cases == 6
    assert candidates[0].weight == Decimal("3.0000")


@pytest.mark.django_db
def test_validate_parameters_snapshots_source_files(parsed_weights_data, user):
    """A run continues to use the DataFile snapshot captured during validation."""
    pipeline_run = _create_pipeline_run()
    NODES.validate_parameters(_node_context(pipeline_run, "validate_parameters"))

    newer_file = _datafile(
        parsed_weights_data,
        user,
        DataFile.Section.ACTIVE_CASE_DATA,
        version=3,
    )
    TANF_T1.objects.create(
        datafile=newer_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="NEW0000001",
        STRATUM="8",
    )

    result = NODES.extract_active_family_counts(
        _node_context(pipeline_run, "extract_active_family_counts")
    )
    intermediate = pipeline_run.intermediate_outputs.get(
        output_key=PIPELINE.intermediate_keys["s1"]
    )

    assert result.output_row_count == 2
    assert {row["stratum"] for row in intermediate.payload} == {"1", "2"}


@pytest.mark.django_db
def test_extract_nodes_write_intermediate_outputs(parsed_weights_data):
    """Extract nodes persist their declared run-scoped output contracts."""
    pipeline_run = _create_pipeline_run()
    NODES.validate_parameters(_node_context(pipeline_run, "validate_parameters"))

    NODES.extract_active_family_counts(
        _node_context(pipeline_run, "extract_active_family_counts")
    )
    NODES.extract_aggregate_case_counts(
        _node_context(pipeline_run, "extract_aggregate_case_counts")
    )
    NODES.extract_stratum_case_counts(
        _node_context(pipeline_run, "extract_stratum_case_counts")
    )

    outputs = {
        output.output_key: output
        for output in ETLIntermediateOutput.objects.filter(pipeline_run=pipeline_run)
    }
    assert outputs[PIPELINE.intermediate_keys["s1"]].row_count == 2
    assert outputs[PIPELINE.intermediate_keys["s3"]].row_count == 1
    assert outputs[PIPELINE.intermediate_keys["s4"]].row_count == 1


@pytest.mark.django_db
def test_qa_and_publish_use_persisted_candidates(parsed_weights_data):
    """QA and publication consume intermediate payloads, not live source queries."""
    pipeline_run = _create_pipeline_run()
    NODES.validate_parameters(_node_context(pipeline_run, "validate_parameters"))
    NODES.extract_active_family_counts(
        _node_context(pipeline_run, "extract_active_family_counts")
    )
    NODES.extract_aggregate_case_counts(
        _node_context(pipeline_run, "extract_aggregate_case_counts")
    )
    NODES.extract_stratum_case_counts(
        _node_context(pipeline_run, "extract_stratum_case_counts")
    )
    NODES.build_weight_candidates(
        _node_context(pipeline_run, "build_weight_candidates")
    )

    TANF_T1.objects.all().delete()
    TANF_T6.objects.all().delete()
    TANF_T7.objects.all().delete()

    qa_result = NODES.run_weights_qa(_node_context(pipeline_run, "run_weights_qa"))
    publish_result = NODES.publish_weights(
        _node_context(pipeline_run, "publish_weights")
    )

    assert qa_result.output_row_count == 4
    assert publish_result.metadata == {
        "program": TANF_PROGRAM,
        "version": 1,
        "row_count": 2,
    }
    assert StatisticalWeight.objects.filter(pipeline_run=pipeline_run).count() == 2


@pytest.mark.django_db
def test_missing_stt_qa_uses_stt_reference_data(parsed_weights_data, region):
    """Required T1/T6 STTs come from state and territory STT records."""
    STT.objects.create(
        name="Guam",
        region=region,
        stt_code="66",
        type=STT.EntityType.TERRITORY,
    )
    STT.objects.create(
        name="Example Tribe",
        region=region,
        stt_code="001",
        type=STT.EntityType.TRIBE,
    )
    pipeline_run = _create_pipeline_run()
    NODES.validate_parameters(_node_context(pipeline_run, "validate_parameters"))
    NODES.extract_active_family_counts(
        _node_context(pipeline_run, "extract_active_family_counts")
    )
    NODES.extract_aggregate_case_counts(
        _node_context(pipeline_run, "extract_aggregate_case_counts")
    )
    NODES.extract_stratum_case_counts(
        _node_context(pipeline_run, "extract_stratum_case_counts")
    )
    NODES.build_weight_candidates(
        _node_context(pipeline_run, "build_weight_candidates")
    )

    NODES.run_weights_qa(_node_context(pipeline_run, "run_weights_qa"))

    qa_result = ETLQAResult.objects.get(
        pipeline_run=pipeline_run,
        check_key="weights_missing_stts",
    )
    assert qa_result.result_payload["s1_missing"] == [66]
    assert qa_result.result_payload["s3_missing"] == [66]
    assert qa_result.result_payload["s4_missing"] == []


@pytest.mark.django_db
def test_publish_weights_rejects_empty_candidates():
    """Empty candidate payloads cannot become successful output versions."""
    pipeline_run = _create_pipeline_run()
    NODES.outputs.write(
        pipeline_run,
        PIPELINE.intermediate_keys["candidates"],
        [],
    )

    with pytest.raises(ValueError, match="No statistical weight candidates"):
        NODES.publish_weights(_node_context(pipeline_run, "publish_weights"))

    assert not StatisticalWeight.objects.filter(pipeline_run=pipeline_run).exists()
    assert not ETLOutput.objects.filter(
        pipeline_run=pipeline_run,
        output_key=PIPELINE.output_key,
    ).exists()


@pytest.mark.django_db
def test_publish_weights_versions_outputs(parsed_weights_data):
    """Reruns publish a new version and retain the prior version until purge."""
    first_run = _create_pipeline_run()
    NODES.validate_parameters(_node_context(first_run, "validate_parameters"))
    NODES.extract_active_family_counts(
        _node_context(first_run, "extract_active_family_counts")
    )
    NODES.extract_aggregate_case_counts(
        _node_context(first_run, "extract_aggregate_case_counts")
    )
    NODES.extract_stratum_case_counts(
        _node_context(first_run, "extract_stratum_case_counts")
    )
    NODES.build_weight_candidates(_node_context(first_run, "build_weight_candidates"))
    first_result = NODES.publish_weights(_node_context(first_run, "publish_weights"))
    first_run.status = ETLPipelineRun.Status.SUCCEEDED
    first_run.save(update_fields=["status", "updated_at"])

    assert first_result.metadata == {
        "program": TANF_PROGRAM,
        "version": 1,
        "row_count": 2,
    }
    assert StatisticalWeight.objects.filter(version=1).count() == 2

    second_run = _create_pipeline_run()
    NODES.validate_parameters(_node_context(second_run, "validate_parameters"))
    NODES.extract_active_family_counts(
        _node_context(second_run, "extract_active_family_counts")
    )
    NODES.extract_aggregate_case_counts(
        _node_context(second_run, "extract_aggregate_case_counts")
    )
    NODES.extract_stratum_case_counts(
        _node_context(second_run, "extract_stratum_case_counts")
    )
    NODES.build_weight_candidates(_node_context(second_run, "build_weight_candidates"))
    second_result = NODES.publish_weights(_node_context(second_run, "publish_weights"))

    assert second_result.metadata == {
        "program": TANF_PROGRAM,
        "version": 2,
        "row_count": 2,
    }
    assert StatisticalWeight.objects.filter(version=2).count() == 2
    assert (
        StatisticalWeight.objects.filter(
            version=1,
            retention_expires_at__isnull=False,
        ).count()
        == 2
    )
    assert (
        StatisticalWeight.objects.filter(
            version=2,
            retention_expires_at__isnull=True,
        ).count()
        == 2
    )

    output = second_run.outputs.get(output_key=PIPELINE.output_key)
    assert output.output_version == 2
    assert output.row_count == 2
    assert output.published


@pytest.mark.django_db
def test_notify_weights_run_includes_operational_summary(
    ofa_system_admin,
    digit_team,
):
    """Statistical weights notification includes status, row count, QA, and run URL."""
    pipeline_run = _create_pipeline_run()
    pipeline_run.status = ETLPipelineRun.Status.RUNNING
    pipeline_run.save(update_fields=["status", "updated_at"])
    ETLOutput.objects.create(
        pipeline_run=pipeline_run,
        output_key=PIPELINE.output_key,
        output_kind=ETLOutput.OutputKind.TABLE,
        reference=StatisticalWeight._meta.db_table,
        output_version=3,
        row_count=2,
        published=True,
        metadata=pipeline_run.output_scope,
    )
    ETLQAResult.objects.create(
        pipeline_run=pipeline_run,
        check_key="weights_row_counts",
        status=ETLQAResult.Status.PASSED,
        summary="Captured statistical weights row counts.",
        result_payload={"candidate_output": 2},
    )

    result = NODES.notify_weights_run(_node_context(pipeline_run, "notify_weights_run"))

    assert result.metadata["notification"] == "sent"
    assert len(mail.outbox) == 1
    message = mail.outbox[0].body
    assert "Pipeline: TANF Statistical Weights" in message
    assert f"Run ID: {pipeline_run.id}" in message
    assert "Status: SUCCEEDED" in message
    assert "Trigger Source: ADMIN" in message
    assert "Row Count: 2" in message
    assert "weights_row_counts: PASSED" in message
    assert f"/etl/runs/{pipeline_run.id}/" in message
