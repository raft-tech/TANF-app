"""ETL pipeline runner and Celery layer scheduler."""

import hashlib
import json
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.utils import timezone

from celery import chain, chord, group

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


class PipelineValidationError(ValueError):
    """Raised when a pipeline definition or run request is invalid."""


class ActivePipelineRunError(ValueError):
    """Raised when another active run exists for the same output scope."""


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


def output_scope_key(output_scope: dict) -> str:
    """Return a stable hash key for an output scope."""
    canonical_scope = json.dumps(
        output_scope,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_scope.encode("utf-8")).hexdigest()


def validate_pipeline_definition(definition: PipelineDefinition) -> None:
    """Validate node references and cycles for a pipeline definition."""
    node_keys = [node.key for node in definition.nodes]
    if len(node_keys) != len(set(node_keys)):
        raise PipelineValidationError("Pipeline node keys must be unique.")

    known_keys = set(node_keys)
    for node in definition.nodes:
        missing = set(node.depends_on) - known_keys
        if missing:
            raise PipelineValidationError(
                f"Node {node.key} depends on unknown nodes: {sorted(missing)}"
            )

    topological_layers(definition)


def topological_layers(definition: PipelineDefinition) -> list[list[str]]:
    """Return node keys in dependency layers."""
    remaining = {node.key: set(node.depends_on) for node in definition.nodes}
    node_order = [node.key for node in definition.nodes]
    completed: set[str] = set()
    layers: list[list[str]] = []

    while remaining:
        ready = [
            node_key
            for node_key in node_order
            if node_key in remaining and remaining[node_key].issubset(completed)
        ]
        if not ready:
            cycle_nodes = sorted(remaining.keys())
            raise PipelineValidationError(
                f"Pipeline contains a dependency cycle involving: {cycle_nodes}"
            )

        layers.append(ready)
        completed.update(ready)
        for node_key in ready:
            remaining.pop(node_key)

    return layers


def build_layer_canvas(
    definition: PipelineDefinition,
    pipeline_run_id: int,
    layer_index: int,
):
    """Build Celery Canvas primitives for one pipeline layer."""
    from tdpservice.etl.tasks import advance_pipeline_run, execute_node

    layers = topological_layers(definition)
    layer = layers[layer_index]
    next_layer = advance_pipeline_run.si(pipeline_run_id, layer_index + 1)

    if len(layer) == 1:
        return chain(execute_node.si(pipeline_run_id, layer[0]), next_layer)

    return chord(
        group([execute_node.si(pipeline_run_id, node_key) for node_key in layer]),
        next_layer,
    )


def build_canvas(definition: PipelineDefinition, pipeline_run_id: int):
    """Build the first layer's Celery Canvas for compatibility."""
    return build_layer_canvas(definition, pipeline_run_id, 0)


def validate_run_parameters(definition: PipelineDefinition, parameters: dict) -> dict:
    """Validate and normalize pipeline parameters."""
    normalized = dict(parameters or {})
    allowed = definition.allowed_parameters

    for name, metadata in allowed.items():
        if metadata.get("required") and name not in normalized:
            raise PipelineValidationError(f"Missing required parameter: {name}")

    if "fiscal_year" in normalized:
        try:
            normalized["fiscal_year"] = int(normalized["fiscal_year"])
        except (TypeError, ValueError) as exc:
            raise PipelineValidationError("fiscal_year must be an integer.") from exc

        if normalized["fiscal_year"] < 2000:
            raise PipelineValidationError("fiscal_year must be 2000 or later.")

    unexpected = set(normalized) - set(allowed)
    if unexpected:
        raise PipelineValidationError(f"Unexpected parameters: {sorted(unexpected)}")

    return normalized


def create_pipeline_run(
    *,
    pipeline_key: str,
    parameters: dict,
    trigger_source: str,
    triggered_by=None,
    retry_of: ETLPipelineRun | None = None,
) -> ETLPipelineRun:
    """Create a pipeline run and initial node run records."""
    definition = get_pipeline_definition(pipeline_key)
    validate_pipeline_definition(definition)
    normalized_parameters = validate_run_parameters(definition, parameters)
    output_scope = definition.output_scope(normalized_parameters)
    scope_key = output_scope_key(output_scope)

    try:
        with transaction.atomic():
            active_run = (
                ETLPipelineRun.objects.select_for_update()
                .filter(
                    pipeline_key=definition.key,
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
                pipeline_key=definition.key,
                pipeline_version=definition.version,
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
                    for node in definition.nodes
                ]
            )
    except IntegrityError as exc:
        active_run = (
            ETLPipelineRun.objects.filter(
                pipeline_key=definition.key,
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


def launch_pipeline_run(pipeline_run_id: int):
    """Queue the first executable layer for a pipeline run."""
    pipeline_run = ETLPipelineRun.objects.get(id=pipeline_run_id)
    definition = get_pipeline_definition(pipeline_run.pipeline_key)
    validate_pipeline_definition(definition)

    if pipeline_run.status == ETLPipelineRun.Status.PENDING:
        pipeline_run.status = ETLPipelineRun.Status.RUNNING
        pipeline_run.started_at = timezone.now()
        pipeline_run.save(update_fields=["status", "started_at", "updated_at"])

    layer_canvas = build_layer_canvas(definition, pipeline_run_id, 0)
    return layer_canvas.apply_async()


def advance_pipeline_run(pipeline_run_id: int, layer_index: int) -> dict:
    """Queue the next pipeline layer after the previous layer succeeds."""
    pipeline_run = ETLPipelineRun.objects.get(id=pipeline_run_id)
    definition = get_pipeline_definition(pipeline_run.pipeline_key)
    validate_pipeline_definition(definition)
    layers = topological_layers(definition)

    if pipeline_run.status in (
        ETLPipelineRun.Status.FAILED,
        ETLPipelineRun.Status.CANCELED,
    ):
        return {"pipeline_run_id": pipeline_run.id, "status": pipeline_run.status}

    previous_layers = layers[:layer_index]
    previous_node_keys = [
        node_key for previous_layer in previous_layers for node_key in previous_layer
    ]
    previous_statuses = dict(
        ETLNodeRun.objects.filter(
            pipeline_run=pipeline_run,
            node_key__in=previous_node_keys,
        ).values_list("node_key", "status")
    )
    if any(status == ETLNodeRun.Status.FAILED for status in previous_statuses.values()):
        return finalize_pipeline_run(pipeline_run_id)
    if any(
        previous_statuses.get(node_key) != ETLNodeRun.Status.SUCCEEDED
        for node_key in previous_node_keys
    ):
        return {
            "pipeline_run_id": pipeline_run.id,
            "layer_index": layer_index,
            "status": "waiting_on_dependencies",
            "dependency_status": previous_statuses,
        }

    if layer_index >= len(layers):
        return finalize_pipeline_run(pipeline_run_id)

    layer = layers[layer_index]
    node_runs = ETLNodeRun.objects.filter(
        pipeline_run=pipeline_run,
        node_key__in=layer,
    )
    statuses = {node_run.node_key: node_run.status for node_run in node_runs}

    if any(status == ETLNodeRun.Status.FAILED for status in statuses.values()):
        return finalize_pipeline_run(pipeline_run_id)

    if all(status == ETLNodeRun.Status.SUCCEEDED for status in statuses.values()):
        return advance_pipeline_run(pipeline_run_id, layer_index + 1)

    if any(status != ETLNodeRun.Status.PENDING for status in statuses.values()):
        return {
            "pipeline_run_id": pipeline_run.id,
            "layer_index": layer_index,
            "status": "already_started",
            "node_statuses": statuses,
        }

    layer_canvas = build_layer_canvas(definition, pipeline_run_id, layer_index)
    result = layer_canvas.apply_async()
    return {
        "pipeline_run_id": pipeline_run.id,
        "layer_index": layer_index,
        "task_id": result.id,
    }


def _dependency_status(pipeline_run: ETLPipelineRun, node: NodeDefinition) -> dict:
    """Return dependency statuses for a node run."""
    if not node.depends_on:
        return {}

    node_runs = ETLNodeRun.objects.filter(
        pipeline_run=pipeline_run, node_key__in=node.depends_on
    )
    return {node_run.node_key: node_run.status for node_run in node_runs}


def _upstream_outputs(pipeline_run: ETLPipelineRun) -> dict[str, ETLOutput]:
    """Return published outputs already produced by this run."""
    return {
        output.output_key: output
        for output in pipeline_run.outputs.filter(published=True).order_by("id")
    }


def _intermediate_outputs(
    pipeline_run: ETLPipelineRun,
) -> dict[str, ETLIntermediateOutput]:
    """Return intermediate outputs already produced by this run."""
    return {
        output.output_key: output
        for output in pipeline_run.intermediate_outputs.all().order_by("id")
    }


def execute_node(pipeline_run_id: int, node_key: str) -> dict:
    """Execute one node and update its run record."""
    pipeline_run = ETLPipelineRun.objects.get(id=pipeline_run_id)
    definition = get_pipeline_definition(pipeline_run.pipeline_key)
    node = definition.node_map[node_key]
    node_run = None

    try:
        with transaction.atomic():
            node_run = ETLNodeRun.objects.select_for_update().get(
                pipeline_run=pipeline_run,
                node_key=node_key,
            )
            if node_run.status in (
                ETLNodeRun.Status.RUNNING,
                ETLNodeRun.Status.SUCCEEDED,
            ):
                return {
                    "node_key": node_key,
                    "status": node_run.status,
                    "already_started": True,
                }
            if node_run.status in (
                ETLNodeRun.Status.FAILED,
                ETLNodeRun.Status.SKIPPED,
            ):
                return {
                    "node_key": node_key,
                    "status": node_run.status,
                    "already_completed": True,
                }

            dependency_status = _dependency_status(pipeline_run, node)
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
                return {"node_key": node_key, "status": node_run.status}

            now = timezone.now()
            if pipeline_run.status == ETLPipelineRun.Status.PENDING:
                pipeline_run.status = ETLPipelineRun.Status.RUNNING
                pipeline_run.started_at = now
                pipeline_run.save(update_fields=["status", "started_at", "updated_at"])

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

        upstream_outputs = _upstream_outputs(pipeline_run)
        intermediate_outputs = _intermediate_outputs(pipeline_run)
        available_contracts = set(upstream_outputs) | set(intermediate_outputs)
        missing_contracts = set(node.input_contracts) - available_contracts
        if missing_contracts:
            raise PipelineValidationError(
                f"Missing input contracts for {node_key}: {sorted(missing_contracts)}"
            )

        context = NodeContext(
            pipeline_run=pipeline_run,
            node=node,
            upstream_outputs=upstream_outputs,
            intermediate_outputs=intermediate_outputs,
        )
        result = node.implementation(context)
        if result is None:
            result = NodeResult()

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
        return {"node_key": node_key, "status": node_run.status}
    except Exception as exc:
        if node_run is not None:
            node_run.status = ETLNodeRun.Status.FAILED
            node_run.finished_at = timezone.now()
            node_run.error_message = str(exc)
            node_run.save(update_fields=["status", "finished_at", "error_message"])

        pipeline_run.status = ETLPipelineRun.Status.FAILED
        pipeline_run.finished_at = timezone.now()
        pipeline_run.error_message = f"{node_key}: {exc}"
        pipeline_run.save(
            update_fields=["status", "finished_at", "error_message", "updated_at"]
        )
        raise


def finalize_pipeline_run(pipeline_run_id: int) -> dict:
    """Finalize a pipeline run after its generated Canvas graph completes."""
    pipeline_run = ETLPipelineRun.objects.get(id=pipeline_run_id)
    node_runs = pipeline_run.node_runs.all()

    if node_runs.filter(status=ETLNodeRun.Status.FAILED).exists():
        pipeline_run.status = ETLPipelineRun.Status.FAILED
    elif node_runs.exclude(status=ETLNodeRun.Status.SUCCEEDED).exists():
        pipeline_run.status = ETLPipelineRun.Status.FAILED
        pipeline_run.error_message = "One or more nodes did not complete."
    else:
        pipeline_run.status = ETLPipelineRun.Status.SUCCEEDED

    pipeline_run.finished_at = timezone.now()
    pipeline_run.save(
        update_fields=["status", "finished_at", "error_message", "updated_at"]
    )
    return {"pipeline_run_id": pipeline_run.id, "status": pipeline_run.status}
