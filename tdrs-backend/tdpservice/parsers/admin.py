"""Django admin customizations for the parser models."""
from django.contrib import admin
from . import models
from django.utils.html import format_html
from django.conf import settings


# Register your models here.
class ParserErrorAdmin(admin.ModelAdmin):
    """ModelAdmin class for ParserError objects generated in parsing."""

    def log_file_s3_path(self, obj):
        """Generate S3 path for the log file."""
        datafile = obj.file if hasattr(obj, 'file') else None
        if not datafile:
            return None
        LOG_PRE_FIX = "v1/data_files/logs"
        DOMAIN = settings.FRONTEND_BASE_URL
        if datafile:
            link = f"{LOG_PRE_FIX}/{datafile.id}/{datafile.year}/{datafile.quarter}/" \
                  f"{datafile.stt}/{datafile.section}/{datafile.filename}"
            url = f"{DOMAIN}/{link}"  # Replace with your actual S3 URL
            return format_html("<a href='{url}'>{field}</a>",
                               field="Parser Errors",
                               url=url)
        else:
            return None

    list_display = [
        'row_number',
        'field_name',
        'error_type',
        'error_message',
        'log_file_s3_path'
    ]

    fields = [
        'file',
        'row_number',
        'column_number',
        'item_number',
        'field_name',
        'rpt_month_year',
        'case_number',
        'error_message',
        'error_type',
    ]


class ParserErrorInline(admin.TabularInline):
    """Inline model for ParserError objects."""

    model = models.ParserError


class DataFileSummaryAdmin(admin.ModelAdmin):
    """ModelAdmin class for DataFileSummary objects generated in parsing."""

    list_display = ['status', 'case_aggregates', 'datafile']


admin.site.register(models.ParserError, ParserErrorAdmin)
admin.site.register(models.DataFileSummary, DataFileSummaryAdmin)
