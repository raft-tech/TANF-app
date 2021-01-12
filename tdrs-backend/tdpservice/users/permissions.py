"""Set permissions for users."""

from rest_framework import permissions
from django.contrib.auth.models import Group


def is_in_group(user, group_name):
    """Take a user and a group name, and returns `True` if the user is in that group."""
    try:
        return Group.objects.get(name=group_name).user_set.filter(id=user.id).exists()
    except Group.DoesNotExist:
        return None

class IsUser(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        """Check if user has required permissions."""
        return obj == request.user


class IsAdmin(permissions.BasePermission):
    """Permission for admin-only views."""

    def has_object_permission(self, request, view, obj):
        """Check if a user is admin or superuser."""
        return request.user.is_authenticated and request.user.is_admin

    def has_permission(self, request, view):
        """Check if a user is admin or superuser."""
        return request.user.is_authenticated and request.user.is_admin


class IsOFAAnalyst(permissions.BasePermission):
    """Permission for OFA Analyst only views."""

    def has_permission(self, request, view):
        """Check if a user is a data analyst."""
        return is_in_group(request.user, "OFA Analyst")


class IsOFAAdmin(permissions.BasePermission):
    """Permission for OFA Analyst only views."""

    def has_permission(self, request, view):
        """Check if a user is a OFA Admin."""
        return is_in_group(request.user, "OFA Admin")


class IsDataPrepper(permissions.BasePermission):
    """Permission for Data Prepper only views."""

    def has_permission(self, request, view):
        """Check if a user is a data prepper."""
        return is_in_group(request.user, "Data Prepper")


class IsOFA(permissions.BasePermission):
    """Permission for any member of OFA."""

    def has_permission(self, request, view):
        """Check if a user is a data prepper."""
        return is_in_group(request.user, "OFA Analyst") or is_in_group(
            request.user, "OFA Admin"
        )
