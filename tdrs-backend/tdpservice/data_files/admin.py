"""Admin class for DataFile objects."""
from django.contrib import admin

from ..core.utils import ReadOnlyAdminMixin
from .models import DataFile, LegacyFileTransfer
from tdpservice.parsers.models import DataFileSummary

class DataFileSummaryStatusFilter(admin.SimpleListFilter):
    """Admin class filter for file status (accepted, rejected) for datafile model"""

    title = 'status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        """Return a list of tuples."""
        return [
            ('Accepted', 'Accepted'),
            ('Rejected', 'Rejected'),
        ]
    
    def queryset(self, request, queryset):
        """Return a queryset."""
        if self.value():
            return queryset.filter(datafilesummary__status=self.value())
        else:
            return queryset


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
            return queryset.filter(prog_type=self.value())
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
    

    list_display = [
        'id',
        'stt',
        'year',
        'quarter',
        'section',
        'version',
        'status',
        'case_totals',
    ]

    list_filter = [
        'quarter',
        'section',
        'stt',
        'user',
        'year',
        'version',
        DataFileSummaryStatusFilter,
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
