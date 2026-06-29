"""Celery node handlers for statistical weights."""

from tdpservice.etl.models import ETLIntermediateOutput
from tdpservice.etl.notifications import send_statistical_weights_notification
from tdpservice.etl.pipelines.base import NodeResult, PipelineNode
from tdpservice.etl.pipelines.sources import SOURCE_DATAFILE_IDS_KEY
from tdpservice.etl.pipelines.statistical_weights.candidates import (
    WeightCandidateBuilder,
)
from tdpservice.etl.pipelines.statistical_weights.extractors import (
    StatisticalWeightsExtractor,
)
from tdpservice.etl.pipelines.statistical_weights.publishing import (
    StatisticalWeightsPublisher,
)
from tdpservice.etl.pipelines.statistical_weights.qa import StatisticalWeightsQA
from tdpservice.etl.pipelines.statistical_weights.sources import (
    StatisticalWeightsSources,
)


class IntermediateOutputStore:
    """Persist and read run-scoped intermediate payloads."""

    def write(self, pipeline_run, output_key: str, payload: list[dict]):
        """Persist a run-scoped intermediate output payload."""
        return ETLIntermediateOutput.objects.update_or_create(
            pipeline_run=pipeline_run,
            output_key=output_key,
            defaults={
                "payload": payload,
                "row_count": len(payload),
            },
        )[0]

    def payload(self, context, output_key: str) -> list[dict]:
        """Return a declared intermediate output payload."""
        return context.intermediate_outputs[output_key].payload


class StatisticalWeightsNodes:
    """Compose statistical weights services into runner node handlers."""

    def __init__(
        self,
        *,
        section: str,
        source_keys: dict[str, str],
        intermediate_keys: dict[str, str],
        output_key: str,
        sources: StatisticalWeightsSources | None = None,
        extractor: StatisticalWeightsExtractor | None = None,
        candidates: WeightCandidateBuilder | None = None,
        qa: StatisticalWeightsQA | None = None,
        publisher: StatisticalWeightsPublisher | None = None,
        outputs: IntermediateOutputStore | None = None,
    ):
        """Initialize node handlers with their domain services."""
        self.section = section
        self.source_keys = source_keys
        self.intermediate_keys = intermediate_keys
        self.output_key = output_key
        self.sources = sources or StatisticalWeightsSources(source_keys=source_keys)
        self.extractor = extractor or StatisticalWeightsExtractor(section=section)
        self.candidates = candidates or WeightCandidateBuilder(section=section)
        self.qa = qa or StatisticalWeightsQA()
        self.publisher = publisher or StatisticalWeightsPublisher(
            section=section,
            output_key=output_key,
        )
        self.outputs = outputs or IntermediateOutputStore()

    def as_pipeline_nodes(self) -> tuple[PipelineNode, ...]:
        """Return runner node declarations for this pipeline."""
        return (
            PipelineNode(
                key="validate_parameters",
                implementation=self.validate_parameters,
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
                key="build_weight_candidates",
                implementation=self.build_weight_candidates,
                input_contracts=(
                    self.intermediate_keys["s1"],
                    self.intermediate_keys["s3"],
                    self.intermediate_keys["s4"],
                ),
                output_contracts=(self.intermediate_keys["candidates"],),
            ),
            PipelineNode(
                key="run_weights_qa",
                implementation=self.run_weights_qa,
                input_contracts=(
                    self.intermediate_keys["s1"],
                    self.intermediate_keys["s3"],
                    self.intermediate_keys["s4"],
                    self.intermediate_keys["candidates"],
                ),
            ),
            PipelineNode(
                key="publish_weights",
                implementation=self.publish_weights,
                input_contracts=(self.intermediate_keys["candidates"],),
                output_contracts=(self.output_key,),
            ),
            PipelineNode(
                key="notify_weights_run",
                implementation=self.notify_weights_run,
                input_contracts=(self.output_key,),
            ),
        )

    def validate_parameters(self, context) -> NodeResult:
        """Validate statistical-weights parameters and snapshot source files."""
        fiscal_year = self.fiscal_year(context)
        program = self.program(context)
        if fiscal_year < 2000:
            raise ValueError("fiscal_year must be 2000 or later.")

        source_ids = self.sources.source_datafile_ids(context)
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
        datafile_ids = self.sources.source_datafile_ids(context)[
            self.source_keys["active"]
        ]
        source_count = self.extractor.active_queryset(datafile_ids, program).count()
        rows = self.extractor.active_family_counts(datafile_ids, program)
        self.outputs.write(context.pipeline_run, self.intermediate_keys["s1"], rows)
        return NodeResult(
            input_row_count=source_count,
            output_row_count=len(rows),
            metadata={
                "dataset": "s1",
                "program": program,
                "source_datafile_ids": datafile_ids,
            },
        )

    def extract_aggregate_case_counts(self, context) -> NodeResult:
        """Build and persist s3 rows."""
        program = self.program(context)
        datafile_ids = self.sources.source_datafile_ids(context)[
            self.source_keys["aggregate"]
        ]
        source_count = self.extractor.aggregate_queryset(datafile_ids, program).count()
        rows = self.extractor.aggregate_case_counts(datafile_ids, program)
        self.outputs.write(context.pipeline_run, self.intermediate_keys["s3"], rows)
        return NodeResult(
            input_row_count=source_count,
            output_row_count=len(rows),
            metadata={
                "dataset": "s3",
                "program": program,
                "source_datafile_ids": datafile_ids,
            },
        )

    def extract_stratum_case_counts(self, context) -> NodeResult:
        """Build and persist s4 rows."""
        program = self.program(context)
        datafile_ids = self.sources.source_datafile_ids(context)[
            self.source_keys["stratum"]
        ]
        source_count = self.extractor.stratum_queryset(datafile_ids, program).count()
        rows = self.extractor.stratum_section_case_counts(datafile_ids, program)
        self.outputs.write(context.pipeline_run, self.intermediate_keys["s4"], rows)
        return NodeResult(
            input_row_count=source_count,
            output_row_count=len(rows),
            metadata={
                "dataset": "s4",
                "program": program,
                "source_datafile_ids": datafile_ids,
            },
        )

    def build_weight_candidates(self, context) -> NodeResult:
        """Build and persist candidate statistical weight rows."""
        candidates = self.candidates.build(
            self.fiscal_year(context),
            self.outputs.payload(context, self.intermediate_keys["s1"]),
            self.outputs.payload(context, self.intermediate_keys["s3"]),
            self.outputs.payload(context, self.intermediate_keys["s4"]),
            self.program(context),
        )
        self.outputs.write(
            context.pipeline_run,
            self.intermediate_keys["candidates"],
            self.candidates.to_payload(candidates),
        )
        return NodeResult(
            output_row_count=len(candidates),
            metadata={"candidate_count": len(candidates)},
        )

    def run_weights_qa(self, context) -> NodeResult:
        """Run and persist statistical weights QA checks."""
        return self.qa.run(
            pipeline_run=context.pipeline_run,
            program=self.program(context),
            s1_rows=self.outputs.payload(context, self.intermediate_keys["s1"]),
            s3_rows=self.outputs.payload(context, self.intermediate_keys["s3"]),
            s4_rows=self.outputs.payload(context, self.intermediate_keys["s4"]),
            candidates=self.candidates.from_payload(
                self.outputs.payload(context, self.intermediate_keys["candidates"])
            ),
        )

    def publish_weights(self, context) -> NodeResult:
        """Publish a new immutable statistical weights version."""
        return self.publisher.publish(
            pipeline_run=context.pipeline_run,
            output_scope=context.output_scope,
            fiscal_year=self.fiscal_year(context),
            program=self.program(context),
            candidates=self.candidates.from_payload(
                self.outputs.payload(context, self.intermediate_keys["candidates"])
            ),
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
