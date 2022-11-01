"""Add STTs and Regions to Django Admin."""

from django.contrib import admin
from .models import STT, Region
from ..core.utils import ReadOnlyAdminMixin


@admin.register(STT)
class STTAdmin(admin.ModelAdmin):
    """Read-only Admin class for STT models."""

    readonly_fields = ['type', 'code', 'code_number', 'name', 'region', 'filenames', 'stt_code', 'state']
    list_display = [field.name for field in STT._meta.fields]


@admin.register(Region)
class RegionAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for STT models."""

    list_display = [field.name for field in Region._meta.fields]
