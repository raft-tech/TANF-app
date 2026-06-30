"""Artifact persistence for statistical weights."""

from django.db import transaction

from tdpservice.etl.artifacts import upsert_table_dataset_artifact
from tdpservice.etl.models import StatisticalWeightsCaseCount


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
