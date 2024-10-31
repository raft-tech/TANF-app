from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from tdpservice.users.models import User
from django.contrib.auth.models import Group
from tdpservice.email.helpers.admin_notifications import email_system_owner_system_admin_role_change

import logging
logger = logging.getLogger()

@receiver(m2m_changed, sender=User.groups.through)
def user_group_changed(sender, instance, action, pk_set, **kwargs):
    ADMIN_GROUP_PK = Group.objects.get(name="OFA System Admin").pk
    ACTIONS = {
        'PRE_REMOVE' : 'pre_remove',
        'PRE_ADD' : 'pre_add',
    }
    group_change_list = [pk for pk in pk_set]
    if ADMIN_GROUP_PK in group_change_list and action == ACTIONS['PRE_ADD']:
        # EMAIL ADMIN GROUP ADDED to OFA ADMIN
        email_system_owner_system_admin_role_change(instance)
    elif ADMIN_GROUP_PK in group_change_list and action == ACTIONS['PRE_REMOVE']:
        # EMAIL ADMIN GROUP REMOVED from OFA ADMIN
        email_system_owner_system_admin_role_change(instance)
