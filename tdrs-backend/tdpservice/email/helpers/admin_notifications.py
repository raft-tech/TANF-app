"""helper functions to administer user accounts."""

def email_admin_deactivated_user(user):
    """Send an email to OFA Admins when a user is deactivated."""
    from tdpservice.users.models import User
    from tdpservice.email.email_enums import EmailType
    from tdpservice.email.email import automated_email, log
    from tdpservice.email.tasks import get_ofa_admin_user_emails, get_system_owner_email

    recipient_emails = get_ofa_admin_user_emails()
    logger_context = {
        'user_id': user.id,
        'object_id': user.id,
        'object_repr': user.username,
        'content_type': User,
    }

    template_path = EmailType.ACCOUNT_DEACTIVATED_ADMIN.value
    text_message = 'A user account has been deactivated.'
    subject = ' TDP User Account Deactivated due to Inactivity'
    context = {
        'user': user,
    }

    log(f"Preparing email to OFA Admins for deactivated user {user.username}", logger_context=logger_context)

    for recipient_email in recipient_emails:
        automated_email(
            email_path=template_path,
            recipient_email=recipient_email,
            subject=subject,
            email_context=context,
            text_message=text_message,
            logger_context=logger_context
        )

def email_system_owner_system_admin_role_change(user):
    """Send an email to the System Owner when a user is assigned or removed from the System Admin role."""
    from tdpservice.users.models import User
    from tdpservice.email.email_enums import EmailType
    from tdpservice.email.email import automated_email, log
    from tdpservice.email.tasks import get_ofa_admin_user_emails, get_system_owner_email
    recipient_email = get_system_owner_email()
    logger_context = {
        'user_id': user.id,
        'object_id': user.id,
        'object_repr': user.username,
        'content_type': User,
    }

    template_path = EmailType.SYSTEM_ADMIN_ROLE_CHANGED.value
    text_message = 'A user has been assigned or removed from the System Admin role.'
    subject = 'TDP User Role Change: System Admin'
    context = {
        'user': user,
    }

    log(f"Preparing email to System Owner for System Admin role change for user {user.username}", logger_context=logger_context)

    automated_email(
        email_path=template_path,
        recipient_email=recipient_email,
        subject=subject,
        email_context=context,
        text_message=text_message,
        logger_context=logger_context
    )