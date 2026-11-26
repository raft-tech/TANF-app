"""Lifecycle orchestration, error reporting, summary updates, and metrics."""

import logging
from typing import Any, Optional

from django.conf import settings
from django.core.files import File
from django.db.models import Case, Count, IntegerField, When
from django.db.utils import DatabaseError

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.error_reports import ErrorReportFactory
from tdpservice.data_files.submission_lifecycle import (
    StaleParseOwnership,
    finish_reparse,
    record_parse_failure,
    record_parse_outcome,
    record_shadow_parse_state,
)
from tdpservice.email.helpers.data_file import send_data_submitted_email
from tdpservice.parsers.aggregates import (
    case_aggregates_by_month,
    fra_total_errors,
    total_errors_by_month,
)
from tdpservice.parsers.error_generator import (
    ErrorGeneratorArgs,
    ErrorGeneratorFactory,
    ErrorGeneratorType,
)
from tdpservice.parsers.models import (
    DataFileSummary,
    ParserError,
    ParserErrorCategoryChoices,
    ShadowDataFileSummary,
)
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.users.models import AccountApprovalStatusChoices, User

from .table_family import (
    _parse_write_scope,
    _parser_models_for_instance,
    _production_parser_models,
    _program_code,
    _section_name,
    _uses_shadow_table,
)

logger = getattr(settings, "PARSER_LOGGER", logging.getLogger("tdpservice.parsers"))


def _get_summary_status(dfs, data_file, parser_error_model=ParserError):
    """Return DataFileSummary-style status using the selected parser error model."""
    if dfs.status != DataFileSummary.Status.PENDING:
        return dfs.status

    counts = parser_error_model.objects.filter(
        file=data_file, deprecated=False
    ).aggregate(
        total=Count("id"),
        precheck=Count(
            Case(
                When(error_type=ParserErrorCategoryChoices.PRE_CHECK, then=1),
                output_field=IntegerField(),
            )
        ),
        record_precheck=Count(
            Case(
                When(error_type=ParserErrorCategoryChoices.RECORD_PRE_CHECK, then=1),
                output_field=IntegerField(),
            )
        ),
        case_consistency=Count(
            Case(
                When(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY, then=1),
                output_field=IntegerField(),
            )
        ),
    )

    if counts["precheck"] > 0:
        return DataFileSummary.Status.REJECTED
    if counts["total"] == 0:
        return DataFileSummary.Status.ACCEPTED
    if counts["case_consistency"] > 0 or counts["record_precheck"] > 0:
        return DataFileSummary.Status.PARTIALLY_ACCEPTED
    return DataFileSummary.Status.ACCEPTED_WITH_ERRORS


def update_dfs(
    dfs,
    data_file,
    parser_error_model=None,
    record_model_resolver=None,
    parse_token=None,
):
    """Update DataFileSummary fields using the selected parser output models."""
    parser_models = _parser_models_for_instance(data_file)
    parser_error_model = parser_error_model or parser_models.parser_error_model
    record_model_resolver = record_model_resolver or parser_models.record_model_resolver

    dfs.status = _get_summary_status(dfs, data_file, parser_error_model)

    program_code = _program_code(data_file)
    section_name = _section_name(data_file) or ""

    from tdpservice.parsers.parsing_service import service as _service_mod

    fra_func = getattr(_service_mod, "fra_total_errors", fra_total_errors)
    case_func = getattr(
        _service_mod, "case_aggregates_by_month", case_aggregates_by_month
    )
    total_func = getattr(
        _service_mod, "total_errors_by_month", total_errors_by_month
    )

    if program_code == "FRA":
        dfs.case_aggregates = fra_func(
            data_file, parser_error_model=parser_error_model
        )
    else:
        if "Case Data" in section_name:
            dfs.case_aggregates = case_func(
                data_file,
                dfs.status,
                parser_error_model=parser_error_model,
                record_model_resolver=record_model_resolver,
            )
        else:
            dfs.case_aggregates = total_func(
                data_file,
                dfs.status,
                parser_error_model=parser_error_model,
            )
    with _parse_write_scope(data_file, parse_token):
        dfs.save()


def set_error_report(dfs, error_report, parse_token=None):
    """Update DataFileSummary error_report."""
    is_shadow = isinstance(dfs, ShadowDataFileSummary)
    file_name = f"{dfs.datafile.original_filename}"
    if is_shadow:
        file_name += "_shadow"

    file_name += "_error_report"
    dfs.error_report = File(error_report, name=file_name)
    with _parse_write_scope(dfs.datafile, parse_token):
        dfs.save()


def _transition_parse_outcome(
    data_file,
    dfs,
    parse_token=None,
    reparse_id=None,
    event_id=None,
    extra_metadata=None,
    actor="python_parser",
    task_name=None,
):
    """Report a parse outcome to the lifecycle controller."""
    parse_context = {
        "section": _section_name(data_file),
        "program_type": _program_code(data_file),
        "parse_summary_status": dfs.status,
        "reparse_id": reparse_id,
        **(extra_metadata or {}),
    }

    if _uses_shadow_table(data_file):
        target_state = (
            SubmissionState.PARSE_COMPLETED
            if dfs.status == DataFileSummary.Status.ACCEPTED
            else SubmissionState.PARSED_WITH_ERRORS
        )
        is_go = actor == "go_parser" or (
            extra_metadata and extra_metadata.get("parser_class") == "GoParser"
        )
        record_shadow_parse_state(
            data_file,
            target_state,
            note="Go shadow parsing completed" if is_go else "Shadow parsing completed",
            log_fields=parse_context,
            event_id=event_id,
            reparse_meta_id=reparse_id,
            source="go_parser" if is_go else actor,
            task_name=task_name,
        )
        return

    record_parse_outcome(
        data_file,
        parse_token,
        dfs.status,
        log_fields=parse_context,
        event_id=event_id,
        reparse_meta_id=reparse_id,
        actor=actor,
        task_name=task_name,
    )


def should_send_reparse_notification(dfs, file_meta, reparse_id) -> bool:
    """Return whether a reparse completion email should be sent."""
    if not reparse_id:
        return True

    if file_meta is None:
        return True

    return not (
        file_meta.previous_summary_status == DataFileSummary.Status.ACCEPTED
        and dfs.status == DataFileSummary.Status.ACCEPTED
    )


def _notify_data_analysts(data_file, dfs, file_meta=None, reparse_id=None):
    """Send submission email to relevant data analysts."""
    from tdpservice.email.helpers.data_file import (
        send_data_submitted_email as _real_send_email,
    )
    from tdpservice.scheduling import parser_task
    from tdpservice.parsers.parsing_service import service as _service_mod

    notifier = send_data_submitted_email
    if (
        hasattr(_service_mod, "send_data_submitted_email")
        and _service_mod.send_data_submitted_email is not _real_send_email
    ):
        notifier = _service_mod.send_data_submitted_email
    elif (
        hasattr(parser_task, "send_data_submitted_email")
        and parser_task.send_data_submitted_email is not _real_send_email
    ):
        notifier = parser_task.send_data_submitted_email

    qs = User.objects.filter(
        stt=data_file.stt,
        account_approval_status=AccountApprovalStatusChoices.APPROVED,
        groups__name="Data Analyst",
    )

    if _program_code(data_file) == "FRA":
        qs = qs.filter(user_permissions__codename="has_fra_access")

    recipients = qs.values_list("username", flat=True).distinct()
    if should_send_reparse_notification(dfs, file_meta, reparse_id):
        notifier(
            dfs, recipients, is_reprocessed=(reparse_id is not None)
        )


def _handle_parse_failure(
    data_file,
    parse_token=None,
    note="",
    reparse_id=None,
    event_id=None,
    actor="python_parser",
    extra_metadata=None,
    task_name=None,
):
    """Report a technical parser failure to the lifecycle controller."""
    log_fields = {
        "section": _section_name(data_file),
        "program_type": _program_code(data_file),
        "reparse_id": reparse_id,
        **({"parse_error": note} if actor == "go_parser" else {}),
        **(extra_metadata or {}),
    }
    if data_file is not None and _uses_shadow_table(data_file):
        return record_shadow_parse_state(
            data_file,
            SubmissionState.PARSE_FAILED,
            note=note,
            log_fields=log_fields,
            event_id=event_id,
            reparse_meta_id=reparse_id,
            source=actor,
            task_name=task_name,
        )
    return record_parse_failure(
        data_file,
        parse_token,
        note=note,
        event_id=event_id,
        reparse_meta_id=reparse_id,
        actor=actor,
        log_fields=log_fields,
        task_name=task_name,
    )


def _reject_dfs(dfs, parse_token=None):
    """Mark a data file summary as rejected if it exists."""
    if dfs is not None:
        with _parse_write_scope(dfs.datafile, parse_token):
            dfs.set_status(DataFileSummary.Status.REJECTED)
            dfs.save()


def _finalize_parse(
    data_file,
    dfs,
    parser_error_model=None,
    record_model_resolver=None,
    roll_log=True,
    parse_token=None,
):
    """Generate parse artifacts and refresh DataFileSummary aggregates."""
    parser_models = _parser_models_for_instance(data_file)
    parser_error_model = parser_error_model or parser_models.parser_error_model
    record_model_resolver = record_model_resolver or parser_models.record_model_resolver

    logger.info(
        "%s DataFile parsing finished for file -> %r.",
        parser_models.label.capitalize(),
        data_file,
    )
    if dfs is None:
        return

    error_report_generator = ErrorReportFactory.get_error_report_generator(
        data_file,
        parser_error_model=parser_error_model,
    )
    error_report = error_report_generator.generate()
    set_error_report(dfs, error_report, parse_token=parse_token)
    if roll_log and len(logger.handlers) > 2:
        logger.handlers[2].doRollover(data_file)

    explicit_status = dfs.status
    update_dfs(
        dfs,
        data_file,
        parser_error_model=parser_error_model,
        record_model_resolver=record_model_resolver,
        parse_token=parse_token,
    )
    if explicit_status == DataFileSummary.Status.REJECTED:
        with _parse_write_scope(data_file, parse_token):
            dfs.status = explicit_status
            dfs.save(update_fields=["status"])


def _finalize_reparse(
    data_file,
    reparse_id,
    file_meta,
    dfs,
    reparse_success,
):
    """Ask the lifecycle controller to close current reparse metadata."""
    if reparse_id is None:
        return
    if data_file is None or file_meta is None:
        return

    from tdpservice.parsers.parsing_service import service as _service_mod

    finish_func = getattr(_service_mod, "finish_reparse", finish_reparse)

    finalized = finish_func(
        data_file,
        file_meta,
        success=reparse_success,
        num_records_created=getattr(dfs, "total_number_of_records_created", 0),
        cat_4_errors_generated=ParserError.objects.filter(
            file_id=data_file.id,
            error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY,
        ).count(),
    )
    if finalized:
        ReparseMeta.set_total_num_records_post(ReparseMeta.objects.get(pk=reparse_id))


def _add_unexpected_error(data_file, parse_token=None):
    """Persist a user-facing parser error for unexpected failures."""
    from tdpservice.parsers.error_generator import (
        ErrorGeneratorFactory as _real_factory,
    )
    from tdpservice.scheduling import parser_task

    factory_cls = ErrorGeneratorFactory
    if (
        hasattr(parser_task, "ErrorGeneratorFactory")
        and parser_task.ErrorGeneratorFactory is not _real_factory
    ):
        factory_cls = parser_task.ErrorGeneratorFactory

    generate_error = factory_cls(data_file).get_generator(
        ErrorGeneratorType.MSG_ONLY_PRECHECK,
        None,
    )
    generator_args = ErrorGeneratorArgs(
        record=None,
        schema=None,
        error_message=(
            "We're sorry, an unexpected error has occurred and the file has been "
            "rejected. Please contact the TDP support team at TANFData@acf.hhs.gov "
            "for further assistance."
        ),
    )
    error = generate_error(generator_args=generator_args)
    with _parse_write_scope(data_file, parse_token):
        error.save()


def _calculate_total_records(dfs: Optional[Any] = None) -> int:
    """Calculate total records processed from summary record counters."""
    if dfs is None:
        return 0
    return (
        getattr(dfs, "total_number_of_records_in_file", 0)
        or getattr(dfs, "total_number_of_records_created", 0)
        or 0
    )


def _count_parser_errors(data_file, parser_error_model):
    """Best-effort count of active errors for execution metrics."""
    try:
        return parser_error_model.objects.filter(
            file=data_file, deprecated=False
        ).count()
    except DatabaseError:
        logger.warning(
            "Failed to count parser errors for execution metadata.",
            extra={"data_file_id": getattr(data_file, "id", None)},
            exc_info=True,
        )
        return None


def _get_execution_metadata(
    dfs: Optional[Any] = None,
    duration_ms: int = 0,
    parser_class: Optional[str] = None,
    data_file: Optional[Any] = None,
) -> dict:
    """Return execution metrics metadata dictionary to append to state transition."""
    total_records = _calculate_total_records(dfs)
    total_errors = 0
    if data_file is not None:
        parser_models = _parser_models_for_instance(data_file)
        if parser_models.parser_error_model:
            error_count = _count_parser_errors(
                data_file, parser_models.parser_error_model
            )
            if error_count is not None:
                total_errors = error_count

    return {
        "parser_class": parser_class,
        "execution_duration_ms": duration_ms,
        "total_records_processed": total_records,
        "total_errors_generated": total_errors,
    }


def _record_failed_parse(
    data_file,
    dfs,
    parse_token,
    note,
    reparse_id=None,
    add_unexpected_error=False,
    event_id=None,
    extra_metadata=None,
):
    """Best-effort failure artifacts, followed by the authoritative outcome."""
    is_shadow = _uses_shadow_table(data_file) if data_file else False
    models = (
        _parser_models_for_instance(data_file)
        if data_file
        else _production_parser_models()
    )
    try:
        if add_unexpected_error and data_file is not None and not is_shadow:
            _add_unexpected_error(data_file, parse_token=parse_token)
        if dfs is not None:
            _reject_dfs(dfs, parse_token=parse_token)
            _finalize_parse(
                data_file,
                dfs,
                parser_error_model=models.parser_error_model,
                record_model_resolver=models.record_model_resolver,
                parse_token=parse_token,
            )
    except StaleParseOwnership:
        return False
    except Exception:
        logger.exception(
            "Failed to finalize parser failure artifacts.",
            extra={
                "data_file_id": getattr(data_file, "id", None),
                "parse_token": str(parse_token) if parse_token else None,
                "reparse_id": reparse_id,
            },
        )
    if extra_metadata is not None and data_file is not None:
        error_count = _count_parser_errors(data_file, models.parser_error_model)
        if error_count is not None:
            extra_metadata["total_errors_generated"] = error_count
    if data_file is not None:
        if not is_shadow and parse_token is None:
            return False
        return _handle_parse_failure(
            data_file,
            parse_token,
            note,
            reparse_id=reparse_id,
            event_id=event_id,
            extra_metadata=extra_metadata,
        )
    return False
