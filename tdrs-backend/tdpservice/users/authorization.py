"""Shared user authorization helpers."""


def is_authorized_admin_user(user):
    """Return whether a user may access the admin console."""
    return (
        getattr(user, "is_active", False)
        and getattr(user, "is_staff", False)
        and getattr(user, "is_superuser", False)
    )
