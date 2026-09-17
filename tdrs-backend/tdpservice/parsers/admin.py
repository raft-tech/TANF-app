"""Django admin customizations for the parser models."""
from django.contrib import admin

from django.contrib.contenttypes.admin import GenericTabularInline

from tdpservice.core.admin import BaseLogAdmin
from tdpservice.core.utils import ReadOnlyAdminMixin

from . import models


# Register your models here.
class ParserErrorAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """ModelAdmin class for ParserError objects generated in parsing."""

    list_per_page = 25
    show_full_result_count = False

    list_display = [
        "row_number",
        "field_name",
        "error_type",
        "error_message",
    ]

    fields = [
        "file",
        "row_number",
        "column_number",
        "item_number",
        "field_name",
        "rpt_month_year",
        "case_number",
        "error_message",
        "error_type",
        "fields_json",
        "values_json",
    ]

    def get_queryset(self, request):
        """Return the queryset with related parser context eager loaded."""
        return super().get_queryset(request).select_related("file", "file__stt")


class ParserErrorInline(admin.TabularInline):
    """Inline model for ParserError objects."""

    model = models.ParserError


class DataFileSummaryAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """ModelAdmin class for DataFileSummary objects generated in parsing."""

    list_display = ["status", "case_aggregates", "datafile"]


class ShadowDataFileSummaryAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """ModelAdmin class for DataFileSummary objects generated in parsing."""

    model = models.ShadowDataFileSummary
    list_display = ["status", "case_aggregates", "datafile"]


class ParseExecutionLogAdmin(BaseLogAdmin):
    """ModelAdmin class for ParseExecutionLog objects."""

    list_display = [
        "created_at",
        "data_file_id",
        "status",
        "parser_class",
        "execution_duration_ms",
        "total_records_processed",
        "total_errors_generated",
        "reparse_meta_id",
    ]
    list_filter = [
        "status",
        "parser_class",
        "reparse_meta_id",
        "created_at",
    ]
    search_fields = [
        "object_id",
        "note",
        "parser_class",
    ]


class ParseExecutionLogInline(GenericTabularInline):
    """Read-only inline for ParseExecutionLog history."""

    model = models.ParseExecutionLog
    ct_field = "content_type"
    ct_fk_field = "object_id"
    fields = [
        "created_at",
        "status",
        "parser_class",
        "execution_duration_ms",
        "total_records_processed",
        "total_errors_generated",
        "reparse_meta_id",
        "note",
    ]
    readonly_fields = fields
    extra = 0
    can_delete = False
    ordering = ["-created_at", "-id"]
    show_change_link = False

    def has_view_permission(self, request, obj=None):
        """Allow viewing execution records from the parent DataFile admin page."""
        return True

    def has_add_permission(self, request, obj=None):
        """Prevent creating execution records from admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent editing execution records from admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deleting execution records from admin."""
        return False


admin.site.register(models.ParserError, ParserErrorAdmin)
admin.site.register(models.DataFileSummary, DataFileSummaryAdmin)
admin.site.register(models.ShadowDataFileSummary, ShadowDataFileSummaryAdmin)
admin.site.register(models.ParseExecutionLog, ParseExecutionLogAdmin)
