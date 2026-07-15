"""Add STTs and Regions to Django Admin."""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from ..core.utils import ReadOnlyAdminMixin
from .models import Program, STT, Region, Section, SttProgramParticipation


@admin.register(STT)
class STTAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for STT models."""

    search_fields = ["name", "stt_code"]

    list_display = [
        "id",
        "type",
        "postal_code",
        "name",
        "region",
        "filenames",
        "stt_code",
        "has_state",
        "ssp",
        "sample",
    ]

    def has_state(self, obj):
        """If Type is tribe do not show state."""
        if obj.type == "tribe":
            return obj.state
        return None

    has_state.short_description = "State"
    has_state.admin_order_field = "state"


@admin.register(Region)
class RegionAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for STT models."""

    list_display = [field.name for field in Region._meta.fields]


class SectionInline(admin.TabularInline):
    """Read-only inline for sections associated with a program."""

    model = Section
    fields = ["section_link"]
    readonly_fields = ["section_link"]
    extra = 0
    can_delete = False

    def section_link(self, obj):
        """Link to the section admin detail page."""
        url = reverse("admin:stts_section_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.name)

    section_link.short_description = "Name"

    def has_add_permission(self, request, obj=None):
        """Prevent adding sections from the Program admin page."""
        return False


@admin.register(Program)
class ProgramAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for Program models."""

    search_fields = ["slug", "name"]
    list_display = ["id", "slug", "name"]
    inlines = [SectionInline]


@admin.register(Section)
class SectionAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for Section models."""

    search_fields = ["name", "program__slug", "program__name"]
    list_display = ["id", "program", "name"]
    list_select_related = ["program"]


@admin.register(SttProgramParticipation)
class SttProgramParticipationAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """Read-only Admin class for SttProgramParticipation models."""

    search_fields = ["stt__name", "stt__stt_code", "program__slug", "program__name"]
    list_display = ["id", "stt", "program", "status"]
    list_filter = ["program", "status"]
    list_select_related = ["stt", "program"]
