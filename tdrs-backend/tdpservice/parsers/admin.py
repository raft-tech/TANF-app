"""Django admin customizations for the parser models."""
from django.contrib import admin
from . import models


# Register your models here.
class ParserErrorAdmin(admin.ModelAdmin):
    """ModelAdmin class for ParserError objects generated in parsing."""

    list_display = [
        'row_number',
        'field_name',
        'error_type',
        'error_message',
    ]
    
    def get_queryset(self, request):
        """Override the queryset to include the related datafile."""
        queryset = super().get_queryset(request).only('row_number', 'field_name', 'error_type', 'error_message',)
        print('__________________', queryset.explain())
        return queryset

class DataFileSummaryAdmin(admin.ModelAdmin):
    """ModelAdmin class for DataFileSummary objects generated in parsing."""

    list_display = ['status', 'case_aggregates', 'datafile']


admin.site.register(models.ParserError, ParserErrorAdmin)
admin.site.register(models.DataFileSummary, DataFileSummaryAdmin)
