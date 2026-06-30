"""Celery node handlers for statistical weights."""

from django.db import transaction

from tdpservice.etl.artifacts import upsert_table_dataset_artifact
from tdpservice.etl.models import StatisticalWeightsCaseCount
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
    }
    count_kinds = {
        "s1": StatisticalWeightsCaseCount.CountKind.ACTIVE_FAMILY,
        "s3": StatisticalWeightsCaseCount.CountKind.AGGREGATE_CASE,
        "s4": StatisticalWeightsCaseCount.CountKind.STRATUM_CASE,
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
            StatisticalWeightsCaseCount(
                pipeline_run=pipeline_run,
                count_kind=self.count_kinds["s1"],
                stt_code=row["stt_code"],
                reporting_month=row["reporting_month"],
                stratum=row["stratum"],
                count=row["case_count"],
            )
            for row in rows
        ]
        return self._replace_rows(
            pipeline_run=pipeline_run,
            key_name="s1",
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
            StatisticalWeightsCaseCount(
                pipeline_run=pipeline_run,
                count_kind=self.count_kinds["s3"],
                stt_code=row["stt_code"],
                reporting_month=row["reporting_month"],
                count=row["case_count"],
            )
            for row in rows
        ]
        return self._replace_rows(
            pipeline_run=pipeline_run,
            key_name="s3",
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
            StatisticalWeightsCaseCount(
                pipeline_run=pipeline_run,
                count_kind=self.count_kinds["s4"],
                stt_code=row["stt_code"],
                reporting_month=row["reporting_month"],
                stratum=row["stratum"],
                count=row["cases"],
            )
            for row in rows
        ]
        return self._replace_rows(
            pipeline_run=pipeline_run,
            key_name="s4",
            objects=objects,
            metadata=metadata,
        )

    def active_family_count_rows(self, context) -> list[dict]:
        """Return s1 rows from the table-backed artifact."""
        self._artifact(context, "s1")
        return [
            {
                "stt_code": row.stt_code,
                "reporting_month": row.reporting_month,
                "stratum": row.stratum,
                "case_count": row.count,
            }
            for row in (
                StatisticalWeightsCaseCount.objects.filter(
                    pipeline_run=context.pipeline_run,
                    count_kind=self.count_kinds["s1"],
                ).order_by("stt_code", "reporting_month", "stratum")
            )
        ]

    def aggregate_case_count_rows(self, context) -> list[dict]:
        """Return s3 rows from the table-backed artifact."""
        self._artifact(context, "s3")
        return [
            {
                "stt_code": row.stt_code,
                "reporting_month": row.reporting_month,
                "case_count": row.count,
            }
            for row in (
                StatisticalWeightsCaseCount.objects.filter(
                    pipeline_run=context.pipeline_run,
                    count_kind=self.count_kinds["s3"],
                ).order_by("stt_code", "reporting_month")
            )
        ]

    def stratum_case_count_rows(self, context) -> list[dict]:
        """Return s4 rows from the table-backed artifact."""
        self._artifact(context, "s4")
        return [
            {
                "stt_code": row.stt_code,
                "reporting_month": row.reporting_month,
                "stratum": row.stratum,
                "cases": row.count,
            }
            for row in (
                StatisticalWeightsCaseCount.objects.filter(
                    pipeline_run=context.pipeline_run,
                    count_kind=self.count_kinds["s4"],
                ).order_by("stt_code", "reporting_month", "stratum")
            )
        ]

    def _replace_rows(
        self,
        *,
        pipeline_run,
        key_name: str,
        objects: list,
        metadata: dict | None,
    ):
        """Replace table rows and upsert the matching artifact manifest."""
        count_kind = self.count_kinds[key_name]
        artifact_metadata = {"count_kind": count_kind.value, **(metadata or {})}
        with transaction.atomic():
            StatisticalWeightsCaseCount.objects.filter(
                pipeline_run=pipeline_run,
                count_kind=count_kind,
            ).delete()
            StatisticalWeightsCaseCount.objects.bulk_create(objects)
            return upsert_table_dataset_artifact(
                pipeline_run=pipeline_run,
                key=self.intermediate_keys[key_name],
                model=StatisticalWeightsCaseCount,
                schema_key=self.schema_keys[key_name],
                row_count=len(objects),
                metadata=artifact_metadata,
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
