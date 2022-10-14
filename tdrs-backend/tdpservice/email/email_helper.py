"""Helper methods for email.py."""
from tdpservice.email.email_enums import EmailType
from tdpservice.email.email import automated_email

from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)

def send_deactivation_warning_email(users, days):
    """Send an email to users that are about to be deactivated."""
    template_path = EmailType.DEACTIVATION_WARNING.value
    text_message = f'Your account will be deactivated in {days} days.'
    subject = f'Account Deactivation Warning: {days} days remaining'
    deactivation_date = datetime.now(timezone.utc) + timedelta(days=days)

    for user in users:
        recipient_email = user.email
        context = {
            'first_name': user.first_name,
            'days': days,
            'deactivation_date': deactivation_date
        }

        automated_email.delay(
            email_path=template_path,
            recipient_email=recipient_email,
            subject=subject,
            email_context=context,
            text_message=text_message
        )

def send_approval_status_update_email(
    new_approval_status,
    recipient_email,
    context
):
    """Send an email to a user when their account approval status is updated."""
    from tdpservice.users.models import AccountApprovalStatusChoices

    template_path = None
    subject = None
    text_message = None
    logger.info(f"Preparing email to {recipient_email} with status {new_approval_status}")
    match new_approval_status:
        case AccountApprovalStatusChoices.INITIAL:
            print("initial")
            return

        case AccountApprovalStatusChoices.ACCESS_REQUEST:
            template_path = EmailType.ACCESS_REQUEST_SUBMITTED.value
            subject = 'Access Request Submitted'
            text_message = 'Your account has been requested.'

        case AccountApprovalStatusChoices.PENDING:
            print("pending")
            return

        case AccountApprovalStatusChoices.APPROVED:
            template_path = EmailType.REQUEST_APPROVED.value
            subject = 'Access Request Approved'
            text_message = 'Your account request has been approved.'

        case AccountApprovalStatusChoices.DENIED:

            template_path = EmailType.REQUEST_DENIED.value
            subject = 'Access Request Denied'
            text_message = 'Your account request has been denied.'

        case AccountApprovalStatusChoices.DEACTIVATED:
            template_path = EmailType.ACCOUNT_DEACTIVATED.value
            subject = 'Account is Deactivated'
            text_message = 'Your account has been deactivated.'

    context.update({'subject': subject})

    automated_email.delay(
        email_path=template_path,
        recipient_email=recipient_email,
        subject=subject,
        email_context=context,
        text_message=text_message
    )

def send_data_submitted_email(recipients, context):
    """Send an email to a user when their data has been submitted."""
    template_path = EmailType.DATA_SUBMITTED.value
    subject = 'Data Submitted'
    text_message = 'Your data has been submitted.'

    print('fmltt')

    automated_email.delay(
        email_path=template_path,
        recipient_email=recipients,
        subject=subject,
        email_context=context,
        text_message=text_message
    )
