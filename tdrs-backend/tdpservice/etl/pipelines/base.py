"""Base contracts for code-owned ETL pipelines."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Iterable

from tdpservice.etl.exceptions import PipelineValidationError


@dataclass(frozen=True)
class PipelineNode:
    """Run bookkeeping for one executable node in an ETL pipeline."""

    key: str
    input_contracts: tuple[str, ...] = ()
    output_contracts: tuple[str, ...] = ()

    def execute(self, definition: "PipelineDefinition", context) -> Any:
        """Run this node's pipeline-owned handler."""
        return getattr(definition, self.key)(context)

    def task(self, pipeline_run_id: int):
        """Return the Celery signature for this node."""
        from tdpservice.etl.tasks import execute_node

        return execute_node.si(pipeline_run_id, self.key)


class PipelineNodeRegistry:
    """Node collection addressable by node key or attribute name."""

    def __init__(self, nodes: Iterable[PipelineNode]):
        """Initialize a registry from pipeline-owned nodes."""
        self._nodes = tuple(nodes)
        self._node_map = {node.key: node for node in self._nodes}

    def __iter__(self):
        """Iterate over registered nodes in declaration order."""
        return iter(self._nodes)

    def __getitem__(self, key: str) -> PipelineNode:
        """Return a node by ETLNodeRun node_key."""
        try:
            return self._node_map[key]
        except KeyError as exc:
            raise PipelineValidationError(f"Unknown pipeline node: {key}") from exc

    def __getattr__(self, key: str) -> PipelineNode:
        """Return a node by attribute when the key is a valid Python name."""
        try:
            return self[key]
        except PipelineValidationError as exc:
            raise AttributeError(key) from exc


@dataclass(frozen=True)
class NodeResult:
    """Structured result returned by a node handler."""

    input_row_count: int | None = None
    output_row_count: int | None = None
    metadata: dict = field(default_factory=dict)


class PipelineDefinition(ABC):
    """Base interface for one approved ETL pipeline."""

    key: str
    version: str
    display_name: str
    description: str
    allowed_parameters: dict
    nodes: PipelineNodeRegistry
    schedule: dict | None = None
    required_groups: tuple[str, ...] = ("OFA System Admin",)

    @abstractmethod
    def validate_parameters(self, parameters: dict) -> dict:
        """Validate and normalize run parameters for this pipeline."""

    @abstractmethod
    def output_scope(self, parameters: dict) -> dict:
        """Build the idempotency/output scope for this pipeline."""

    def validate(self) -> None:
        """Validate node metadata for this pipeline."""
        node_keys = [node.key for node in self.nodes]
        if len(node_keys) != len(set(node_keys)):
            raise PipelineValidationError("Pipeline node keys must be unique.")

        missing_handlers = [
            node.key
            for node in self.nodes
            if not callable(getattr(self, node.key, None))
        ]
        if missing_handlers:
            raise PipelineValidationError(
                f"Pipeline node handlers are missing: {sorted(missing_handlers)}"
            )

    @abstractmethod
    def build_canvas(self, pipeline_run_id: int) -> Any:
        """Build the code-owned Celery Canvas for this pipeline run."""

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
