"""Source extractors for statistical weights."""

from django.db.models import Count, Sum

from tdpservice.etl.pipelines.statistical_weights.adapters import adapter_for_program


class StatisticalWeightsExtractor:
    """Extract run-scoped s1, s3, and s4 rows for statistical weights."""

    def __init__(self, *, section: str):
        """Initialize the extractor with the statistical weights section."""
        self.section = section

    def active_queryset(self, datafile_ids: list[int], program_type: str):
        """Return active-case rows in scope."""
        return adapter_for_program(program_type).active_queryset(datafile_ids)

    def aggregate_queryset(self, datafile_ids: list[int], program_type: str):
        """Return aggregate rows in scope."""
        return adapter_for_program(program_type).aggregate_queryset(datafile_ids)

    def stratum_queryset(self, datafile_ids: list[int], program_type: str):
        """Return stratum rows in scope."""
        return adapter_for_program(program_type).stratum_queryset(datafile_ids)

    def active_family_counts(
        self,
        datafile_ids: list[int],
        program_type: str,
    ) -> list[dict]:
        """Build s1: unique families by STT, reporting month, and stratum."""
        adapter = adapter_for_program(program_type)
        rows = (
            adapter.active_queryset(datafile_ids)
            .values("datafile__stt__stt_code", "RPT_MONTH_YEAR", "STRATUM")
            .annotate(case_count=Count("CASE_NUMBER", distinct=True))
            .order_by("datafile__stt__stt_code", "RPT_MONTH_YEAR", "STRATUM")
        )
        return [
            {
                "stt_code": adapter.normalize_code(row["datafile__stt__stt_code"]),
                "reporting_month": row["RPT_MONTH_YEAR"],
                "stratum": adapter.normalize_code(row["STRATUM"]),
                "case_count": int(row["case_count"] or 0),
            }
            for row in rows
        ]

    def aggregate_case_counts(
        self,
        datafile_ids: list[int],
        program_type: str,
    ) -> list[dict]:
        """Build s3: aggregate cases by STT and reporting month."""
        adapter = adapter_for_program(program_type)
        rows = (
            adapter.aggregate_queryset(datafile_ids)
            .values("datafile__stt__stt_code", "RPT_MONTH_YEAR")
            .annotate(case_count=Sum(adapter.aggregate_case_count_field))
            .order_by("datafile__stt__stt_code", "RPT_MONTH_YEAR")
        )
        return [
            {
                "stt_code": adapter.normalize_code(row["datafile__stt__stt_code"]),
                "reporting_month": row["RPT_MONTH_YEAR"],
                "case_count": int(row["case_count"] or 0),
            }
            for row in rows
        ]

    def stratum_section_case_counts(
        self,
        datafile_ids: list[int],
        program_type: str,
    ) -> list[dict]:
        """Build s4: stratum cases by STT, reporting month, and stratum."""
        adapter = adapter_for_program(program_type)
        rows = (
            adapter.stratum_queryset(datafile_ids)
            .filter(TDRS_SECTION_IND=self.section, FAMILIES_MONTH__gt=0)
            .values("datafile__stt__stt_code", "RPT_MONTH_YEAR", "STRATUM")
            .annotate(cases=Sum("FAMILIES_MONTH"))
            .order_by("datafile__stt__stt_code", "RPT_MONTH_YEAR", "STRATUM")
        )
        return [
            {
                "stt_code": adapter.normalize_code(row["datafile__stt__stt_code"]),
                "reporting_month": row["RPT_MONTH_YEAR"],
                "stratum": adapter.normalize_code(row["STRATUM"]),
                "cases": int(row["cases"] or 0),
            }
            for row in rows
        ]
