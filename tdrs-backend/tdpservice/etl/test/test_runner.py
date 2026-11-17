"""Tests for ETL runner services."""

from collections.abc import Callable
from unittest.mock import patch

from django.db import IntegrityError, transaction

import pytest

from tdpservice.data_files.models import Program
from tdpservice.etl.exceptions import ActivePipelineRunError, PipelineValidationError
from tdpservice.etl.models import ETLArtifact, ETLNodeRun, ETLPipelineRun
from tdpservice.etl.pipelines.base import (
    NodeResult,
    PipelineDefinition,
    PipelineNode,
    PipelineNodeRegistry,
)
from tdpservice.etl.registry import get_pipeline_definition
from tdpservice.etl.runner import (
    PipelineRunFactory,
    PipelineRunLauncher,
    output_scope_key,
)
from tdpservice.etl.tasks import finalize_pipeline_run, run_pipeline_node


def _noop(context) -> None:
    """No-op node handler for graph tests."""
    return None


class DummyPipelineNode(PipelineNode):
    """Minimal concrete node for runner tests."""

    def __init__(
        self,
        key: str,
        operation: Callable[[object], NodeResult | None] | None = None,
        *,
        input_contracts: tuple[str, ...] = (),
        output_contracts: tuple[str, ...] = (),
    ):
        """Initialize a test node with configurable execution."""
        self._key = key
        self.operation = operation or _noop
        self.input_contracts = input_contracts
        self.output_contracts = output_contracts

    @property
    def key(self) -> str:
        """Return the stable test node key."""
        return self._key

    def execute(self, context) -> NodeResult | None:
        """Run the configured test operation."""
        return self.operation(context)


def _node(key: str, operation=None, **kwargs):
    """Build a concrete test node with a stable key."""
    return DummyPipelineNode(key, operation, **kwargs)


class ConcretePipelineDefinition(PipelineDefinition):
    """Minimal concrete pipeline definition for runner tests."""

    key = "test_pipeline"
    version = "1"
    display_name = "Test Pipeline"
    description = "Pipeline used by runner tests."
    allowed_parameters = {"fiscal_year": {"required": True}}

    def __init__(
        self,
        nodes,
        handlers=None,
        *,
        completion_keys: tuple[str, ...] = (),
        canvas_builder=None,
    ):
        """Initialize a test pipeline with configurable nodes."""
        self.nodes = PipelineNodeRegistry(nodes)
        self.handlers = handlers or {}
        self.completion_keys = completion_keys
        self._canvas_builder = canvas_builder

    def extract(self, context):
        """Run a configurable extract handler."""
        return self.handlers.get("extract", _noop)(context)

    def consume(self, context):
        """Run a configurable consume handler."""
        return self.handlers["consume"](context)

    def validate_parameters(self, parameters: dict) -> dict:
        """Return test parameters unchanged."""
        return dict(parameters or {})

    def output_scope(self, parameters: dict) -> dict:
        """Return a simple fiscal-year output scope."""
        return {
            "pipeline": self.key,
            "fiscal_year": int(parameters["fiscal_year"]),
        }

    def _pipeline_nodes(self) -> PipelineNodeRegistry:
        """Return configured test node declarations."""
        return self.nodes

    def build_canvas(self, pipeline_run_id: int):
        """Return configured Canvas or raise if none was provided."""
        if self._canvas_builder is not None:
            return self._canvas_builder(self, pipeline_run_id)
        raise PipelineValidationError(
            f"Pipeline {self.key} does not define an executable Celery Canvas."
        )


def _definition(nodes, handlers=None, **kwargs):
    """Build a minimal pipeline definition."""
    return ConcretePipelineDefinition(nodes, handlers, **kwargs)


def _create_pipeline_run():
    """Create a statistical weights pipeline run for runner tests."""
    return PipelineRunFactory.for_pipeline_key("statistical_weights").create(
        parameters={"fiscal_year": 2026, "program": Program.Code.TANF},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )


def test_pipeline_canvas_uses_chord_for_extract_fan_in():
    """The pipeline-owned Canvas expresses the DAG without a layer compiler."""
    definition = get_pipeline_definition("statistical_weights")

    canvas_graph = definition.build_canvas(pipeline_run_id=1)
    chord_task = canvas_graph.tasks[1]

    canvas_repr = repr(canvas_graph)
    assert chord_task.name == "celery.chord"
    assert [task.args[1] for task in chord_task.tasks] == [
        "extract_active_family_counts",
        "extract_aggregate_case_counts",
        "extract_stratum_case_counts",
    ]
    assert chord_task.body.immutable
    assert chord_task.body.args[1] == "run_weights_qa"
    downstream_chain = chord_task.body.options["link"][0]
    assert downstream_chain.immutable
    assert [task.args[1] for task in downstream_chain.tasks[:1]] == [
        "publish_weights",
    ]
    assert (
        downstream_chain.tasks[1].name == "tdpservice.etl.tasks.finalize_pipeline_run"
    )
    assert all(task.immutable for task in downstream_chain.tasks)
    assert definition.completion_keys == ("notify_weights_run",)
    assert "notify_weights_run" not in canvas_repr
    assert "validate_run_sources" in canvas_repr
    assert "extract_active_family_counts" in canvas_repr
    assert "extract_aggregate_case_counts" in canvas_repr
    assert "extract_stratum_case_counts" in canvas_repr
    assert "build_weight_candidates" not in canvas_repr
    assert "advance_pipeline_run" not in canvas_repr


def test_pipeline_nodes_create_registered_task_signatures():
    """Pipeline nodes expose their Celery task signatures directly."""
    definition = get_pipeline_definition("statistical_weights")

    node = definition.nodes["publish_weights"]
    signature = definition.nodes.publish_weights.task(pipeline_run_id=123)

    assert definition.nodes.publish_weights is node
    assert signature.name == "tdpservice.etl.tasks.run_pipeline_node"
    assert signature.args == (123, "publish_weights")


def test_pipeline_validation_rejects_duplicate_node_keys():
    """Pipeline node keys must be unique for ETLNodeRun lookup."""
    definition = _definition(
        [
            _node("extract"),
            _node("extract"),
        ]
    )

    with pytest.raises(PipelineValidationError):
        definition.validate()


def test_pipeline_node_exposes_configured_key():
    """Pipeline nodes expose their configured ETLNodeRun key."""
    node = _node("extract")

    assert node.key == "extract"


def test_pipeline_definition_requires_canvas_builder_implementation():
    """Pipeline definitions must implement executable Canvas declaration."""

    class MissingCanvasPipeline(PipelineDefinition):
        key = "missing_canvas"
        version = "1"
        display_name = "Missing Canvas"
        description = "Pipeline missing a Canvas implementation."
        allowed_parameters = {}
        nodes = PipelineNodeRegistry(())

        def validate_parameters(self, parameters: dict) -> dict:
            return {}

        def output_scope(self, parameters: dict) -> dict:
            return {}

    with pytest.raises(TypeError):
        MissingCanvasPipeline()


@pytest.mark.parametrize(
    "parameters,is_valid",
    [
        [[1, 2, 3], False],
        ["string", False],
        [1234, False],
        [("a", "b"), False],
        [{"fiscal_year": 2026, "program": Program.Code.TANF}, True],
    ],
)
def test_statistical_weights_parameters_validates_is_dict(parameters, is_valid):
    """Fiscal year input is normalized for output-scope idempotency."""
    definition = get_pipeline_definition("statistical_weights")

    if is_valid:
        assert definition.validate_parameters(parameters) == parameters
    else:
        with pytest.raises(PipelineValidationError):
            definition.validate_parameters(parameters)


def test_statistical_weights_parameters_normalize_fiscal_year():
    """Fiscal year input is normalized for output-scope idempotency."""
    definition = get_pipeline_definition("statistical_weights")

    assert definition.validate_parameters(
        {"fiscal_year": "2026", "program": Program.Code.TANF}
    ) == {
        "fiscal_year": 2026,
        "program": Program.Code.TANF,
    }


def test_validate_statistical_weights_parameters_rejects_program_alias():
    """Program input must use exact supported program codes."""
    definition = get_pipeline_definition("statistical_weights")

    with pytest.raises(PipelineValidationError):
        definition.validate_parameters({"fiscal_year": "2026", "program": "TANF"})


def test_validate_statistical_weights_parameters_rejects_unknown_program():
    """Only supported statistical weights programs are accepted."""
    definition = get_pipeline_definition("statistical_weights")

    with pytest.raises(PipelineValidationError):
        definition.validate_parameters({"fiscal_year": 2026, "program": "WPR"})


def test_validate_run_parameters_rejects_unknown_parameters():
    """Only code-defined pipeline parameters are accepted."""
    definition = get_pipeline_definition("statistical_weights")

    with pytest.raises(PipelineValidationError):
        definition.validate_parameters(
            {
                "fiscal_year": 2026,
                "program": Program.Code.TANF,
                "raw_sql": "select 1",
            }
        )


@pytest.mark.django_db
def test_active_run_scope_key_constraint_allows_completed_reruns():
    """The database rejects duplicate active scopes and allows completed reruns."""
    definition = get_pipeline_definition("statistical_weights")
    parameters = {"fiscal_year": 2026, "program": Program.Code.TANF}
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
    creator = PipelineRunFactory.for_pipeline_key("statistical_weights")
    first_run = creator.create(
        parameters={"fiscal_year": 2026, "program": Program.Code.TANF},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    with pytest.raises(ActivePipelineRunError):
        creator.create(
            parameters={"fiscal_year": 2026, "program": Program.Code.TANF},
            trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
        )

    first_run.status = ETLPipelineRun.Status.SUCCEEDED
    first_run.save(update_fields=["status", "updated_at"])
    second_run = creator.create(
        parameters={"fiscal_year": 2026, "program": Program.Code.TANF},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    assert second_run.output_scope_key == first_run.output_scope_key


@pytest.mark.django_db
def test_create_pipeline_run_scopes_active_runs_by_program():
    """Different programs can run concurrently for the same fiscal year."""
    creator = PipelineRunFactory.for_pipeline_key("statistical_weights")

    tanf_run = creator.create(
        parameters={"fiscal_year": 2026, "program": Program.Code.TANF},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )
    ssp_run = creator.create(
        parameters={"fiscal_year": 2026, "program": Program.Code.SSP},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    assert tanf_run.output_scope_key != ssp_run.output_scope_key
    assert tanf_run.output_scope["program"] == Program.Code.TANF
    assert ssp_run.output_scope["program"] == Program.Code.SSP


@pytest.mark.django_db
def test_run_pipeline_node_task_resolves_registered_node():
    """The Celery task resolves a node and delegates execution to the node."""
    calls = []

    def handler(context):
        calls.append(context.parameters["fiscal_year"])
        return NodeResult(output_row_count=1)

    definition = _definition([_node("extract", handler)])
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

    with patch("tdpservice.etl.tasks.get_pipeline_definition", return_value=definition):
        result = run_pipeline_node(pipeline_run.id, "extract")

    assert result == {
        "node_key": "extract",
        "status": ETLNodeRun.Status.SUCCEEDED,
    }
    assert calls == [2026]


@pytest.mark.django_db
def test_run_pipeline_node_ignores_already_succeeded_node():
    """Duplicate task delivery does not run a node handler twice."""
    calls = []

    def handler(context):
        calls.append(context.parameters["fiscal_year"])
        return NodeResult(output_row_count=1)

    definition = _definition([_node("extract", handler)])
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

    first_result = definition.nodes["extract"].run(pipeline_run)
    second_result = definition.nodes["extract"].run(pipeline_run)

    assert first_result == {
        "node_key": "extract",
        "status": ETLNodeRun.Status.SUCCEEDED,
    }
    assert second_result == {
        "node_key": "extract",
        "status": ETLNodeRun.Status.SUCCEEDED,
        "already_started": True,
    }
    assert calls == [2026]


@pytest.mark.django_db
def test_run_pipeline_node_fails_missing_input_contracts():
    """Nodes fail before their handlers when declared artifact inputs are missing."""
    pipeline_run = _create_pipeline_run()
    pipeline_run.node_runs.filter(
        node_key__in=[
            "validate_run_sources",
            "extract_active_family_counts",
            "extract_aggregate_case_counts",
            "extract_stratum_case_counts",
        ]
    ).update(status=ETLNodeRun.Status.SUCCEEDED)

    with pytest.raises(PipelineValidationError):
        get_pipeline_definition("statistical_weights").nodes.run_weights_qa.run(
            pipeline_run
        )

    node_run = pipeline_run.node_runs.get(node_key="run_weights_qa")
    pipeline_run.refresh_from_db()
    assert node_run.status == ETLNodeRun.Status.FAILED
    assert "Missing input contracts" in node_run.error_message
    assert pipeline_run.status == ETLPipelineRun.Status.FAILED


@pytest.mark.django_db
def test_run_pipeline_node_accepts_present_artifact_contract():
    """A declared artifact manifest satisfies a node input contract."""
    calls = []

    def handler(context):
        calls.append(sorted(context.artifacts))
        return NodeResult(output_row_count=1)

    definition = _definition(
        [_node("consume", handler, input_contracts=("artifact.input",))],
    )
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
    ETLNodeRun.objects.create(pipeline_run=pipeline_run, node_key="consume")
    ETLArtifact.objects.create(
        pipeline_run=pipeline_run,
        key="artifact.input",
        artifact_kind=ETLArtifact.ArtifactKind.DATASET,
        storage_kind=ETLArtifact.StorageKind.POSTGRES_TABLE,
        reference="example_table",
        schema_key="example.input",
        row_count=1,
    )

    result = definition.nodes["consume"].run(pipeline_run)

    assert result == {
        "node_key": "consume",
        "status": ETLNodeRun.Status.SUCCEEDED,
    }
    assert calls == [["artifact.input"]]


def test_pipeline_validation_rejects_unknown_completion_key():
    """Declared completion_keys must exist in the pipeline node registry."""
    definition = _definition(
        [_node("extract")],
        completion_keys=("missing_node",),
    )

    with pytest.raises(PipelineValidationError, match="Unknown completion node keys"):
        definition.validate()


def test_pipeline_validation_rejects_duplicate_completion_keys():
    """Declared completion_keys must be unique."""
    definition = _definition(
        [_node("extract"), _node("notify")],
        completion_keys=("notify", "notify"),
    )

    with pytest.raises(PipelineValidationError, match="unique"):
        definition.validate()


@pytest.mark.django_db
def test_finalize_persists_terminal_status_before_running_completion_nodes():
    """Completion nodes observe the persisted terminal pipeline status."""
    observed_statuses = []

    def notify(context):
        persisted = ETLPipelineRun.objects.get(id=context.pipeline_run.id)
        observed_statuses.append((persisted.status, persisted.finished_at is not None))
        return NodeResult(metadata={"notified": True})

    definition = _definition(
        [_node("extract"), _node("notify", notify)],
        completion_keys=("notify",),
    )
    pipeline_run = PipelineRunFactory(definition).create(
        parameters={"fiscal_year": 2026},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )
    pipeline_run.node_runs.filter(node_key="extract").update(
        status=ETLNodeRun.Status.SUCCEEDED
    )

    result = PipelineRunLauncher(
        pipeline_run=pipeline_run,
        definition=definition,
    ).finalize()

    pipeline_run.refresh_from_db()
    notify_run = pipeline_run.node_runs.get(node_key="notify")
    assert result["status"] == ETLPipelineRun.Status.SUCCEEDED
    assert observed_statuses == [(ETLPipelineRun.Status.SUCCEEDED, True)]
    assert pipeline_run.status == ETLPipelineRun.Status.SUCCEEDED
    assert notify_run.status == ETLNodeRun.Status.SUCCEEDED
    assert notify_run.metadata == {"notified": True}


@pytest.mark.django_db
def test_finalize_without_completion_keys_retains_existing_behavior():
    """Pipelines without completion_keys retain existing finalization behavior."""
    definition = _definition([_node("extract"), _node("load")])
    pipeline_run = PipelineRunFactory(definition).create(
        parameters={"fiscal_year": 2026},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )
    pipeline_run.node_runs.update(status=ETLNodeRun.Status.SUCCEEDED)

    result = PipelineRunLauncher(
        pipeline_run=pipeline_run,
        definition=definition,
    ).finalize()

    pipeline_run.refresh_from_db()
    assert result == {
        "pipeline_run_id": pipeline_run.id,
        "status": ETLPipelineRun.Status.SUCCEEDED,
    }
    assert pipeline_run.status == ETLPipelineRun.Status.SUCCEEDED
    assert pipeline_run.finished_at is not None


@pytest.mark.django_db
def test_completion_node_failure_does_not_overwrite_succeeded_pipeline():
    """A failing completion node records its own error without altering SUCCEEDED."""

    def broken_notify(context):
        raise RuntimeError("SMTP down")

    definition = _definition(
        [_node("extract"), _node("notify", broken_notify)],
        completion_keys=("notify",),
    )
    pipeline_run = PipelineRunFactory(definition).create(
        parameters={"fiscal_year": 2026},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )
    pipeline_run.node_runs.filter(node_key="extract").update(
        status=ETLNodeRun.Status.SUCCEEDED
    )

    result = PipelineRunLauncher(
        pipeline_run=pipeline_run,
        definition=definition,
    ).finalize()

    pipeline_run.refresh_from_db()
    notify_run = pipeline_run.node_runs.get(node_key="notify")
    assert result["status"] == ETLPipelineRun.Status.SUCCEEDED
    assert pipeline_run.status == ETLPipelineRun.Status.SUCCEEDED
    assert pipeline_run.error_message is None
    assert notify_run.status == ETLNodeRun.Status.FAILED
    assert notify_run.error_message == "SMTP down"


@pytest.mark.django_db
def test_completion_node_failure_does_not_overwrite_failed_pipeline_error():
    """A failing completion node preserves the original upstream failure error."""

    def broken_notify(context):
        raise RuntimeError("SMTP down")

    definition = _definition(
        [_node("extract"), _node("notify", broken_notify)],
        completion_keys=("notify",),
    )
    pipeline_run = PipelineRunFactory(definition).create(
        parameters={"fiscal_year": 2026},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )
    pipeline_run.status = ETLPipelineRun.Status.FAILED
    pipeline_run.error_message = "extract: source missing"
    pipeline_run.save(update_fields=["status", "error_message", "updated_at"])
    pipeline_run.node_runs.filter(node_key="extract").update(
        status=ETLNodeRun.Status.FAILED,
        error_message="source missing",
    )

    result = PipelineRunLauncher(
        pipeline_run=pipeline_run,
        definition=definition,
    ).finalize()

    pipeline_run.refresh_from_db()
    notify_run = pipeline_run.node_runs.get(node_key="notify")
    assert result["status"] == ETLPipelineRun.Status.FAILED
    assert pipeline_run.status == ETLPipelineRun.Status.FAILED
    assert pipeline_run.error_message == "extract: source missing"
    assert notify_run.status == ETLNodeRun.Status.FAILED
    assert notify_run.error_message == "SMTP down"


@pytest.mark.django_db
def test_launch_executes_completion_once_on_parallel_failures(settings):
    """Multiple parallel task failures trigger completion processing only once."""
    from celery import chain, chord

    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = False

    notify_calls = []

    def fail_first(context):
        raise RuntimeError("branch 1 failed")

    def fail_second(context):
        raise RuntimeError("branch 2 failed")

    def notify(context):
        persisted = ETLPipelineRun.objects.get(id=context.pipeline_run.id)
        notify_calls.append(persisted.status)
        return NodeResult(metadata={"status_seen": persisted.status})

    def build_parallel_canvas(defn, pipeline_run_id):
        return chain(
            defn.nodes.start.task(pipeline_run_id),
            chord(
                [
                    defn.nodes.branch_a.task(pipeline_run_id),
                    defn.nodes.branch_b.task(pipeline_run_id),
                ],
                finalize_pipeline_run.si(pipeline_run_id),
            ),
        )

    definition = _definition(
        [
            _node("start"),
            _node("branch_a", fail_first),
            _node("branch_b", fail_second),
            _node("notify", notify),
        ],
        completion_keys=("notify",),
        canvas_builder=build_parallel_canvas,
    )
    pipeline_run = PipelineRunFactory(definition).create(
        parameters={"fiscal_year": 2026},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    with patch("tdpservice.etl.tasks.get_pipeline_definition", return_value=definition):
        with patch("tdpservice.etl.runner.get_pipeline_definition", return_value=definition):
            with pytest.raises(RuntimeError):
                PipelineRunLauncher(
                    pipeline_run=pipeline_run,
                    definition=definition,
                ).launch()

            second_finalize = PipelineRunLauncher(
                pipeline_run=pipeline_run,
                definition=definition,
            ).finalize()

    pipeline_run.refresh_from_db()
    notify_run = pipeline_run.node_runs.get(node_key="notify")
    assert notify_calls == [ETLPipelineRun.Status.FAILED]
    assert second_finalize["already_finalized"] is True
    assert pipeline_run.status == ETLPipelineRun.Status.FAILED
    assert notify_run.status == ETLNodeRun.Status.SUCCEEDED
