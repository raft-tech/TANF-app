"""Filters for the User admin interface."""

from django.contrib import admin
from tdpservice.users.models import AccountApprovalStatusChoices


class ActiveStatusListFilter(admin.SimpleListFilter):
    """Filter to show active or inactive users."""

    title = "activation status"
    parameter_name = "active_status"

    def lookups(self, request, model_admin):
        """Define the filter options."""
        return (("inactive", "Unhide Inactive Users"),)

    def queryset(self, request, queryset):
        """Filter the queryset based on the selected value."""
        value = self.value()
        if value == "inactive":
            return queryset.filter(
                account_approval_status=AccountApprovalStatusChoices.DEACTIVATED
            )
        return queryset

    def choices(self, changelist):
        """Generate the choices for the filter, modifying the All display text."""
        for choice in super().choices(changelist):
            if choice["display"] == "All":
                choice["display"] = "All Active Users"
            yield choice
