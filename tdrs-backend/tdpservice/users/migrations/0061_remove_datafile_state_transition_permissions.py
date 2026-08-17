"""Keep audit-table permissions out of the OFA System Admin role matrix."""

from django.db import migrations


DEFAULT_ACTIONS = ("add", "change", "view")
AUDIT_MODEL = "datafilestatetransition"


def audit_permission_ids(apps):
    """Return DataFileStateTransition add/change/view permission ids."""
    permission_model = apps.get_model("auth", "Permission")
    return list(
        permission_model.objects.filter(
            content_type__app_label="data_files",
            content_type__model=AUDIT_MODEL,
            codename__in=[
                f"{action}_{AUDIT_MODEL}" for action in DEFAULT_ACTIONS
            ],
        ).values_list("id", flat=True)
    )


def remove_audit_permissions(apps, schema_editor):
    """Remove audit-table permissions added by fresh-DB migration ordering."""
    group, _ = apps.get_model("auth", "Group").objects.get_or_create(
        name="OFA System Admin"
    )
    group.permissions.remove(*audit_permission_ids(apps))


def restore_audit_permissions(apps, schema_editor):
    """Restore removed permissions if the migration is rolled back."""
    group, _ = apps.get_model("auth", "Group").objects.get_or_create(
        name="OFA System Admin"
    )
    group.permissions.add(*audit_permission_ids(apps))


class Migration(migrations.Migration):

    dependencies = [
        ("data_files", "0032_datafilestatetransition"),
        ("users", "0060_add_program_section_permissions"),
    ]

    operations = [
        migrations.RunPython(
            remove_audit_permissions,
            reverse_code=restore_audit_permissions,
        ),
    ]
