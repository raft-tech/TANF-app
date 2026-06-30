"""Celery node handlers for statistical weights."""

from django.db import transaction

from tdpservice.etl.artifacts import upsert_table_dataset_artifact
from tdpservice.etl.models import (
    StatisticalWeightCandidate,
    StatisticalWeightsActiveFamilyCount,
    StatisticalWeightsAggregateCaseCount,
    StatisticalWeightsStratumCaseCount,
)
from tdpservice.etl.notifications import send_statistical_weights_notification
from tdpservice.etl.pipelines.base import NodeResult, PipelineNode
from tdpservice.etl.pipelines.sources import SOURCE_DATAFILE_IDS_KEY
from tdpservice.etl.pipelines.statistical_weights.candidates import (
    WeightCandidate,
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


class StatisticalWeightsArtifactStore:
    """Persist and read run-scoped statistical weights artifacts."""

    schema_keys = {
        "s1": "statistical_weights.s1",
        "s3": "statistical_weights.s3",
        "s4": "statistical_weights.s4",
        "candidates": "statistical_weights.candidates",
    }

    def __init__(self, *, intermediate_keys: dict[str, str]):
        """Initialize the store with pipeline artifact keys."""
        self.intermediate_keys = intermediate_keys

    def write_active_family_counts(
        self,
        pipeline_run,
        rows: list[dict],
        metadata: dict | None = None,
    ):
        """Replace and manifest s1 active-family count rows."""
        objects = [
            StatisticalWeightsActiveFamilyCount(
                pipeline_run=pipeline_run,
                stt_code=row["stt_code"],
                reporting_month=row["reporting_month"],
                stratum=row["stratum"],
                case_count=row["case_count"],
            )
            for row in rows
        ]
        return self._replace_rows(
            pipeline_run=pipeline_run,
            key_name="s1",
            model=StatisticalWeightsActiveFamilyCount,
            objects=objects,
            metadata=metadata,
        )

    def write_aggregate_case_counts(
        self,
        pipeline_run,
        rows: list[dict],
        metadata: dict | None = None,
    ):
        """Replace and manifest s3 aggregate case count rows."""
        objects = [
            StatisticalWeightsAggregateCaseCount(
                pipeline_run=pipeline_run,
                stt_code=row["stt_code"],
                reporting_month=row["reporting_month"],
                case_count=row["case_count"],
            )
            for row in rows
        ]
        return self._replace_rows(
            pipeline_run=pipeline_run,
            key_name="s3",
            model=StatisticalWeightsAggregateCaseCount,
            objects=objects,
            metadata=metadata,
        )

    def write_stratum_case_counts(
        self,
        pipeline_run,
        rows: list[dict],
        metadata: dict | None = None,
    ):
        """Replace and manifest s4 stratum case count rows."""
        objects = [
            StatisticalWeightsStratumCaseCount(
                pipeline_run=pipeline_run,
                stt_code=row["stt_code"],
                reporting_month=row["reporting_month"],
                stratum=row["stratum"],
                cases=row["cases"],
            )
            for row in rows
        ]
        return self._replace_rows(
            pipeline_run=pipeline_run,
            key_name="s4",
            model=StatisticalWeightsStratumCaseCount,
            objects=objects,
            metadata=metadata,
        )

    def write_candidates(
        self,
        pipeline_run,
        candidates: list[WeightCandidate],
        metadata: dict | None = None,
    ):
        """Replace and manifest candidate statistical weight rows."""
        objects = [
            StatisticalWeightCandidate(
                pipeline_run=pipeline_run,
                fiscal_year=candidate.fiscal_year,
                reporting_month=candidate.reporting_month,
                program=candidate.program,
                section=candidate.section,
                stt_code=candidate.stt_code,
                stratum=candidate.stratum,
                case_count=candidate.case_count,
                cases=candidate.cases,
                weight=candidate.weight,
            )
            for candidate in candidates
        ]
        return self._replace_rows(
            pipeline_run=pipeline_run,
            key_name="candidates",
            model=StatisticalWeightCandidate,
            objects=objects,
            metadata=metadata,
        )

    def active_family_count_rows(self, context) -> list[dict]:
        """Return s1 rows from the table-backed artifact."""
        self._artifact(context, "s1")
        return list(
            StatisticalWeightsActiveFamilyCount.objects.filter(
                pipeline_run=context.pipeline_run
            )
            .order_by("stt_code", "reporting_month", "stratum")
            .values("stt_code", "reporting_month", "stratum", "case_count")
        )

    def aggregate_case_count_rows(self, context) -> list[dict]:
        """Return s3 rows from the table-backed artifact."""
        self._artifact(context, "s3")
        return list(
            StatisticalWeightsAggregateCaseCount.objects.filter(
                pipeline_run=context.pipeline_run
            )
            .order_by("stt_code", "reporting_month")
            .values("stt_code", "reporting_month", "case_count")
        )

    def stratum_case_count_rows(self, context) -> list[dict]:
        """Return s4 rows from the table-backed artifact."""
        self._artifact(context, "s4")
        return list(
            StatisticalWeightsStratumCaseCount.objects.filter(
                pipeline_run=context.pipeline_run
            )
            .order_by("stt_code", "reporting_month", "stratum")
            .values("stt_code", "reporting_month", "stratum", "cases")
        )

    def candidates(self, context) -> list[WeightCandidate]:
        """Return candidate rows from the table-backed artifact."""
        self._artifact(context, "candidates")
        return [
            WeightCandidate(
                fiscal_year=row.fiscal_year,
                reporting_month=row.reporting_month,
                program=row.program,
                section=row.section,
                stt_code=row.stt_code,
                stratum=row.stratum,
                case_count=row.case_count,
                cases=row.cases,
                weight=row.weight,
            )
            for row in StatisticalWeightCandidate.objects.filter(
                pipeline_run=context.pipeline_run
            ).order_by("stt_code", "reporting_month", "stratum")
        ]

    def _replace_rows(
        self,
        *,
        pipeline_run,
        key_name: str,
        model,
        objects: list,
        metadata: dict | None,
    ):
        """Replace table rows and upsert the matching artifact manifest."""
        with transaction.atomic():
            model.objects.filter(pipeline_run=pipeline_run).delete()
            model.objects.bulk_create(objects)
            return upsert_table_dataset_artifact(
                pipeline_run=pipeline_run,
                key=self.intermediate_keys[key_name],
                model=model,
                schema_key=self.schema_keys[key_name],
                row_count=len(objects),
                metadata=metadata,
            )

    def _artifact(self, context, key_name: str):
        """Return a declared artifact from node context."""
        return context.artifacts[self.intermediate_keys[key_name]]


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
        artifacts: StatisticalWeightsArtifactStore | None = None,
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
        self.artifacts = artifacts or StatisticalWeightsArtifactStore(
            intermediate_keys=intermediate_keys,
        )

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
        datafile_ids = self.sources.source_datafile_ids(context)[
            self.source_keys["aggregate"]
        ]
        source_count = self.extractor.aggregate_queryset(datafile_ids, program).count()
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
        datafile_ids = self.sources.source_datafile_ids(context)[
            self.source_keys["stratum"]
        ]
        source_count = self.extractor.stratum_queryset(datafile_ids, program).count()
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

    def build_weight_candidates(self, context) -> NodeResult:
        """Build and persist candidate statistical weight rows."""
        candidates = self.candidates.build(
            self.fiscal_year(context),
            self.artifacts.active_family_count_rows(context),
            self.artifacts.aggregate_case_count_rows(context),
            self.artifacts.stratum_case_count_rows(context),
            self.program(context),
        )
        self.artifacts.write_candidates(
            context.pipeline_run,
            candidates,
            metadata={"candidate_count": len(candidates)},
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
            s1_rows=self.artifacts.active_family_count_rows(context),
            s3_rows=self.artifacts.aggregate_case_count_rows(context),
            s4_rows=self.artifacts.stratum_case_count_rows(context),
            candidates=self.artifacts.candidates(context),
        )

    def publish_weights(self, context) -> NodeResult:
        """Publish a new immutable statistical weights version."""
        return self.publisher.publish(
            pipeline_run=context.pipeline_run,
            output_scope=context.output_scope,
            fiscal_year=self.fiscal_year(context),
            program=self.program(context),
            candidates=self.artifacts.candidates(context),
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
