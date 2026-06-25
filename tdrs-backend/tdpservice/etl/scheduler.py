"""Scheduling helpers for ETL pipelines."""

from datetime import date

from django.utils import timezone

from tdpservice.etl.models import ETLPipelineRun
from tdpservice.etl.runner import ActivePipelineRunError, create_pipeline_run


def fiscal_year_for_date(value: date) -> int:
    """Return the federal fiscal year for a date."""
    return value.year + 1 if value.month >= 10 else value.year


def is_first_workday(value: date) -> bool:
    """Return whether a date is the first Monday-Friday workday of its month."""
    if value.weekday() >= 5:
        return False

    prior_day = 1
    while prior_day < value.day:
        if date(value.year, value.month, prior_day).weekday() < 5:
            return False
        prior_day += 1

    return True


def schedule_statistical_weights_run(
    today: date | None = None,
) -> ETLPipelineRun | None:
    """Create a scheduled statistical weights run when due."""
    today = today or timezone.localdate()
    if not is_first_workday(today):
        return None

    fiscal_year = fiscal_year_for_date(today)
    output_scope = {
        "pipeline": "tanf_statistical_weights",
        "fiscal_year": fiscal_year,
        "program": "TANF",
        "section": "1",
    }
    already_scheduled = ETLPipelineRun.objects.filter(
        pipeline_key="tanf_statistical_weights",
        output_scope=output_scope,
        trigger_source=ETLPipelineRun.TriggerSource.SCHEDULED,
        status__in=[
            ETLPipelineRun.Status.PENDING,
            ETLPipelineRun.Status.RUNNING,
            ETLPipelineRun.Status.SUCCEEDED,
        ],
        created_at__year=today.year,
        created_at__month=today.month,
    ).exists()
    if already_scheduled:
        return None

    try:
        return create_pipeline_run(
            pipeline_key="tanf_statistical_weights",
            parameters={"fiscal_year": fiscal_year},
            trigger_source=ETLPipelineRun.TriggerSource.SCHEDULED,
        )
    except ActivePipelineRunError:
        return None
