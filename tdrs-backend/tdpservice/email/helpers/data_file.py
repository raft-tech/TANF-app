"""Helper functions for sending data file submission emails."""
from tdpservice.email.email_enums import EmailType
from tdpservice.email.email import automated_email, log
from tdpservice.users.models import User, AccountApprovalStatusChoices
from django.contrib.auth.models import Group

def send_data_submitted_email(recipients, data_file, context, subject):
    """Send an email to a user when their data has been submitted."""
    template_path = EmailType.DATA_SUBMITTED.value
    text_message = 'Your data has been submitted.'

    logger_context = {
        'user_id': data_file.user.id,
        'object_id': data_file.id,
        'object_repr': f"Uploaded data file for quarter: {data_file.fiscal_year}"
    }

    log(f'Data file submitted; emailing Data Analysts {recipients}', logger_context=logger_context)

    automated_email(
        email_path=template_path,
        recipient_email=recipients,
        subject=subject,
        email_context=context,
        text_message=text_message
    )

def send_data_processed_email(data_file, status):
    """Send an email to a user when their data has been processed."""
    template_path = EmailType.DATA_PROCESSED.value  # this is some copilot junk?
    text_message = 'Your data has been processed.'

    # send new email to user with parsing results
    # might need try/catch here.
    subject = f"Data Processed for {data_file.section}"

    context = {
        'stt_name': str(data_file.stt),
        'submission_date': data_file.created_at,
        'submitted_by': data_file.user.get_full_name(),
        'fiscal_year': data_file.fiscal_year,
        'section_name': data_file.section,
        'subject': subject,
        'status': "No Errors" if status == "Accepted" else "Error Report Available"  # we can ignore "Pending"
    }

    recipients = User.objects.filter(
        stt=data_file.stt,
        account_approval_status=AccountApprovalStatusChoices.APPROVED,
        groups=Group.objects.get(name='Data Analyst')
    ).values_list('username', flat=True).distinct()

    # we need dfs.status,
    logger_context = {
        'user_id': data_file.user.id,
        'object_id': data_file.id,
        'object_repr': f"Uploaded data file for quarter: {data_file.fiscal_year}"
    }
    if len(recipients) > 0:
        # throw err
        log(f'No Data Analysts found for STT: {data_file.stt} to send email to.', logger_context=logger_context)
        return
    else:
        log(f'Data file processed; emailing Data Analysts {recipients}', logger_context=logger_context)

    automated_email(
        email_path=template_path,
        recipient_email=recipients,
        subject=subject,
        email_context=context,
        text_message=text_message
    )
