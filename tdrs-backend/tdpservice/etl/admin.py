"""Admin registrations for ETL models."""

from django.contrib import admin

from tdpservice.etl.models import (
    ETLIntermediateOutput,
    ETLNodeRun,
    ETLOutput,
    ETLPipelineRun,
    ETLQAResult,
    StatisticalWeight,
)


@admin.register(ETLPipelineRun)
class ETLPipelineRunAdmin(admin.ModelAdmin):
    """Admin view for pipeline runs."""

    list_display = (
        "id",
        "pipeline_key",
        "pipeline_version",
        "status",
        "trigger_source",
        "triggered_by",
        "final_output",
        "created_at",
        "started_at",
        "finished_at",
    )
    list_filter = ("pipeline_key", "status", "trigger_source")
    search_fields = ("pipeline_key", "error_message")
    readonly_fields = ("final_output", "created_at", "updated_at")


@admin.register(ETLNodeRun)
class ETLNodeRunAdmin(admin.ModelAdmin):
    """Admin view for node runs."""

    list_display = (
        "id",
        "pipeline_run",
        "node_key",
        "status",
        "input_row_count",
        "output_row_count",
    )
    list_filter = ("node_key", "status")
    search_fields = ("node_key", "error_message")


@admin.register(ETLQAResult)
class ETLQAResultAdmin(admin.ModelAdmin):
    """Admin view for QA results."""

    list_display = ("id", "pipeline_run", "check_key", "status", "blocking")
    list_filter = ("check_key", "status", "blocking")
    search_fields = ("check_key", "summary")


@admin.register(ETLOutput)
class ETLOutputAdmin(admin.ModelAdmin):
    """Admin view for outputs."""

    list_display = (
        "id",
        "pipeline_run",
        "output_key",
        "output_kind",
        "output_version",
        "row_count",
        "published",
    )
    list_filter = ("output_key", "output_kind", "published")
    search_fields = ("output_key", "reference")


@admin.register(ETLIntermediateOutput)
class ETLIntermediateOutputAdmin(admin.ModelAdmin):
    """Admin view for run-scoped intermediate outputs."""

    list_display = ("id", "pipeline_run", "output_key", "row_count", "created_at")
    list_filter = ("output_key",)
    search_fields = ("output_key",)


@admin.register(StatisticalWeight)
class StatisticalWeightAdmin(admin.ModelAdmin):
    """Admin view for statistical weights."""

    list_display = (
        "id",
        "fiscal_year",
        "reporting_month",
        "program",
        "section",
        "stt_code",
        "stratum",
        "version",
        "weight",
        "retention_expires_at",
    )
    list_filter = ("fiscal_year", "program", "section", "version")
    search_fields = ("stt_code", "stratum")
