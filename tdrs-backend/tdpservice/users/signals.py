"""Signals for the users app."""
import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from tdpservice.email.helpers.admin_notifications import (
    email_system_owner_system_admin_role_change,
)
from tdpservice.users.models import User

logger = logging.getLogger()


@receiver(pre_save, sender=User)
def user_is_staff_superuser_changed(sender, instance, **kwargs):
    """Send an email to the System Owner when a user is assigned or removed from the System Admin role."""
    # first get instance from db for existing state
    try:
        current_user_state = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return

    # check if is_staff is assigned
    if instance.is_staff and not current_user_state.is_staff:
        email_system_owner_system_admin_role_change(instance, "is_staff_assigned")
    # check if is_staff is removed
    elif not instance.is_staff and current_user_state.is_staff:
        email_system_owner_system_admin_role_change(instance, "is_staff_removed")
    # check if is_superuser is assigned
    if instance.is_superuser and not current_user_state.is_superuser:
        email_system_owner_system_admin_role_change(instance, "is_superuser_assigned")
    # check if is_superuser is removed
    elif not instance.is_superuser and current_user_state.is_superuser:
        email_system_owner_system_admin_role_change(instance, "is_superuser_removed")


@receiver(post_save, sender=User)
def user_is_staff_superuser_created(sender, instance, created, **kwargs):
    """Send an email to the System Owner when a user is assigned or removed from the System Admin role."""
    if created:
        if instance.is_staff:
            email_system_owner_system_admin_role_change(instance, "is_staff_assigned")
        if instance.is_superuser:
            email_system_owner_system_admin_role_change(
                instance, "is_superuser_assigned"
            )
