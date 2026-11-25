"""ETL pipeline run creation and execution services."""

import hashlib
import json
import logging
from datetime import datetime, timedelta

from celery import chord
from django.db import IntegrityError, transaction
from django.utils import timezone

from tdpservice.etl.exceptions import ActivePipelineRunError
from tdpservice.etl.models import ETLNodeRun, ETLPipelineRun
from tdpservice.etl.pipelines.base import PipelineDefinition
from tdpservice.etl.registry import get_pipeline_definition

logger = logging.getLogger(__name__)

COMPLETION_CLAIM_TTL = timedelta(minutes=5)

ACTIVE_RUN_STATUSES = (
    ETLPipelineRun.Status.PENDING,
    ETLPipelineRun.Status.RUNNING,
)


class PipelineRunFactory:
    """Create pipeline run records from a code-owned pipeline definition."""

    def __init__(self, definition: PipelineDefinition):
        """Initialize a run creator for one pipeline definition."""
        self.definition = definition

    @classmethod
    def for_pipeline_key(cls, pipeline_key: str) -> "PipelineRunFactory":
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
        """Create a pipeline run and initial ETLNodeRun records."""
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


class PipelineRunLauncher:
    """Launch and finalize a persisted pipeline run."""

    def __init__(
        self,
        *,
        pipeline_run: ETLPipelineRun,
        definition: PipelineDefinition,
    ):
        """Initialize a launcher for one persisted pipeline run."""
        self.pipeline_run = pipeline_run
        self.definition = definition

    @classmethod
    def for_run_id(cls, pipeline_run_id: int) -> "PipelineRunLauncher":
        """Build a launcher for a persisted pipeline run."""
        pipeline_run = ETLPipelineRun.objects.get(id=pipeline_run_id)
        definition = get_pipeline_definition(pipeline_run.pipeline_key)
        definition.validate()
        return cls(pipeline_run=pipeline_run, definition=definition)

    def launch(self):
        """Queue the pipeline-owned Canvas for a pipeline run."""
        from tdpservice.etl.tasks import finalize_pipeline_run

        if self.pipeline_run.status == ETLPipelineRun.Status.PENDING:
            self.pipeline_run.status = ETLPipelineRun.Status.RUNNING
            self.pipeline_run.started_at = timezone.now()
            self.pipeline_run.save(update_fields=["status", "started_at", "updated_at"])

        pipeline_canvas = self.definition.build_canvas(self.pipeline_run.id)
        _attach_error_callback(
            pipeline_canvas,
            finalize_pipeline_run.si(self.pipeline_run.id),
        )
        return pipeline_canvas.apply_async()

    def finalize(self) -> dict:
        """Finalize a pipeline run and execute any declared completion nodes."""
        completion_keys = tuple(self.definition.completion_keys)
        if not self._claim_completion(completion_keys):
            return {
                "pipeline_run_id": self.pipeline_run.id,
                "status": self.pipeline_run.status,
                "already_finalized": True,
            }

        completion_results = self._run_completion_nodes()
        if completion_keys:
            self._mark_completion_completed(completion_keys)

        result = {
            "pipeline_run_id": self.pipeline_run.id,
            "status": self.pipeline_run.status,
        }
        if completion_results:
            result["completion_results"] = completion_results
        return result

    def _claim_completion(self, completion_keys: tuple[str, ...]) -> bool:
        """Acquire or recover the completion claim, returning True if caller should run."""
        now = timezone.now()
        terminal_statuses = (
            ETLNodeRun.Status.SUCCEEDED,
            ETLNodeRun.Status.FAILED,
        )
        with transaction.atomic():
            pipeline_run = ETLPipelineRun.objects.select_for_update().get(
                id=self.pipeline_run.id
            )
            metadata = dict(pipeline_run.metadata or {})
            if metadata.get("completion_completed_at"):
                self.pipeline_run = pipeline_run
                return False

            if metadata.get("completion_claimed_at"):
                return self._try_recover_claim(
                    pipeline_run, metadata, completion_keys, terminal_statuses, now
                )

            metadata["completion_claimed_at"] = now.isoformat()
            if not completion_keys:
                metadata["completion_completed_at"] = now.isoformat()
            pipeline_run.metadata = metadata
            self._apply_terminal_outcome(pipeline_run, completion_keys, now)
            self.pipeline_run = pipeline_run
            return True

    def _try_recover_claim(
        self,
        pipeline_run: ETLPipelineRun,
        metadata: dict,
        completion_keys: tuple[str, ...],
        terminal_statuses: tuple[str, ...],
        now: datetime,
    ) -> bool:
        """Recover an expired completion claim if incomplete completion nodes remain."""
        incomplete_nodes = pipeline_run.node_runs.filter(
            node_key__in=completion_keys
        ).exclude(status__in=terminal_statuses)
        if not incomplete_nodes.exists():
            metadata["completion_completed_at"] = now.isoformat()
            pipeline_run.metadata = metadata
            pipeline_run.save(update_fields=["metadata", "updated_at"])
            self.pipeline_run = pipeline_run
            return False

        if not _is_claim_stale(metadata.get("completion_claimed_at"), now):
            self.pipeline_run = pipeline_run
            return False

        incomplete_nodes.filter(status=ETLNodeRun.Status.RUNNING).update(
            status=ETLNodeRun.Status.PENDING
        )
        metadata["completion_claimed_at"] = now.isoformat()
        pipeline_run.metadata = metadata
        pipeline_run.save(update_fields=["metadata", "updated_at"])
        self.pipeline_run = pipeline_run
        return True

    @staticmethod
    def _apply_terminal_outcome(
        pipeline_run: ETLPipelineRun,
        completion_keys: tuple[str, ...],
        now: datetime,
    ) -> None:
        """Compute and persist the pipeline's terminal status from execution nodes."""
        execution_node_runs = pipeline_run.node_runs.exclude(
            node_key__in=set(completion_keys)
        )
        failed_node_runs = execution_node_runs.filter(
            status=ETLNodeRun.Status.FAILED
        )

        if failed_node_runs.exists():
            pipeline_run.status = ETLPipelineRun.Status.FAILED
            if not pipeline_run.error_message:
                first_failed = failed_node_runs.order_by("id").first()
                if first_failed and first_failed.error_message:
                    pipeline_run.error_message = (
                        f"{first_failed.node_key}: {first_failed.error_message}"
                    )
        elif execution_node_runs.exclude(status=ETLNodeRun.Status.SUCCEEDED).exists():
            pipeline_run.status = ETLPipelineRun.Status.FAILED
            if not pipeline_run.error_message:
                pipeline_run.error_message = (
                    "One or more ETLNodeRun records did not complete."
                )
        else:
            pipeline_run.status = ETLPipelineRun.Status.SUCCEEDED

        if pipeline_run.finished_at is None:
            pipeline_run.finished_at = now

        pipeline_run.save(
            update_fields=[
                "status",
                "finished_at",
                "error_message",
                "metadata",
                "updated_at",
            ]
        )

    def _mark_completion_completed(self, completion_keys: tuple[str, ...]) -> None:
        """Record completion finalization once all completion nodes are terminal."""
        terminal_statuses = (
            ETLNodeRun.Status.SUCCEEDED,
            ETLNodeRun.Status.FAILED,
        )
        with transaction.atomic():
            pipeline_run = ETLPipelineRun.objects.select_for_update().get(
                id=self.pipeline_run.id
            )
            has_incomplete = (
                pipeline_run.node_runs.filter(node_key__in=completion_keys)
                .exclude(status__in=terminal_statuses)
                .exists()
            )
            if has_incomplete:
                return
            metadata = dict(pipeline_run.metadata or {})
            if not metadata.get("completion_completed_at"):
                metadata["completion_completed_at"] = timezone.now().isoformat()
                pipeline_run.metadata = metadata
                pipeline_run.save(update_fields=["metadata", "updated_at"])
            self.pipeline_run = pipeline_run

    def _run_completion_nodes(self) -> list[dict]:
        """Execute declared completion nodes without altering pipeline outcome."""
        results = []
        for node_key in self.definition.completion_keys:
            node = self.definition.nodes[node_key]
            try:
                results.append(node.run(self.pipeline_run, is_completion=True))
            except Exception as exc:
                logger.exception(
                    "Completion node %s failed for pipeline run %s.",
                    node_key,
                    self.pipeline_run.id,
                )
                results.append(
                    {
                        "node_key": node_key,
                        "status": ETLNodeRun.Status.FAILED,
                        "error": str(exc),
                    }
                )
        return results


def _attach_error_callback(canvas_sig, error_sig) -> None:
    """Attach an error callback to every non-finalizer task in a Canvas."""
    if isinstance(canvas_sig, chord):
        for task in canvas_sig.tasks:
            _attach_error_callback(task, error_sig)
        if canvas_sig.body is not None:
            _attach_error_callback(canvas_sig.body, error_sig)
    elif hasattr(canvas_sig, "tasks"):
        for task in canvas_sig.tasks:
            _attach_error_callback(task, error_sig)
    elif getattr(canvas_sig, "task", None) != error_sig.task:
        existing_links = canvas_sig.options.get("link_error") or []
        if not any(
            getattr(link, "task", None) == error_sig.task for link in existing_links
        ):
            canvas_sig.link_error(error_sig.clone())

    for linked in canvas_sig.options.get("link") or ():
        _attach_error_callback(linked, error_sig)


def _is_claim_stale(claimed_at: str | None, now: datetime) -> bool:
    """Return True when an in-flight completion claim has expired."""
    if not claimed_at:
        return True
    try:
        claimed_dt = datetime.fromisoformat(claimed_at)
    except (TypeError, ValueError):
        return True
    if timezone.is_naive(claimed_dt):
        claimed_dt = timezone.make_aware(claimed_dt, timezone.get_current_timezone())
    return now - claimed_dt >= COMPLETION_CLAIM_TTL


def output_scope_key(output_scope: dict) -> str:
    """Return a stable hash key for an output scope."""
    canonical_scope = json.dumps(
        output_scope,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_scope.encode("utf-8")).hexdigest()
