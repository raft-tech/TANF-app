"""Set permissions for users."""

from rest_framework import permissions
from django.contrib.auth.models import Group

def is_in_group(user, group_name):
    """
    Takes a user and a group name, and returns `True` if the user is in that group.
    """
    try:
        return Group.objects.get(name=group_name).user_set.filter(id=user.id).exists()
    except Group.DoesNotExist:
        return None

# Is Owner or admin?
class IsUserOrAdmin(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        """Check if user has required permissions."""
        return obj == request.user or (
            request.user.is_authenticated and request.user.is_admin
        )


class IsAdmin(permissions.BasePermission):
    """Permission for admin-only views."""

    def has_permission(self, request, view):
        """Check if a user is admin or superuser."""
        return request.user.is_authenticated and request.user.is_admin
