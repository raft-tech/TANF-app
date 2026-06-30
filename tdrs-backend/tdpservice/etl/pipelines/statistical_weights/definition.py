"""Pipeline definition for statistical weights."""

from typing import Any

from celery import chain, chord

from tdpservice.data_files.models import DataFile
from tdpservice.etl.exceptions import PipelineValidationError
from tdpservice.etl.notifications import send_statistical_weights_notification
from tdpservice.etl.pipelines.base import NodeResult, PipelineDefinition, PipelineNode
from tdpservice.etl.pipelines.sources import (
    SOURCE_DATAFILE_IDS_KEY,
    DataFileSource,
    DataFileSourceSnapshot,
)
from tdpservice.etl.pipelines.statistical_weights.adapters import adapter_for_program
from tdpservice.etl.pipelines.statistical_weights.candidates import (
    WeightCandidate,
    WeightCandidateBuilder,
)
from tdpservice.etl.pipelines.statistical_weights.extractors import (
    StatisticalWeightsExtractor,
)
from tdpservice.etl.pipelines.statistical_weights.nodes import (
    StatisticalWeightsArtifactStore,
)
from tdpservice.etl.pipelines.statistical_weights.publishing import (
    StatisticalWeightsPublisher,
)
from tdpservice.etl.pipelines.statistical_weights.qa import StatisticalWeightsQA


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

    def __init__(self):
        """Initialize this pipeline's executable node declarations."""
        self.datafile_snapshot = DataFileSourceSnapshot()
        self.extractor = StatisticalWeightsExtractor(section=self.section)
        self.candidates = WeightCandidateBuilder(section=self.section)
        self.qa = StatisticalWeightsQA()
        self.publisher = StatisticalWeightsPublisher(
            section=self.section,
            output_key=self.output_key,
        )
        self.artifacts = StatisticalWeightsArtifactStore(
            intermediate_keys=self.intermediate_keys,
        )
        self.nodes = self._pipeline_nodes()

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

    def datafile_sources(self, program: str) -> tuple[DataFileSource, ...]:
        """Return this pipeline's DataFile source declarations."""
        adapter = adapter_for_program(program)
        return (
            DataFileSource(
                key=self.source_keys["active"],
                program_type=adapter.program_type,
                section=DataFile.Section.ACTIVE_CASE_DATA,
            ),
            DataFileSource(
                key=self.source_keys["aggregate"],
                program_type=adapter.program_type,
                section=DataFile.Section.AGGREGATE_DATA,
            ),
            DataFileSource(
                key=self.source_keys["stratum"],
                program_type=adapter.program_type,
                section=DataFile.Section.STRATUM_DATA,
            ),
        )

    def snapshot_source_datafile_ids(
        self,
        fiscal_year: int,
        program_type: str,
    ) -> dict[str, list[int]]:
        """Return a fresh source DataFile snapshot for one weights run."""
        return self.datafile_snapshot.build_snapshot(
            fiscal_year=fiscal_year,
            sources=self.datafile_sources(program_type),
        )

    def source_datafile_ids(self, context) -> dict[str, list[int]]:
        """Return a run's source DataFile snapshot, creating it once when needed."""
        return self.datafile_snapshot.snapshot(
            context.pipeline_run,
            fiscal_year=int(context.parameters["fiscal_year"]),
            sources=self.datafile_sources(context.parameters["program"]),
        )

    def build_canvas(self, pipeline_run_id: int) -> Any:
        """Build the Celery Canvas for the statistical weights DAG."""
        from tdpservice.etl.tasks import execute_node, finalize_pipeline_run

        run_weights_qa_signature = execute_node.si(
            pipeline_run_id,
            "run_weights_qa",
        )
        finalize = chain(
            execute_node.si(pipeline_run_id, "publish_weights"),
            execute_node.si(pipeline_run_id, "notify_weights_run"),
            finalize_pipeline_run.si(pipeline_run_id),
        )
        finalize.set(immutable=True)
        run_weights_qa_signature.link(finalize)

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

    def _pipeline_nodes(self) -> tuple[PipelineNode, ...]:
        """Return runner node declarations for this pipeline."""
        return (
            PipelineNode(
                key="validate_parameters",
                implementation=self.validate_run_sources,
            ),
            PipelineNode(
                key="extract_active_family_counts",
                implementation=self.extract_active_family_counts,
                output_contracts=(self.intermediate_keys["s1"],),
            ),
            PipelineNode(
                key="extract_aggregate_case_counts",
                implementation=self.extract_aggregate_case_counts,
                output_contracts=(self.intermediate_keys["s3"],),
            ),
            PipelineNode(
                key="extract_stratum_case_counts",
                implementation=self.extract_stratum_case_counts,
                output_contracts=(self.intermediate_keys["s4"],),
            ),
            PipelineNode(
                key="run_weights_qa",
                implementation=self.run_weights_qa,
                input_contracts=(
                    self.intermediate_keys["s1"],
                    self.intermediate_keys["s3"],
                    self.intermediate_keys["s4"],
                ),
            ),
            PipelineNode(
                key="publish_weights",
                implementation=self.publish_weights,
                input_contracts=(
                    self.intermediate_keys["s1"],
                    self.intermediate_keys["s3"],
                    self.intermediate_keys["s4"],
                ),
                output_contracts=(self.output_key,),
            ),
            PipelineNode(
                key="notify_weights_run",
                implementation=self.notify_weights_run,
                input_contracts=(self.output_key,),
            ),
        )

    def validate_run_sources(self, context) -> NodeResult:
        """Validate statistical-weights parameters and snapshot source files."""
        fiscal_year = self.fiscal_year(context)
        program = self.program(context)
        if fiscal_year < 2000:
            raise ValueError("fiscal_year must be 2000 or later.")

        source_ids = self.source_datafile_ids(context)
        missing_sources = [
            source_key
            for source_key, datafile_ids in source_ids.items()
            if not datafile_ids
        ]
        if missing_sources:
            missing_list = ", ".join(sorted(missing_sources))
            raise ValueError(
                "No accepted DataFiles found for required statistical weights "
                f"sources: {missing_list}."
            )

        return NodeResult(
            metadata={
                "fiscal_year": fiscal_year,
                "program": program,
                SOURCE_DATAFILE_IDS_KEY: source_ids,
            }
        )

    def extract_active_family_counts(self, context) -> NodeResult:
        """Build and persist s1 rows."""
        program = self.program(context)
        adapter = adapter_for_program(program)
        datafile_ids = self.source_datafile_ids(context)[self.source_keys["active"]]
        source_count = adapter.active_queryset(datafile_ids).count()
        rows = self.extractor.active_family_counts(datafile_ids, program)
        metadata = {
            "dataset": "s1",
            "program": program,
            "source_datafile_ids": datafile_ids,
        }
        self.artifacts.write_active_family_counts(
            context.pipeline_run,
            rows,
            metadata=metadata,
        )
        return NodeResult(
            input_row_count=source_count,
            output_row_count=len(rows),
            metadata=metadata,
        )

    def extract_aggregate_case_counts(self, context) -> NodeResult:
        """Build and persist s3 rows."""
        program = self.program(context)
        adapter = adapter_for_program(program)
        datafile_ids = self.source_datafile_ids(context)[self.source_keys["aggregate"]]
        source_count = adapter.aggregate_queryset(datafile_ids).count()
        rows = self.extractor.aggregate_case_counts(datafile_ids, program)
        metadata = {
            "dataset": "s3",
            "program": program,
            "source_datafile_ids": datafile_ids,
        }
        self.artifacts.write_aggregate_case_counts(
            context.pipeline_run,
            rows,
            metadata=metadata,
        )
        return NodeResult(
            input_row_count=source_count,
            output_row_count=len(rows),
            metadata=metadata,
        )

    def extract_stratum_case_counts(self, context) -> NodeResult:
        """Build and persist s4 rows."""
        program = self.program(context)
        adapter = adapter_for_program(program)
        datafile_ids = self.source_datafile_ids(context)[self.source_keys["stratum"]]
        source_count = adapter.stratum_queryset(datafile_ids).count()
        rows = self.extractor.stratum_section_case_counts(datafile_ids, program)
        metadata = {
            "dataset": "s4",
            "program": program,
            "source_datafile_ids": datafile_ids,
        }
        self.artifacts.write_stratum_case_counts(
            context.pipeline_run,
            rows,
            metadata=metadata,
        )
        return NodeResult(
            input_row_count=source_count,
            output_row_count=len(rows),
            metadata=metadata,
        )

    def build_candidates(
        self,
        context,
        *,
        s1_rows: list[dict] | None = None,
        s3_rows: list[dict] | None = None,
        s4_rows: list[dict] | None = None,
    ) -> list[WeightCandidate]:
        """Build candidate statistical weight rows from persisted aggregates."""
        if s1_rows is None:
            s1_rows = self.artifacts.active_family_count_rows(context)
        if s3_rows is None:
            s3_rows = self.artifacts.aggregate_case_count_rows(context)
        if s4_rows is None:
            s4_rows = self.artifacts.stratum_case_count_rows(context)
        return self.candidates.build(
            self.fiscal_year(context),
            s1_rows,
            s3_rows,
            s4_rows,
            self.program(context),
        )

    def run_weights_qa(self, context) -> NodeResult:
        """Run and persist statistical weights QA checks."""
        s1_rows = self.artifacts.active_family_count_rows(context)
        s3_rows = self.artifacts.aggregate_case_count_rows(context)
        s4_rows = self.artifacts.stratum_case_count_rows(context)
        candidates = self.build_candidates(
            context,
            s1_rows=s1_rows,
            s3_rows=s3_rows,
            s4_rows=s4_rows,
        )
        return self.qa.run(
            pipeline_run=context.pipeline_run,
            program=self.program(context),
            s1_rows=s1_rows,
            s3_rows=s3_rows,
            s4_rows=s4_rows,
            candidates=candidates,
        )

    def publish_weights(self, context) -> NodeResult:
        """Publish a new immutable statistical weights version."""
        return self.publisher.publish(
            pipeline_run=context.pipeline_run,
            output_scope=context.output_scope,
            fiscal_year=self.fiscal_year(context),
            program=self.program(context),
            candidates=self.build_candidates(context),
        )

    def notify_weights_run(self, context) -> NodeResult:
        """Notify operational users that a statistical weights run completed."""
        return NodeResult(
            metadata=send_statistical_weights_notification(context.pipeline_run)
        )

    def fiscal_year(self, context) -> int:
        """Return the fiscal year parameter."""
        return int(context.parameters["fiscal_year"])

    def program(self, context) -> str:
        """Return the exact DataFile program type parameter for this run."""
        return context.parameters["program"]

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
