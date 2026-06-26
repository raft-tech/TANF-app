"""Code-owned ETL pipeline registry."""

from dataclasses import dataclass, field
from typing import Callable

from celery import chain, chord, group

from tdpservice.etl.exceptions import PipelineValidationError


@dataclass(frozen=True)
class NodeResult:
    """Structured result returned by a node implementation."""

    input_row_count: int | None = None
    output_row_count: int | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class NodeDefinition:
    """Definition for one ETL pipeline node."""

    key: str
    depends_on: tuple[str, ...]
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
    nodes: tuple[NodeDefinition, ...]
    allowed_parameters: dict
    schedule: dict | None = None
    required_groups: tuple[str, ...] = ("OFA System Admin",)

    @property
    def node_map(self) -> dict[str, NodeDefinition]:
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
        """Validate node references and cycles for this pipeline."""
        node_keys = [node.key for node in self.nodes]
        if len(node_keys) != len(set(node_keys)):
            raise PipelineValidationError("Pipeline node keys must be unique.")

        known_keys = set(node_keys)
        for node in self.nodes:
            missing = set(node.depends_on) - known_keys
            if missing:
                raise PipelineValidationError(
                    f"Node {node.key} depends on unknown nodes: {sorted(missing)}"
                )

        self.topological_layers()

    def topological_layers(self) -> list[list[str]]:
        """Return node keys in dependency layers."""
        remaining = {node.key: set(node.depends_on) for node in self.nodes}
        node_order = [node.key for node in self.nodes]
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
                    "Pipeline contains a dependency cycle involving: " f"{cycle_nodes}"
                )

            layers.append(ready)
            completed.update(ready)
            for node_key in ready:
                remaining.pop(node_key)

        return layers

    def build_layer_canvas(self, pipeline_run_id: int, layer_index: int):
        """Build Celery Canvas primitives for one pipeline layer."""
        from tdpservice.etl.tasks import advance_pipeline_run, execute_node

        layer = self.topological_layers()[layer_index]
        next_layer = advance_pipeline_run.si(pipeline_run_id, layer_index + 1)

        if len(layer) == 1:
            return chain(execute_node.si(pipeline_run_id, layer[0]), next_layer)

        return chord(
            group([execute_node.si(pipeline_run_id, node_key) for node_key in layer]),
            next_layer,
        )

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
                    "depends_on": list(node.depends_on),
                    "input_contracts": list(node.input_contracts),
                    "output_contracts": list(node.output_contracts),
                }
                for node in self.nodes
            ],
        }


def _statistical_weights_pipeline() -> PipelineDefinition:
    """Build the TANF statistical weights pipeline definition."""
    from tdpservice.etl.nodes import statistical_weights

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
        schedule={"first_workday_monthly": True},
        nodes=(
            NodeDefinition(
                key="validate_parameters",
                depends_on=(),
                implementation=statistical_weights.validate_parameters,
            ),
            NodeDefinition(
                key="extract_t1_family_counts",
                depends_on=("validate_parameters",),
                implementation=statistical_weights.extract_t1_family_counts,
                output_contracts=("weights.s1",),
            ),
            NodeDefinition(
                key="extract_t6_case_counts",
                depends_on=("validate_parameters",),
                implementation=statistical_weights.extract_t6_case_counts,
                output_contracts=("weights.s3",),
            ),
            NodeDefinition(
                key="extract_t7_section_case_counts",
                depends_on=("validate_parameters",),
                implementation=statistical_weights.extract_t7_section_case_counts,
                output_contracts=("weights.s4",),
            ),
            NodeDefinition(
                key="build_weight_candidates",
                depends_on=(
                    "extract_t1_family_counts",
                    "extract_t6_case_counts",
                    "extract_t7_section_case_counts",
                ),
                implementation=statistical_weights.build_weight_candidates,
                input_contracts=("weights.s1", "weights.s3", "weights.s4"),
                output_contracts=("statistical_weights.candidates",),
            ),
            NodeDefinition(
                key="run_weights_qa",
                depends_on=("build_weight_candidates",),
                implementation=statistical_weights.run_weights_qa,
                input_contracts=(
                    "weights.s1",
                    "weights.s3",
                    "weights.s4",
                    "statistical_weights.candidates",
                ),
            ),
            NodeDefinition(
                key="publish_weights",
                depends_on=("run_weights_qa",),
                implementation=statistical_weights.publish_weights,
                input_contracts=("statistical_weights.candidates",),
                output_contracts=("statistical_weights",),
            ),
            NodeDefinition(
                key="notify_weights_run",
                depends_on=("publish_weights",),
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
