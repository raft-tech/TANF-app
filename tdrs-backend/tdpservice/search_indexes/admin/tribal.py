"""ModelAdmin classes for parsed TRIBAL data files."""
from django.contrib import admin
from .filter import CreationDateFilter


class Tribal_TANF_T1Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed Tribal_T1 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'COUNTY_FIPS_CODE',
        'ZIP_CODE',
        'STRATUM',
        'datafile',
    ]

    list_filter = [
        CreationDateFilter,
        'RPT_MONTH_YEAR',
        'ZIP_CODE',
        'STRATUM',
    ]


class Tribal_TANF_T2Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed Tribal_T2 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
    ]

    list_filter = [
        CreationDateFilter,
        'RPT_MONTH_YEAR',
    ]


class Tribal_TANF_T3Admin(admin.ModelAdmin):
    """ModelAdmin class for parsed Tribal_T3 data files."""

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
    ]

    list_filter = [
        CreationDateFilter,
        'RPT_MONTH_YEAR',
    ]
