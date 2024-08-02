"""ModelAdmin classes for parsed SSP data files."""
from .mixins import ReadOnlyAdminMixin


class ReparseMetaAdmin(ReadOnlyAdminMixin):
    """ModelAdmin class for parsed M1 data files."""

    list_display = [
        'created_at',
        'finished',
        'db_backup_location',
    ]

    list_filter = [
        'finished'
    ]
