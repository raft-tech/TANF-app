"""Tests for ETL runner services."""

from unittest.mock import patch

from django.db import IntegrityError, transaction

import pytest

from tdpservice.etl.exceptions import ActivePipelineRunError, PipelineValidationError
from tdpservice.etl.models import ETLNodeRun, ETLPipelineRun
from tdpservice.etl.registry import (
    NodeResult,
    PipelineDefinition,
    PipelineNode,
    get_pipeline_definition,
)
from tdpservice.etl.runner import NodeExecutor, PipelineRunCreator, output_scope_key


def _noop(context):
    """No-op node implementation for graph tests."""
    return None


def _definition(nodes):
    """Build a minimal pipeline definition."""
    return PipelineDefinition(
        key="test_pipeline",
        version="1",
        display_name="Test Pipeline",
        description="Pipeline used by runner tests.",
        nodes=tuple(nodes),
        allowed_parameters={"fiscal_year": {"required": True}},
    )


def _create_pipeline_run():
    """Create a statistical weights pipeline run for runner tests."""
    return PipelineRunCreator.for_pipeline_key("tanf_statistical_weights").create(
        parameters={"fiscal_year": 2026},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )


def test_pipeline_canvas_uses_chord_for_extract_fan_in():
    """The pipeline-owned Canvas expresses the DAG without a layer compiler."""
    definition = get_pipeline_definition("tanf_statistical_weights")

    canvas_graph = definition.build_canvas(pipeline_run_id=1)
    chord_task = canvas_graph.tasks[1]

    canvas_repr = repr(canvas_graph)
    assert chord_task.name == "celery.chord"
    assert [task.args[1] for task in chord_task.tasks] == [
        "extract_t1_family_counts",
        "extract_t6_case_counts",
        "extract_t7_section_case_counts",
    ]
    assert chord_task.body.args[1] == "build_weight_candidates"
    assert chord_task.body.immutable
    downstream_chain = chord_task.body.options["link"][0]
    assert downstream_chain.immutable
    assert [task.args[1] for task in downstream_chain.tasks[:3]] == [
        "run_weights_qa",
        "publish_weights",
        "notify_weights_run",
    ]
    assert (
        downstream_chain.tasks[3].name == "tdpservice.etl.tasks.finalize_pipeline_run"
    )
    assert all(task.immutable for task in downstream_chain.tasks)
    assert "validate_parameters" in canvas_repr
    assert "extract_t1_family_counts" in canvas_repr
    assert "extract_t6_case_counts" in canvas_repr
    assert "extract_t7_section_case_counts" in canvas_repr
    assert "build_weight_candidates" in canvas_repr
    assert "advance_pipeline_run" not in canvas_repr


def test_pipeline_validation_rejects_duplicate_node_keys():
    """Pipeline node keys must be unique for execution lookup."""
    definition = _definition(
        [
            PipelineNode("extract", _noop),
            PipelineNode("extract", _noop),
        ]
    )

    with pytest.raises(PipelineValidationError):
        definition.validate()


def test_pipeline_build_canvas_requires_canvas_builder():
    """Pipeline definitions must own an executable Canvas declaration."""
    definition = _definition([PipelineNode("extract", _noop)])

    with pytest.raises(PipelineValidationError):
        definition.build_canvas(pipeline_run_id=1)


def test_validate_run_parameters_normalizes_fiscal_year():
    """Fiscal year input is normalized for output-scope idempotency."""
    definition = _definition([PipelineNode("extract", _noop)])

    assert definition.validate_parameters({"fiscal_year": "2026"}) == {
        "fiscal_year": 2026
    }


def test_validate_run_parameters_rejects_unknown_parameters():
    """Only code-defined pipeline parameters are accepted."""
    definition = _definition([PipelineNode("extract", _noop)])

    with pytest.raises(PipelineValidationError):
        definition.validate_parameters({"fiscal_year": 2026, "raw_sql": "select 1"})


@pytest.mark.django_db
def test_active_run_scope_key_constraint_allows_completed_reruns():
    """The database rejects duplicate active scopes and allows completed reruns."""
    definition = get_pipeline_definition("tanf_statistical_weights")
    parameters = {"fiscal_year": 2026}
    scope = definition.output_scope(parameters)
    scope_key = output_scope_key(scope)

    ETLPipelineRun.objects.create(
        pipeline_key=definition.key,
        pipeline_version=definition.version,
        status=ETLPipelineRun.Status.PENDING,
        parameters=parameters,
        output_scope=scope,
        output_scope_key=scope_key,
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            ETLPipelineRun.objects.create(
                pipeline_key=definition.key,
                pipeline_version=definition.version,
                status=ETLPipelineRun.Status.RUNNING,
                parameters=parameters,
                output_scope=scope,
                output_scope_key=scope_key,
                trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
            )

    ETLPipelineRun.objects.create(
        pipeline_key=definition.key,
        pipeline_version=definition.version,
        status=ETLPipelineRun.Status.SUCCEEDED,
        parameters=parameters,
        output_scope=scope,
        output_scope_key=scope_key,
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )


@pytest.mark.django_db
def test_create_pipeline_run_reports_active_scope():
    """Run creation converts active-scope conflicts into a domain error."""
    creator = PipelineRunCreator.for_pipeline_key("tanf_statistical_weights")
    first_run = creator.create(
        parameters={"fiscal_year": 2026},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    with pytest.raises(ActivePipelineRunError):
        creator.create(
            parameters={"fiscal_year": 2026},
            trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
        )

    first_run.status = ETLPipelineRun.Status.SUCCEEDED
    first_run.save(update_fields=["status", "updated_at"])
    second_run = creator.create(
        parameters={"fiscal_year": 2026},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    assert second_run.output_scope_key == first_run.output_scope_key


@pytest.mark.django_db
def test_execute_node_ignores_already_succeeded_node():
    """Duplicate task delivery does not run a node implementation twice."""
    calls = []

    def implementation(context):
        calls.append(context.node.key)
        return NodeResult(output_row_count=1)

    definition = _definition([PipelineNode("extract", implementation)])
    parameters = {"fiscal_year": 2026}
    scope = definition.output_scope(parameters)
    pipeline_run = ETLPipelineRun.objects.create(
        pipeline_key=definition.key,
        pipeline_version=definition.version,
        status=ETLPipelineRun.Status.RUNNING,
        parameters=parameters,
        output_scope=scope,
        output_scope_key=output_scope_key(scope),
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )
    ETLNodeRun.objects.create(pipeline_run=pipeline_run, node_key="extract")

    with patch(
        "tdpservice.etl.runner.get_pipeline_definition", return_value=definition
    ):
        first_result = NodeExecutor.for_run_id(pipeline_run.id, "extract").execute()
        second_result = NodeExecutor.for_run_id(pipeline_run.id, "extract").execute()

    assert first_result == {
        "node_key": "extract",
        "status": ETLNodeRun.Status.SUCCEEDED,
    }
    assert second_result == {
        "node_key": "extract",
        "status": ETLNodeRun.Status.SUCCEEDED,
        "already_started": True,
    }
    assert calls == ["extract"]


@pytest.mark.django_db
def test_execute_node_fails_missing_input_contracts():
    """Nodes fail before implementation when declared intermediate inputs are missing."""
    pipeline_run = _create_pipeline_run()
    pipeline_run.node_runs.filter(
        node_key__in=[
            "validate_parameters",
            "extract_t1_family_counts",
            "extract_t6_case_counts",
            "extract_t7_section_case_counts",
        ]
    ).update(status=ETLNodeRun.Status.SUCCEEDED)

    with pytest.raises(PipelineValidationError):
        NodeExecutor.for_run_id(
            pipeline_run.id,
            "build_weight_candidates",
        ).execute()

    node_run = pipeline_run.node_runs.get(node_key="build_weight_candidates")
    pipeline_run.refresh_from_db()
    assert node_run.status == ETLNodeRun.Status.FAILED
    assert "Missing input contracts" in node_run.error_message
    assert pipeline_run.status == ETLPipelineRun.Status.FAILED
