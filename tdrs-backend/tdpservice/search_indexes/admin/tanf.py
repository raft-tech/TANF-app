"""ModelAdmin classes for parsed TANF data files."""
from django.contrib import admin
from .filters import CreationDateFilter, FiscalPeriodFilter, STTFilter
from .mixins import DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin, AdminModelMixin


class TANF_T1Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed T1 data files."""

    actions = ["export_as_csv"]

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'COUNTY_FIPS_CODE',
        'ZIP_CODE',
        'STRATUM',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR',
        'ZIP_CODE',
        'STRATUM',
    ]


class TANF_T2Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed T2 data files."""

    actions = ["export_as_csv"]

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR',
    ]


class TANF_T3Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed T3 data files."""

    actions = ["export_as_csv"]

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR',
    ]


class TANF_T4Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed T4 data files."""

    actions = ["export_as_csv"]

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR',
    ]


class TANF_T5Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed T5 data files."""

    actions = ["export_as_csv"]

    list_display = [
        'RecordType',
        'RPT_MONTH_YEAR',
        'CASE_NUMBER',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR',
    ]


class TANF_T6Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed T6 data files."""

    actions = ["export_as_csv"]

    list_display = [
        'RecordType',
        'CALENDAR_QUARTER',
        'RPT_MONTH_YEAR',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        'CALENDAR_QUARTER',
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR'
    ]


class TANF_T7Admin(DisableDeleteActionMixin, ExportCsvMixin, SttCodeMixin):
    """ModelAdmin class for parsed T7 data files."""

    actions = ["export_as_csv"]

    list_display = [
        'RecordType',
        'CALENDAR_QUARTER',
        'RPT_MONTH_YEAR',
        'TDRS_SECTION_IND',
        'STRATUM',
        'FAMILIES_MONTH',
        'datafile',
        'stt_code',
    ]

    list_filter = [
        'CALENDAR_QUARTER',
        FiscalPeriodFilter,
        CreationDateFilter,
        STTFilter,
        'RPT_MONTH_YEAR',
    ]
