"""Helpers for defining Django-managed parser shadow models."""

from django.db import models


def create_shadow_model(
    name,
    source_model,
    db_table,
    *,
    app_label=None,
    module=None,
    field_overrides=None,
    foreign_key_overrides=None,
    exclude_fields=None,
):
    """Create a managed shadow model with cloned fields from a source model."""
    field_overrides = field_overrides or {}
    foreign_key_overrides = foreign_key_overrides or {}
    exclude_fields = set(exclude_fields or ())

    attrs = {"__module__": module or source_model.__module__}

    for field in source_model._meta.local_fields:
        if field.name in exclude_fields:
            continue

        override = field_overrides.get(field.name)
        if override is not None:
            attrs[field.name] = override
            continue

        override = foreign_key_overrides.get(field.name)
        if override is not None:
            attrs[field.name] = override
            continue

        if field.is_relation:
            raise ValueError(
                f"Shadow model {name} must override relational field {field.name}"
            )

        attrs[field.name] = field.clone()

    for field_name, field in field_overrides.items():
        attrs.setdefault(field_name, field)

    meta_attrs = {
        "db_table": db_table,
        "managed": True,
    }
    if app_label:
        meta_attrs["app_label"] = app_label
    attrs["Meta"] = type("Meta", (), meta_attrs)

    return type(name, (models.Model,), attrs)
