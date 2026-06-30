"""Pipeline definition for statistical weights."""

from typing import Any

from celery import chain, chord

from tdpservice.data_files.models import DataFile
from tdpservice.etl.exceptions import PipelineValidationError
from tdpservice.etl.pipelines.base import PipelineDefinition
from tdpservice.etl.pipelines.statistical_weights.nodes import StatisticalWeightsNodes


class StatisticalWeightsPipeline(PipelineDefinition):
    """Pipeline definition for Section 1 statistical weights."""

    key = "statistical_weights"
    version = "1"
    display_name = "Statistical Weights"
    description = (
        "Generate Section 1 statistical weights for a fiscal year and program."
    )
    schedule = {"first_workday_monthly": True}

    # TODO: Alex indicated this pipeline executes for section 1 and 2. But I don't see the scripts for it. Hard coded
    # to section 1 for now.
    section = "1"
    source_keys = {
        "active": "active",
        "aggregate": "aggregate",
        "stratum": "stratum",
    }
    intermediate_keys = {
        "s1": "weights.s1",
        "s3": "weights.s3",
        "s4": "weights.s4",
    }
    output_key = "statistical_weights"
    supported_program_types = (
        DataFile.ProgramType.TANF,
        DataFile.ProgramType.SSP,
        DataFile.ProgramType.TRIBAL,
    )
    allowed_parameters = {
        "fiscal_year": {
            "type": "integer",
            "required": True,
            "description": "Fiscal year to generate weights for.",
        },
        "program": {
            "type": "string",
            "required": True,
            "description": "DataFile program type to generate weights for.",
            "choices": list(supported_program_types),
        },
    }

    def __init__(self, node_handlers: StatisticalWeightsNodes | None = None):
        """Initialize this pipeline's executable node declarations."""
        self.node_handlers = node_handlers or StatisticalWeightsNodes(
            section=self.section,
            source_keys=self.source_keys,
            intermediate_keys=self.intermediate_keys,
            output_key=self.output_key,
        )
        self.nodes = self.node_handlers.as_pipeline_nodes()

    def validate_parameters(self, parameters: dict) -> dict:
        """Validate statistical weights run parameters."""
        validated = dict(parameters or {})
        unexpected = set(validated) - set(self.allowed_parameters)
        if unexpected:
            raise PipelineValidationError(
                f"Unexpected parameters: {sorted(unexpected)}"
            )

        for name, metadata in self.allowed_parameters.items():
            if metadata.get("required") and name not in validated:
                raise PipelineValidationError(f"Missing required parameter: {name}")

        validated["fiscal_year"] = self._normalize_fiscal_year(validated["fiscal_year"])
        validated["program"] = self._validate_program_type(validated["program"])
        return validated

    def output_scope(self, parameters: dict) -> dict:
        """Build the idempotency/output scope for statistical weights."""
        return {
            "pipeline": self.key,
            "fiscal_year": int(parameters["fiscal_year"]),
            "program": self._validate_program_type(parameters["program"]),
            "section": self.section,
        }

    def datafile_sources(self, program: str):
        """Return this pipeline's DataFile source declarations."""
        return self.node_handlers.sources.datafile_sources(program)

    def build_canvas(self, pipeline_run_id: int) -> Any:
        """Build the Celery Canvas for the statistical weights DAG."""
        from tdpservice.etl.tasks import execute_node, finalize_pipeline_run

        run_weights_qa_signature = execute_node.si(
            pipeline_run_id,
            "run_weights_qa",
        )
        downstream = chain(
            execute_node.si(pipeline_run_id, "publish_weights"),
            execute_node.si(pipeline_run_id, "notify_weights_run"),
            finalize_pipeline_run.si(pipeline_run_id),
        )
        downstream.set(immutable=True)
        run_weights_qa_signature.link(downstream)

        return chain(
            execute_node.si(pipeline_run_id, "validate_parameters"),
            chord(
                [
                    execute_node.si(
                        pipeline_run_id,
                        "extract_active_family_counts",
                    ),
                    execute_node.si(
                        pipeline_run_id,
                        "extract_aggregate_case_counts",
                    ),
                    execute_node.si(
                        pipeline_run_id,
                        "extract_stratum_case_counts",
                    ),
                ],
                run_weights_qa_signature,
            ),
        )

    @staticmethod
    def _normalize_fiscal_year(value) -> int:
        """Normalize and validate fiscal year."""
        try:
            fiscal_year = int(value)
        except (TypeError, ValueError) as exc:
            raise PipelineValidationError("fiscal_year must be an integer.") from exc

        if fiscal_year < 2000:
            raise PipelineValidationError("fiscal_year must be 2000 or later.")
        return fiscal_year

    @classmethod
    def _validate_program_type(cls, value) -> str:
        """Validate that program is an exact DataFile.ProgramType value."""
        if value not in cls.supported_program_types:
            choices = ", ".join(cls.supported_program_types)
            raise PipelineValidationError(f"program must be one of: {choices}.")
        return value
