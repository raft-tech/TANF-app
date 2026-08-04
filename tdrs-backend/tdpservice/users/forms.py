"""Forms for the user admin."""

from typing import Any

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.models import ModelChoiceIteratorValue
from django.forms.utils import ErrorDict

from tdpservice.users.constants import REGIONAL_ROLES
from tdpservice.users.models import Region, User


USER_ADMIN_WORKFLOW_FIELDS = [
    "username",
    "first_name",
    "last_name",
    "account_approval_status",
    "groups",
    "stt",
    "regions",
]


class UserForm(forms.ModelForm):
    """Customize the user admin form."""

    regions = forms.ModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple("Regions", is_stacked=False),
    )

    class Meta:
        """Define customizations."""

        model = User
        exclude = ["password"]
        readonly_fields = [
            "last_login",
            "date_joined",
            "login_gov_uuid",
            "hhs_id",
            "access_request",
        ]

    class Media:
        """Include custom js for toggling regions based on roles."""

        js = ("admin/js/user_form_region_toggle.js",)

    def clean(self):
        """Add extra validation for locations based on roles."""

        cleaned_data = super().clean()

        groups = cleaned_data.get("groups", [])
        regions = cleaned_data.get("regions", [])
        stt = cleaned_data.get("stt")

        if len(groups) > 1:
            raise ValidationError("User should not have multiple groups.")

        # Check if the user belongs to any regional group
        has_regional_role = any(g.name in REGIONAL_ROLES for g in groups)

        if has_regional_role and not (regions or stt):
            raise ValidationError(
                "Users in regional roles must have at least one region or location assigned."
            )

        if regions and stt:
            raise ValidationError(
                "A user may only have a Region or STT assigned, not both."
            )

        if not has_regional_role and regions:
            raise ValidationError(
                "Users without regional roles should not be assigned regions."
            )

        return cleaned_data

    def clean_groups(self):
        """Ensure only one group is assigned."""
        groups = self.cleaned_data.get("groups", [])
        if len(groups) > 1:
            raise ValidationError("User should not have multiple groups")

        return groups

    def clean_feature_flags(self):
        """Ensure only one feature flag is assigned."""
        feature_flags = self.cleaned_data.get("feature_flags", {})

        if not feature_flags:
            feature_flags = {}

        return feature_flags


class UserAdminWorkflowForm(UserForm):
    """Constrained user admin form used by the React admin console."""

    class Meta:
        """Expose only the first migrated admin workflow fields."""

        model = User
        fields = USER_ADMIN_WORKFLOW_FIELDS
        labels = {
            "account_approval_status": "Account approval status",
            "stt": "STT",
        }


def _field_type(field: forms.Field) -> str:
    """Return a frontend-friendly field type for a Django form field."""
    if isinstance(field, (forms.ModelMultipleChoiceField, forms.MultipleChoiceField)):
        return "multiselect"
    if isinstance(field, (forms.ModelChoiceField, forms.ChoiceField)):
        return "select"
    if isinstance(field, forms.BooleanField):
        return "checkbox"
    if isinstance(field, forms.EmailField):
        return "email"
    if isinstance(field, forms.IntegerField):
        return "number"
    if isinstance(field.widget, forms.Textarea):
        return "textarea"
    return "text"


def _choice_value(value: Any) -> str:
    """Serialize a Django choice value for browser form controls."""
    if isinstance(value, ModelChoiceIteratorValue):
        value = value.value
    if value is None:
        return ""
    return str(value)


def _field_choices(field: forms.Field) -> list[dict[str, str]]:
    """Serialize Django field choices."""
    choices = getattr(field, "choices", None)
    if choices is None:
        return []

    serialized_choices = []
    for value, label in choices:
        if isinstance(label, (list, tuple)):
            for nested_value, nested_label in label:
                serialized_choices.append(
                    {"value": _choice_value(nested_value), "label": str(nested_label)}
                )
            continue

        serialized_choices.append({"value": _choice_value(value), "label": str(label)})

    return serialized_choices


def _serialize_initial_value(field: forms.Field, value: Any) -> Any:
    """Serialize a Django initial value for JSON metadata."""
    if isinstance(field, (forms.ModelMultipleChoiceField, forms.MultipleChoiceField)):
        if value in (None, ""):
            return []
        if isinstance(value, QuerySet):
            value = list(value)
        if not isinstance(value, (list, tuple, set)):
            value = [value]
        return [_choice_value(getattr(item, "pk", item)) for item in value]

    if isinstance(field, forms.ModelChoiceField):
        if value in (None, ""):
            return None
        return _choice_value(getattr(value, "pk", value))

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return value


def _field_constraints(field: forms.Field) -> dict[str, Any]:
    """Return generic constraints supported by the React admin form."""
    constraints = {}
    for attr_name in ["max_length", "min_length", "max_value", "min_value"]:
        value = getattr(field, attr_name, None)
        if value is not None:
            constraints[attr_name] = value

    pattern = field.widget.attrs.get("pattern")
    if pattern:
        constraints["pattern"] = pattern

    return constraints


def build_user_admin_form_metadata(
    form: UserAdminWorkflowForm, user: User
) -> dict[str, Any]:
    """Build React admin metadata from the Django user admin workflow form."""
    fields = []
    for field_name, field in form.fields.items():
        fields.append(
            {
                "name": field_name,
                "label": str(field.label or field_name.replace("_", " ").title()),
                "type": _field_type(field),
                "required": field.required,
                "help_text": str(field.help_text or ""),
                "initial": _serialize_initial_value(field, form[field_name].value()),
                "choices": _field_choices(field),
                "constraints": _field_constraints(field),
            }
        )

    return {
        "workflow": "users.user.change",
        "title": "Edit user",
        "object": {"id": str(user.pk), "label": str(user)},
        "submit_url": f"/users/{user.pk}/admin-form/",
        "fields": fields,
    }


def normalize_form_errors(errors: ErrorDict) -> dict[str, Any]:
    """Return normalized field and non-field errors from a Django form."""
    field_errors = {}
    non_field_errors = []

    for field_name, error_list in errors.as_data().items():
        messages = [
            str(message)
            for validation_error in error_list
            for message in validation_error.messages
        ]

        if field_name == NON_FIELD_ERRORS:
            non_field_errors.extend(messages)
        else:
            field_errors[field_name] = messages

    return {
        "field_errors": field_errors,
        "non_field_errors": non_field_errors,
    }
