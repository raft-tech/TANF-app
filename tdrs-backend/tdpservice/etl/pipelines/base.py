from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable

from tdpservice.etl.exceptions import PipelineValidationError


@dataclass(frozen=True)
class PipelineNode:
    """Executable node registered for one ETL pipeline."""

    key: str
    implementation: Callable
    input_contracts: tuple[str, ...] = ()
    output_contracts: tuple[str, ...] = ()


@dataclass(frozen=True)
class NodeResult:
    """Structured result returned by a node implementation."""

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
    nodes: tuple[PipelineNode, ...]
    schedule: dict | None = None
    required_groups: tuple[str, ...] = ("OFA System Admin",)

    @property
    def node_map(self) -> dict[str, PipelineNode]:
        """Return nodes keyed by node key."""
        return {node.key: node for node in self.nodes}

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
