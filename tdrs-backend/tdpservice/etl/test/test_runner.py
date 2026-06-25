"""Tests for ETL runner graph validation."""

from unittest.mock import patch

from django.db import IntegrityError, transaction

import pytest

from tdpservice.etl.models import ETLNodeRun, ETLPipelineRun
from tdpservice.etl.registry import (
    NodeDefinition,
    NodeResult,
    PipelineDefinition,
    get_pipeline_definition,
)
from tdpservice.etl.runner import (
    ActivePipelineRunError,
    PipelineValidationError,
    advance_pipeline_run,
    build_layer_canvas,
    create_pipeline_run,
    execute_node,
    output_scope_key,
    topological_layers,
    validate_run_parameters,
)


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


def test_topological_layers_groups_ready_nodes():
    """Independent branches are returned in the same dependency layer."""
    definition = _definition(
        [
            NodeDefinition("extract", (), _noop),
            NodeDefinition("branch_a", ("extract",), _noop),
            NodeDefinition("branch_b", ("extract",), _noop),
            NodeDefinition("publish", ("branch_a", "branch_b"), _noop),
        ]
    )

    assert topological_layers(definition) == [
        ["extract"],
        ["branch_a", "branch_b"],
        ["publish"],
    ]


def test_parallel_layer_canvas_advances_to_layer_scheduler_only():
    """Parallel layers schedule one layer-advancer callback, not downstream nodes."""
    definition = get_pipeline_definition("tanf_statistical_weights")

    canvas_graph = build_layer_canvas(definition, pipeline_run_id=1, layer_index=1)

    canvas_repr = repr(canvas_graph)
    assert "extract_t1_family_counts" in canvas_repr
    assert "extract_t6_case_counts" in canvas_repr
    assert "extract_t7_section_case_counts" in canvas_repr
    assert "advance_pipeline_run" in canvas_repr
    assert "run_weights_qa" not in canvas_repr
    assert "publish_weights" not in canvas_repr
    assert "notify_weights_run" not in canvas_repr


def test_topological_layers_rejects_cycles():
    """A cyclic pipeline definition fails validation."""
    definition = _definition(
        [
            NodeDefinition("a", ("b",), _noop),
            NodeDefinition("b", ("a",), _noop),
        ]
    )

    with pytest.raises(PipelineValidationError):
        topological_layers(definition)


def test_validate_run_parameters_normalizes_fiscal_year():
    """Fiscal year input is normalized for output-scope idempotency."""
    definition = _definition([NodeDefinition("extract", (), _noop)])

    assert validate_run_parameters(definition, {"fiscal_year": "2026"}) == {
        "fiscal_year": 2026
    }


def test_validate_run_parameters_rejects_unknown_parameters():
    """Only code-defined pipeline parameters are accepted."""
    definition = _definition([NodeDefinition("extract", (), _noop)])

    with pytest.raises(PipelineValidationError):
        validate_run_parameters(
            definition,
            {"fiscal_year": 2026, "raw_sql": "select 1"},
        )


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
    first_run = create_pipeline_run(
        pipeline_key="tanf_statistical_weights",
        parameters={"fiscal_year": 2026},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    with pytest.raises(ActivePipelineRunError):
        create_pipeline_run(
            pipeline_key="tanf_statistical_weights",
            parameters={"fiscal_year": 2026},
            trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
        )

    first_run.status = ETLPipelineRun.Status.SUCCEEDED
    first_run.save(update_fields=["status", "updated_at"])
    second_run = create_pipeline_run(
        pipeline_key="tanf_statistical_weights",
        parameters={"fiscal_year": 2026},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    assert second_run.output_scope_key == first_run.output_scope_key


@pytest.mark.django_db
def test_advance_pipeline_run_waits_for_prior_layers():
    """Duplicate or early callbacks do not advance before dependencies finish."""
    pipeline_run = create_pipeline_run(
        pipeline_key="tanf_statistical_weights",
        parameters={"fiscal_year": 2026},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    result = advance_pipeline_run(pipeline_run.id, layer_index=1)

    assert result["status"] == "waiting_on_dependencies"
    assert result["dependency_status"] == {
        "validate_parameters": ETLNodeRun.Status.PENDING
    }


@pytest.mark.django_db
def test_execute_node_ignores_already_succeeded_node():
    """Duplicate task delivery does not run a node implementation twice."""
    calls = []

    def implementation(context):
        calls.append(context.node.key)
        return NodeResult(output_row_count=1)

    definition = _definition([NodeDefinition("extract", (), implementation)])
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
        first_result = execute_node(pipeline_run.id, "extract")
        second_result = execute_node(pipeline_run.id, "extract")

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
    pipeline_run = create_pipeline_run(
        pipeline_key="tanf_statistical_weights",
        parameters={"fiscal_year": 2026},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )
    pipeline_run.node_runs.filter(
        node_key__in=[
            "validate_parameters",
            "extract_t1_family_counts",
            "extract_t6_case_counts",
            "extract_t7_section_case_counts",
        ]
    ).update(status=ETLNodeRun.Status.SUCCEEDED)

    with pytest.raises(PipelineValidationError):
        execute_node(pipeline_run.id, "build_weight_candidates")

    node_run = pipeline_run.node_runs.get(node_key="build_weight_candidates")
    pipeline_run.refresh_from_db()
    assert node_run.status == ETLNodeRun.Status.FAILED
    assert "Missing input contracts" in node_run.error_message
    assert pipeline_run.status == ETLPipelineRun.Status.FAILED
