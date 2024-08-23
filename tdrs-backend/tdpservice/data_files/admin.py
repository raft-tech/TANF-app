"""Admin class for DataFile objects."""
from django.contrib import admin

from ..core.utils import ReadOnlyAdminMixin
from .models import DataFile, LegacyFileTransfer
from tdpservice.parsers.models import DataFileSummary, ParserError
from django.conf import settings
from django.utils.html import format_html

DOMAIN = settings.FRONTEND_BASE_URL

class DataFileSummaryPrgTypeFilter(admin.SimpleListFilter):
    """Admin class filter for Program Type on datafile model."""

    title = 'Program Type'
    parameter_name = 'program_type'

    def lookups(self, request, model_admin):
        """Return a list of tuples."""
        return [
            ('TAN', 'TAN'),
            ('SSP', 'SSP'),
        ]

    def queryset(self, request, queryset):
        """Return a queryset."""
        if self.value():
            query_set_ids = [df.id for df in queryset if df.prog_type == self.value()]
            return queryset.filter(id__in=query_set_ids)
        else:
            return queryset

@admin.register(DataFile)
class DataFileAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin class for DataFile models."""

    def status(self, obj):
        """Return the status of the data file summary."""
        return DataFileSummary.objects.get(datafile=obj).status

    def case_totals(self, obj):
        """Return the case totals."""
        return DataFileSummary.objects.get(datafile=obj).case_aggregates

    def error_report_link(self, obj):
        """Return the link to the error report."""
        pe_len = ParserError.objects.filter(file=obj).count()

        filtered_parserror_list_url = f'{DOMAIN}/admin/parsers/parsererror/?file=' + str(obj.id)
        # have to find the error id from obj
        return format_html("<a href='{url}'>{field}</a>",
                           field="Parser Errors: " + str(pe_len),
                           url=filtered_parserror_list_url)

    error_report_link.allow_tags = True

    def data_file_summary(self, obj):
        """Return the data file summary."""
        df = DataFileSummary.objects.get(datafile=obj)
        return format_html("<a href='{url}'>{field}</a>",
                           field=f'{df.id}' + ":" + df.get_status(),
                           url=f"{DOMAIN}/admin/parsers/datafilesummary/{df.id}/change/")

    class by_submission_date(admin.SimpleListFilter):
        """filter data files by month."""

        title = 'Submission Date'
        parameter_name = 'Submission Day/Month/Year'

        def lookups(self, request, model_admin):
            """Return a list of tuples."""
            return [
                ('1', 'Yesterday'),
                ('0', 'Today'),
                ('7', 'Past 7 days'),
                ('30', 'This month'),
                ('365', 'This year'),
            ]

        def queryset(self, request, queryset):
            """Return a queryset."""
            from datetime import datetime, timedelta, timezone
            yesterday = (datetime.now(tz=timezone.utc) - timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
                )
            this_month = datetime.now(tz=timezone.utc).replace(day=1)
            this_year = datetime.now(tz=timezone.utc).replace(month=1, day=1)
            if self.value() == '1':
                query_set_ids = [df.id for df in queryset if df.created_at.replace(
                    hour=0, minute=0, second=0, microsecond=0
                    ) == yesterday]
                return queryset.filter(id__in=query_set_ids)
            elif self.value() in ['0', '7']:
                last_login__lte = datetime.now(tz=timezone.utc) - timedelta(days=int(self.value()))
                query_set_ids = [df.id for df in queryset if df.created_at >= last_login__lte]
                return queryset.filter(id__in=query_set_ids)
            elif self.value() == '30':
                query_set_ids = [df.id for df in queryset if df.created_at >= this_month]
                return queryset.filter(id__in=query_set_ids)
            elif self.value() == '365':
                query_set_ids = [df.id for df in queryset if df.created_at >= this_year]
                return queryset.filter(id__in=query_set_ids)
            else:
                return queryset

    list_display = [
        'id',
        'stt',
        'year',
        'quarter',
        'section',
        'version',
        'data_file_summary',
        'error_report_link',
    ]

    list_filter = [
        'quarter',
        'section',
        'stt',
        'user',
        'year',
        by_submission_date,
        'version',
        'summary__status',
        DataFileSummaryPrgTypeFilter
    ]

@admin.register(LegacyFileTransfer)
class LegacyFileTransferAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Admin class for LegacyFileTransfer models."""

    list_display = [
        'id',
        'sent_at',
        'result',
        'uploaded_by',
        'file_name',
        'file_shasum',
    ]

    list_filter = [
        'sent_at',
        'result',
        'uploaded_by',
        'file_name',
        'file_shasum',
    ]
