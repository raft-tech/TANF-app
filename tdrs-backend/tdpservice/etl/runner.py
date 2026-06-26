"""ETL pipeline runner and Celery layer scheduler."""

import hashlib
import json
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.utils import timezone

from tdpservice.etl.exceptions import ActivePipelineRunError, PipelineValidationError
from tdpservice.etl.models import (
    ETLIntermediateOutput,
    ETLNodeRun,
    ETLOutput,
    ETLPipelineRun,
)
from tdpservice.etl.registry import (
    NodeDefinition,
    NodeResult,
    PipelineDefinition,
    get_pipeline_definition,
)

ACTIVE_RUN_STATUSES = (
    ETLPipelineRun.Status.PENDING,
    ETLPipelineRun.Status.RUNNING,
)


@dataclass(frozen=True)
class NodeContext:
    """Execution context passed to a node implementation."""

    pipeline_run: ETLPipelineRun
    node: NodeDefinition
    upstream_outputs: dict[str, ETLOutput]
    intermediate_outputs: dict[str, ETLIntermediateOutput]

    @property
    def parameters(self) -> dict:
        """Return run parameters."""
        return self.pipeline_run.parameters

    @property
    def output_scope(self) -> dict:
        """Return run output scope."""
        return self.pipeline_run.output_scope


class PipelineRunCreator:
    """Create pipeline run records from a code-owned pipeline definition."""

    def __init__(self, definition: PipelineDefinition):
        """Initialize a run creator for one pipeline definition."""
        self.definition = definition

    @classmethod
    def for_pipeline_key(cls, pipeline_key: str) -> "PipelineRunCreator":
        """Build a creator for an approved pipeline key."""
        return cls(get_pipeline_definition(pipeline_key))

    def create(
        self,
        *,
        parameters: dict,
        trigger_source: str,
        triggered_by=None,
        retry_of: ETLPipelineRun | None = None,
    ) -> ETLPipelineRun:
        """Create a pipeline run and initial node run records."""
        self.definition.validate()
        normalized_parameters = self.definition.validate_parameters(parameters)
        output_scope = self.definition.output_scope(normalized_parameters)
        scope_key = output_scope_key(output_scope)

        try:
            with transaction.atomic():
                active_run = (
                    ETLPipelineRun.objects.select_for_update()
                    .filter(
                        pipeline_key=self.definition.key,
                        output_scope_key=scope_key,
                        status__in=ACTIVE_RUN_STATUSES,
                    )
                    .first()
                )
                if active_run:
                    raise ActivePipelineRunError(
                        f"Run {active_run.id} is already active for this output scope."
                    )

                pipeline_run = ETLPipelineRun.objects.create(
                    pipeline_key=self.definition.key,
                    pipeline_version=self.definition.version,
                    status=ETLPipelineRun.Status.PENDING,
                    parameters=normalized_parameters,
                    output_scope=output_scope,
                    output_scope_key=scope_key,
                    trigger_source=trigger_source,
                    triggered_by=triggered_by,
                    retry_of=retry_of,
                )
                ETLNodeRun.objects.bulk_create(
                    [
                        ETLNodeRun(pipeline_run=pipeline_run, node_key=node.key)
                        for node in self.definition.nodes
                    ]
                )
        except IntegrityError as exc:
            active_run = (
                ETLPipelineRun.objects.filter(
                    pipeline_key=self.definition.key,
                    output_scope_key=scope_key,
                    status__in=ACTIVE_RUN_STATUSES,
                )
                .order_by("id")
                .first()
            )
            if active_run:
                raise ActivePipelineRunError(
                    f"Run {active_run.id} is already active for this output scope."
                ) from exc
            raise

        return pipeline_run


class PipelineRunScheduler:
    """Launch, advance, and finalize a persisted pipeline run."""

    def __init__(
        self,
        *,
        pipeline_run: ETLPipelineRun,
        definition: PipelineDefinition,
    ):
        """Initialize a scheduler for one persisted pipeline run."""
        self.pipeline_run = pipeline_run
        self.definition = definition

    @classmethod
    def for_run_id(cls, pipeline_run_id: int) -> "PipelineRunScheduler":
        """Build a scheduler for a persisted pipeline run."""
        pipeline_run = ETLPipelineRun.objects.get(id=pipeline_run_id)
        definition = get_pipeline_definition(pipeline_run.pipeline_key)
        definition.validate()
        return cls(pipeline_run=pipeline_run, definition=definition)

    def launch(self):
        """Queue the first executable layer for a pipeline run."""
        if self.pipeline_run.status == ETLPipelineRun.Status.PENDING:
            self.pipeline_run.status = ETLPipelineRun.Status.RUNNING
            self.pipeline_run.started_at = timezone.now()
            self.pipeline_run.save(update_fields=["status", "started_at", "updated_at"])

        layer_canvas = self.definition.build_layer_canvas(self.pipeline_run.id, 0)
        return layer_canvas.apply_async()

    def advance(self, layer_index: int) -> dict:
        """Queue the next pipeline layer after the previous layer succeeds."""
        layers = self.definition.topological_layers()

        if self.pipeline_run.status in (
            ETLPipelineRun.Status.FAILED,
            ETLPipelineRun.Status.CANCELED,
        ):
            return {
                "pipeline_run_id": self.pipeline_run.id,
                "status": self.pipeline_run.status,
            }

        previous_node_keys = [
            node_key
            for previous_layer in layers[:layer_index]
            for node_key in previous_layer
        ]
        previous_statuses = self._node_statuses(previous_node_keys)
        if any(
            status == ETLNodeRun.Status.FAILED for status in previous_statuses.values()
        ):
            return self.finalize()
        if any(
            previous_statuses.get(node_key) != ETLNodeRun.Status.SUCCEEDED
            for node_key in previous_node_keys
        ):
            return {
                "pipeline_run_id": self.pipeline_run.id,
                "layer_index": layer_index,
                "status": "waiting_on_dependencies",
                "dependency_status": previous_statuses,
            }

        if layer_index >= len(layers):
            return self.finalize()

        layer = layers[layer_index]
        statuses = self._node_statuses(layer)

        if any(status == ETLNodeRun.Status.FAILED for status in statuses.values()):
            return self.finalize()

        if all(status == ETLNodeRun.Status.SUCCEEDED for status in statuses.values()):
            return self.advance(layer_index + 1)

        if any(status != ETLNodeRun.Status.PENDING for status in statuses.values()):
            return {
                "pipeline_run_id": self.pipeline_run.id,
                "layer_index": layer_index,
                "status": "already_started",
                "node_statuses": statuses,
            }

        layer_canvas = self.definition.build_layer_canvas(
            self.pipeline_run.id,
            layer_index,
        )
        result = layer_canvas.apply_async()
        return {
            "pipeline_run_id": self.pipeline_run.id,
            "layer_index": layer_index,
            "task_id": result.id,
        }

    def finalize(self) -> dict:
        """Finalize a pipeline run after its generated Canvas graph completes."""
        node_runs = self.pipeline_run.node_runs.all()

        if node_runs.filter(status=ETLNodeRun.Status.FAILED).exists():
            self.pipeline_run.status = ETLPipelineRun.Status.FAILED
        elif node_runs.exclude(status=ETLNodeRun.Status.SUCCEEDED).exists():
            self.pipeline_run.status = ETLPipelineRun.Status.FAILED
            self.pipeline_run.error_message = "One or more nodes did not complete."
        else:
            self.pipeline_run.status = ETLPipelineRun.Status.SUCCEEDED

        self.pipeline_run.finished_at = timezone.now()
        self.pipeline_run.save(
            update_fields=["status", "finished_at", "error_message", "updated_at"]
        )
        return {
            "pipeline_run_id": self.pipeline_run.id,
            "status": self.pipeline_run.status,
        }

    def _node_statuses(self, node_keys: list[str]) -> dict:
        """Return statuses for node keys in this pipeline run."""
        return dict(
            ETLNodeRun.objects.filter(
                pipeline_run=self.pipeline_run,
                node_key__in=node_keys,
            ).values_list("node_key", "status")
        )


class NodeExecutor:
    """Execute one pipeline node and persist its node-run state."""

    def __init__(
        self,
        *,
        pipeline_run: ETLPipelineRun,
        definition: PipelineDefinition,
        node_key: str,
    ):
        """Initialize an executor for one pipeline node run."""
        self.pipeline_run = pipeline_run
        self.definition = definition
        self.node_key = node_key

    @classmethod
    def for_run_id(cls, pipeline_run_id: int, node_key: str) -> "NodeExecutor":
        """Build an executor for one persisted pipeline node run."""
        pipeline_run = ETLPipelineRun.objects.get(id=pipeline_run_id)
        definition = get_pipeline_definition(pipeline_run.pipeline_key)
        return cls(
            pipeline_run=pipeline_run,
            definition=definition,
            node_key=node_key,
        )

    @property
    def node(self) -> NodeDefinition:
        """Return this executor's node definition."""
        return self.definition.node_map[self.node_key]

    def execute(self) -> dict:
        """Execute one node and update its run record."""
        node_run = None

        try:
            with transaction.atomic():
                node_run = ETLNodeRun.objects.select_for_update().get(
                    pipeline_run=self.pipeline_run,
                    node_key=self.node_key,
                )
                start_result = self._start_node_run(node_run)
                if start_result:
                    return start_result

            context = self._build_context()
            result = self.node.implementation(context)
            if result is None:
                result = NodeResult()

            self._mark_succeeded(node_run, result)
            return {"node_key": self.node_key, "status": node_run.status}
        except Exception as exc:
            self._mark_failed(node_run, exc)
            raise

    def _start_node_run(self, node_run: ETLNodeRun) -> dict | None:
        """Claim a pending node run or return its existing terminal state."""
        if node_run.status in (
            ETLNodeRun.Status.RUNNING,
            ETLNodeRun.Status.SUCCEEDED,
        ):
            return {
                "node_key": self.node_key,
                "status": node_run.status,
                "already_started": True,
            }
        if node_run.status in (
            ETLNodeRun.Status.FAILED,
            ETLNodeRun.Status.SKIPPED,
        ):
            return {
                "node_key": self.node_key,
                "status": node_run.status,
                "already_completed": True,
            }

        dependency_status = self._dependency_status()
        dependency_failed = any(
            status != ETLNodeRun.Status.SUCCEEDED
            for status in dependency_status.values()
        )
        if dependency_failed:
            node_run.status = ETLNodeRun.Status.SKIPPED
            node_run.dependency_status = dependency_status
            node_run.finished_at = timezone.now()
            node_run.error_message = "One or more dependencies did not succeed."
            node_run.save(
                update_fields=[
                    "status",
                    "dependency_status",
                    "finished_at",
                    "error_message",
                ]
            )
            return {"node_key": self.node_key, "status": node_run.status}

        now = timezone.now()
        if self.pipeline_run.status == ETLPipelineRun.Status.PENDING:
            self.pipeline_run.status = ETLPipelineRun.Status.RUNNING
            self.pipeline_run.started_at = now
            self.pipeline_run.save(update_fields=["status", "started_at", "updated_at"])

        node_run.status = ETLNodeRun.Status.RUNNING
        node_run.dependency_status = dependency_status
        node_run.started_at = now
        node_run.error_message = None
        node_run.save(
            update_fields=[
                "status",
                "dependency_status",
                "started_at",
                "error_message",
            ]
        )
        return None

    def _dependency_status(self) -> dict:
        """Return dependency statuses for this node run."""
        if not self.node.depends_on:
            return {}

        node_runs = ETLNodeRun.objects.filter(
            pipeline_run=self.pipeline_run,
            node_key__in=self.node.depends_on,
        )
        return {node_run.node_key: node_run.status for node_run in node_runs}

    def _build_context(self) -> NodeContext:
        """Build a validated node context from persisted upstream artifacts."""
        upstream_outputs = self._upstream_outputs()
        intermediate_outputs = self._intermediate_outputs()
        available_contracts = set(upstream_outputs) | set(intermediate_outputs)
        missing_contracts = set(self.node.input_contracts) - available_contracts
        if missing_contracts:
            raise PipelineValidationError(
                "Missing input contracts for "
                f"{self.node_key}: {sorted(missing_contracts)}"
            )

        return NodeContext(
            pipeline_run=self.pipeline_run,
            node=self.node,
            upstream_outputs=upstream_outputs,
            intermediate_outputs=intermediate_outputs,
        )

    def _upstream_outputs(self) -> dict[str, ETLOutput]:
        """Return published outputs already produced by this run."""
        return {
            output.output_key: output
            for output in self.pipeline_run.outputs.filter(published=True).order_by(
                "id"
            )
        }

    def _intermediate_outputs(self) -> dict[str, ETLIntermediateOutput]:
        """Return intermediate outputs already produced by this run."""
        return {
            output.output_key: output
            for output in self.pipeline_run.intermediate_outputs.all().order_by("id")
        }

    def _mark_succeeded(
        self,
        node_run: ETLNodeRun,
        result: NodeResult,
    ) -> None:
        """Persist a successful node result."""
        node_run.status = ETLNodeRun.Status.SUCCEEDED
        node_run.finished_at = timezone.now()
        node_run.input_row_count = result.input_row_count
        node_run.output_row_count = result.output_row_count
        node_run.metadata = result.metadata
        node_run.save(
            update_fields=[
                "status",
                "finished_at",
                "input_row_count",
                "output_row_count",
                "metadata",
            ]
        )

    def _mark_failed(
        self,
        node_run: ETLNodeRun | None,
        exc: Exception,
    ) -> None:
        """Persist node and pipeline failure state."""
        if node_run is not None:
            node_run.status = ETLNodeRun.Status.FAILED
            node_run.finished_at = timezone.now()
            node_run.error_message = str(exc)
            node_run.save(update_fields=["status", "finished_at", "error_message"])

        self.pipeline_run.status = ETLPipelineRun.Status.FAILED
        self.pipeline_run.finished_at = timezone.now()
        self.pipeline_run.error_message = f"{self.node_key}: {exc}"
        self.pipeline_run.save(
            update_fields=["status", "finished_at", "error_message", "updated_at"]
        )


def output_scope_key(output_scope: dict) -> str:
    """Return a stable hash key for an output scope."""
    canonical_scope = json.dumps(
        output_scope,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_scope.encode("utf-8")).hexdigest()
