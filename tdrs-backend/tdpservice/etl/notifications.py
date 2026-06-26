"""Notification helpers for ETL pipelines."""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q

from tdpservice.etl.models import ETLPipelineRun
from tdpservice.users.models import AccountApprovalStatusChoices, User

logger = logging.getLogger(__name__)


def _operational_recipient_emails() -> list[str]:
    """Return approved operational recipients for ETL notifications."""
    return list(
        User.objects.filter(
            Q(groups__name="OFA System Admin") | Q(groups__name="DIGIT Team"),
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        .exclude(email="")
        .values_list("email", flat=True)
        .distinct()
    )


def _qa_summary_lines(pipeline_run: ETLPipelineRun) -> list[str]:
    """Return short QA summary lines for an ETL run."""
    return [
        f"- {result.check_key}: {result.status} - {result.summary}"
        for result in pipeline_run.qa_results.order_by("id")
    ]


def _run_detail_url(pipeline_run: ETLPipelineRun) -> str:
    """Return an API URL for ETL run details."""
    return f"{settings.BASE_URL}/etl/runs/{pipeline_run.id}/"


def _program_label(pipeline_run: ETLPipelineRun) -> str:
    """Return the statistical weights program label for a run."""
    return (
        pipeline_run.output_scope.get("program")
        or pipeline_run.parameters.get("program")
        or "unknown"
    )


def _statistical_weights_message(pipeline_run: ETLPipelineRun) -> str:
    """Return a plain-text statistical weights notification body."""
    program = _program_label(pipeline_run)
    output = pipeline_run.outputs.filter(output_key="statistical_weights").last()
    output_version = output.output_version if output else "unknown"
    row_count = output.row_count if output else 0
    run_status = ETLPipelineRun.Status.SUCCEEDED if output else pipeline_run.status
    qa_lines = _qa_summary_lines(pipeline_run)
    if not qa_lines:
        qa_lines = ["- No QA results recorded."]

    return "\n".join(
        [
            f"{program} Statistical Weights ETL run completed.",
            "",
            f"Pipeline: {program} Statistical Weights",
            f"Run ID: {pipeline_run.id}",
            f"Fiscal Year: {pipeline_run.parameters.get('fiscal_year')}",
            f"Program: {program}",
            f"Status: {run_status}",
            f"Trigger Source: {pipeline_run.trigger_source}",
            f"Output Version: {output_version}",
            f"Row Count: {row_count}",
            f"Run Detail: {_run_detail_url(pipeline_run)}",
            "",
            "QA Summary:",
            *qa_lines,
        ]
    )


def send_statistical_weights_notification(pipeline_run: ETLPipelineRun) -> dict:
    """Send the statistical weights run-completion notification."""
    recipients = _operational_recipient_emails()
    if not recipients:
        return {"notification": "no_recipients"}

    program = _program_label(pipeline_run)
    output = pipeline_run.outputs.filter(output_key="statistical_weights").last()
    run_status = ETLPipelineRun.Status.SUCCEEDED if output else pipeline_run.status
    subject = f"{program} Statistical Weights Run {pipeline_run.id} {run_status}"
    message = _statistical_weights_message(pipeline_run)

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipients,
            fail_silently=False,
        )
    except Exception as exc:
        logger.exception("Failed to send ETL notification email.")
        return {
            "notification": "failed",
            "error": str(exc),
            "recipients": recipients,
        }

    return {
        "notification": "sent",
        "recipient_count": len(recipients),
        "run_detail_url": _run_detail_url(pipeline_run),
    }
