"""Code-owned ETL pipeline registry."""

from dataclasses import dataclass, field
from typing import Any, Callable

from celery import chain, chord

from tdpservice.etl.exceptions import PipelineValidationError


@dataclass(frozen=True)
class NodeResult:
    """Structured result returned by a node implementation."""

    input_row_count: int | None = None
    output_row_count: int | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class PipelineNode:
    """Executable node registered for one ETL pipeline."""

    key: str
    implementation: Callable
    input_contracts: tuple[str, ...] = ()
    output_contracts: tuple[str, ...] = ()


@dataclass(frozen=True)
class PipelineDefinition:
    """Definition for one approved ETL pipeline."""

    key: str
    version: str
    display_name: str
    description: str
    nodes: tuple[PipelineNode, ...]
    allowed_parameters: dict
    canvas_builder: Callable[[int], Any] | None = None
    schedule: dict | None = None
    required_groups: tuple[str, ...] = ("OFA System Admin",)

    @property
    def node_map(self) -> dict[str, PipelineNode]:
        """Return nodes keyed by node key."""
        return {node.key: node for node in self.nodes}

    def output_scope(self, parameters: dict) -> dict:
        """Build the idempotency/output scope for the pipeline."""
        fiscal_year = int(parameters["fiscal_year"])
        return {
            "pipeline": self.key,
            "fiscal_year": fiscal_year,
            "program": "TANF",
            "section": "1",
        }

    def validate_parameters(self, parameters: dict) -> dict:
        """Validate and normalize run parameters for this pipeline."""
        normalized = dict(parameters or {})
        allowed = self.allowed_parameters

        for name, metadata in allowed.items():
            if metadata.get("required") and name not in normalized:
                raise PipelineValidationError(f"Missing required parameter: {name}")

        if "fiscal_year" in normalized:
            try:
                normalized["fiscal_year"] = int(normalized["fiscal_year"])
            except (TypeError, ValueError) as exc:
                raise PipelineValidationError(
                    "fiscal_year must be an integer."
                ) from exc

            if normalized["fiscal_year"] < 2000:
                raise PipelineValidationError("fiscal_year must be 2000 or later.")

        unexpected = set(normalized) - set(allowed)
        if unexpected:
            raise PipelineValidationError(
                f"Unexpected parameters: {sorted(unexpected)}"
            )

        return normalized

    def validate(self) -> None:
        """Validate node metadata for this pipeline."""
        node_keys = [node.key for node in self.nodes]
        if len(node_keys) != len(set(node_keys)):
            raise PipelineValidationError("Pipeline node keys must be unique.")

    def build_canvas(self, pipeline_run_id: int) -> Any:
        """Build the code-owned Celery Canvas for this pipeline run."""
        if self.canvas_builder is None:
            raise PipelineValidationError(
                f"Pipeline {self.key} does not define an executable Celery Canvas."
            )
        return self.canvas_builder(pipeline_run_id)

    def serialize(self) -> dict:
        """Return API-safe pipeline definition metadata."""
        return {
            "key": self.key,
            "version": self.version,
            "display_name": self.display_name,
            "description": self.description,
            "allowed_parameters": self.allowed_parameters,
            "schedule": self.schedule,
            "nodes": [
                {
                    "key": node.key,
                    "input_contracts": list(node.input_contracts),
                    "output_contracts": list(node.output_contracts),
                }
                for node in self.nodes
            ],
        }


def _statistical_weights_pipeline() -> PipelineDefinition:
    """Build the TANF statistical weights pipeline definition."""
    from tdpservice.etl.nodes import statistical_weights

    def build_canvas(pipeline_run_id: int) -> Any:
        from tdpservice.etl.tasks import execute_node, finalize_pipeline_run

        build_weight_candidates = execute_node.si(
            pipeline_run_id,
            "build_weight_candidates",
        )
        downstream = chain(
            execute_node.si(pipeline_run_id, "run_weights_qa"),
            execute_node.si(pipeline_run_id, "publish_weights"),
            execute_node.si(pipeline_run_id, "notify_weights_run"),
            finalize_pipeline_run.si(pipeline_run_id),
        )
        downstream.set(immutable=True)
        build_weight_candidates.link(downstream)

        return chain(
            execute_node.si(pipeline_run_id, "validate_parameters"),
            chord(
                [
                    execute_node.si(pipeline_run_id, "extract_t1_family_counts"),
                    execute_node.si(pipeline_run_id, "extract_t6_case_counts"),
                    execute_node.si(
                        pipeline_run_id,
                        "extract_t7_section_case_counts",
                    ),
                ],
                build_weight_candidates,
            ),
        )

    return PipelineDefinition(
        key="tanf_statistical_weights",
        version="1",
        display_name="TANF Statistical Weights",
        description="Generate TANF Section 1 statistical weights for a fiscal year.",
        allowed_parameters={
            "fiscal_year": {
                "type": "integer",
                "required": True,
                "description": "Fiscal year to generate weights for.",
            }
        },
        canvas_builder=build_canvas,
        schedule={"first_workday_monthly": True},
        nodes=(
            PipelineNode(
                key="validate_parameters",
                implementation=statistical_weights.validate_parameters,
            ),
            PipelineNode(
                key="extract_t1_family_counts",
                implementation=statistical_weights.extract_t1_family_counts,
                output_contracts=("weights.s1",),
            ),
            PipelineNode(
                key="extract_t6_case_counts",
                implementation=statistical_weights.extract_t6_case_counts,
                output_contracts=("weights.s3",),
            ),
            PipelineNode(
                key="extract_t7_section_case_counts",
                implementation=statistical_weights.extract_t7_section_case_counts,
                output_contracts=("weights.s4",),
            ),
            PipelineNode(
                key="build_weight_candidates",
                implementation=statistical_weights.build_weight_candidates,
                input_contracts=("weights.s1", "weights.s3", "weights.s4"),
                output_contracts=("statistical_weights.candidates",),
            ),
            PipelineNode(
                key="run_weights_qa",
                implementation=statistical_weights.run_weights_qa,
                input_contracts=(
                    "weights.s1",
                    "weights.s3",
                    "weights.s4",
                    "statistical_weights.candidates",
                ),
            ),
            PipelineNode(
                key="publish_weights",
                implementation=statistical_weights.publish_weights,
                input_contracts=("statistical_weights.candidates",),
                output_contracts=("statistical_weights",),
            ),
            PipelineNode(
                key="notify_weights_run",
                implementation=statistical_weights.notify_weights_run,
                input_contracts=("statistical_weights",),
            ),
        ),
    )


PIPELINE_REGISTRY = {
    "tanf_statistical_weights": _statistical_weights_pipeline,
}


def list_pipeline_definitions() -> list[PipelineDefinition]:
    """Return all approved pipeline definitions."""
    return [factory() for factory in PIPELINE_REGISTRY.values()]


def get_pipeline_definition(pipeline_key: str) -> PipelineDefinition:
    """Return one approved pipeline definition."""
    try:
        return PIPELINE_REGISTRY[pipeline_key]()
    except KeyError as exc:
        raise KeyError(f"Unknown ETL pipeline: {pipeline_key}") from exc
