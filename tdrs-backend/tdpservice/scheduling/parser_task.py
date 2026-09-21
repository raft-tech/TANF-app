"""Celery hook for parsing tasks."""

from __future__ import absolute_import

import logging
import uuid

from django.conf import settings
from django.db import transaction

from celery import current_app, shared_task

from tdpservice.core.utils import get_feature_flag, log
from tdpservice.data_files.enums import GoParserMode, SubmissionState
from tdpservice.data_files.error_reports import ErrorReportFactory
from tdpservice.data_files.models import (
    DataFile,
    ReparseFileMeta,
    ShadowDataFile,
    create_or_update_shadow_data_file,
)
from tdpservice.data_files.parser_error_choices import ParserErrorCategoryChoices
from tdpservice.data_files.submission_lifecycle import (
    StaleParseOwnership,
    begin_parse,
    claim_parse,
    record_parse_dispatch_failure,
    record_parse_outcome,
    record_shadow_parse_state,
)
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
from tdpservice.parsers.factory import ParserFactory
from tdpservice.parsers.models import (
    DataFileSummary,
    ParserError,
    ShadowDataFileSummary,
    ShadowParserError,
)
from tdpservice.parsers.service import (
    ParserModelSet,
    ParseResult,
    ParsingService,
    _add_unexpected_error,
    _calculate_total_records,
    _finalize_parse,
    _finalize_reparse,
    _get_execution_metadata,
    _get_summary_status,
    _handle_parse_failure,
    _notify_data_analysts,
    _parse_write_scope,
    _parser_models_for_instance,
    _parser_models_for_mode,
    _production_parser_models,
    _record_failed_parse,
    _reject_dfs,
    _resolve_parse_owner,
    _shadow_parser_models,
    _shadow_record_model,
    _transition_parse_outcome,
    _uses_shadow_table,
    set_error_report,
    should_send_reparse_notification,
    update_dfs,
)
from tdpservice.log_handler import change_log_filename
from tdpservice.parsers.util import (
    DecoderUnknownException,
    log_parser_exception,
)
from tdpservice.email.helpers.data_file import send_data_submitted_email
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta

logger = logging.getLogger("tdpservice.parsers")

GO_PARSER_TASK_NAME = "tdpservice.scheduling.parser_task.go_parse"
GO_PARSER_POST_PARSE_TASK_NAME = "tdpservice.scheduling.parser_task.post_parse"
GO_PARSER_QUEUE = getattr(settings, "GO_PARSER_QUEUE", "go-parser")
GO_PARSER_FEATURE_FLAG = "go_parser_mode"

__all__ = [
    "DecoderUnknownException",
    "DataFileSummary",
    "ErrorReportFactory",
    "ErrorGeneratorArgs",
    "ErrorGeneratorFactory",
    "ErrorGeneratorType",
    "GO_PARSER_POST_PARSE_TASK_NAME",
    "GO_PARSER_QUEUE",
    "GO_PARSER_TASK_NAME",
    "ParserError",
    "ParserErrorCategoryChoices",
    "ParserFactory",
    "ParserModelSet",
    "ParseResult",
    "ParsingService",
    "ReparseMeta",
    "ShadowDataFileSummary",
    "ShadowParserError",
    "StaleParseOwnership",
    "_add_unexpected_error",
    "_calculate_total_records",
    "_finalize_parse",
    "_finalize_reparse",
    "_get_execution_metadata",
    "_get_summary_status",
    "_handle_parse_failure",
    "_notify_data_analysts",
    "_parse_write_scope",
    "_parser_models_for_instance",
    "_parser_models_for_mode",
    "_production_parser_models",
    "_record_failed_parse",
    "_reject_dfs",
    "_resolve_parse_owner",
    "_shadow_parser_models",
    "_shadow_record_model",
    "_transition_parse_outcome",
    "_uses_shadow_table",
    "begin_parse",
    "case_aggregates_by_month",
    "change_log_filename",
    "claim_parse",
    "fra_total_errors",
    "go_parse",
    "logger",
    "log_parser_exception",
    "parse",
    "post_parse",
    "queue_go_parse",
    "queue_parse",
    "record_parse_dispatch_failure",
    "record_parse_outcome",
    "record_shadow_parse_state",
    "send_data_submitted_email",
    "set_error_report",
    "should_send_reparse_notification",
    "total_errors_by_month",
    "update_dfs",
]


def _evaluate_go_parser_mode() -> GoParserMode:
    """Evaluate the current feature flag for an unassigned data file."""
    enabled, config = get_feature_flag(GO_PARSER_FEATURE_FLAG)
    if not enabled:
        return GoParserMode.PYTHON_ONLY

    try:
        return GoParserMode(config.get("mode"))
    except (AttributeError, TypeError, ValueError):
        logger.error(
            "Invalid %s feature flag configuration; disabling Go parser dispatch.",
            GO_PARSER_FEATURE_FLAG,
        )
        return GoParserMode.PYTHON_ONLY


@transaction.atomic
def resolve_or_reuse_parser_mode(data_file_id: int) -> GoParserMode:
    """Return one durable parser route for every dispatch of a data file."""
    data_file = DataFile.objects.select_for_update().get(id=data_file_id)
    if data_file.parser_mode is not None:
        return GoParserMode(data_file.parser_mode)

    parser_mode = _evaluate_go_parser_mode()
    data_file.parser_mode = parser_mode
    data_file.save(update_fields=["parser_mode"])
    return parser_mode


def queue_go_parse(
    data_file_id: int,
    table_mode: GoParserMode,
    reparse_id: int | None = None,
    parse_token=None,
    event_id=None,
) -> None:
    """Queue a Go parser task with routing, ownership, and audit context."""
    if table_mode not in (GoParserMode.GO_SHADOW, GoParserMode.GO_ONLY):
        raise ValueError(f"Cannot queue Go parser in {table_mode.value!r} mode")
    event_id = str(event_id or uuid.uuid4())
    try:
        current_app.send_task(
            GO_PARSER_TASK_NAME,
            args=[
                data_file_id,
                reparse_id or 0,
                table_mode.value,
                str(parse_token or ""),
                event_id,
            ],
            queue=GO_PARSER_QUEUE,
            ignore_result=True,
        )
    except Exception:
        data_file = DataFile.objects.get(id=data_file_id)
        log(
            (
                f"Failed to submit Go parser {table_mode.value} task "
                f"for datafile {data_file_id}."
            ),
            logger_context={
                "user_id": data_file.user_id,
                "content_type": DataFile,
                "object_id": data_file.pk,
                "object_repr": repr(data_file),
            },
            level="exception",
        )
        if table_mode == GoParserMode.GO_ONLY:
            raise


def queue_parse(
    data_file_id: int,
    reparse_id: int | None = None,
    event_id=None,
) -> uuid.UUID:
    """Route every parse of a data file using its persisted parser mode."""
    event_id = str(event_id or uuid.uuid4())
    table_mode = resolve_or_reuse_parser_mode(data_file_id)
    data_file = DataFile.objects.get(pk=data_file_id)
    file_meta = None
    if reparse_id:
        file_meta = ReparseFileMeta.objects.get(
            data_file_id=data_file_id,
            reparse_meta_id=reparse_id,
        )

    if table_mode == GoParserMode.GO_SHADOW:
        create_or_update_shadow_data_file(data_file)

    parse_token = claim_parse(data_file, reparse_file_meta=file_meta)
    try:
        if table_mode != GoParserMode.GO_ONLY:
            parse.delay(
                data_file_id,
                reparse_id=reparse_id,
                parse_token=str(parse_token),
                event_id=event_id,
            )
        else:
            begin_parse(
                data_file,
                parse_token,
                file_meta,
                actor="go_parser",
                event_id=event_id,
            )

        if table_mode != GoParserMode.PYTHON_ONLY:
            queue_go_parse(
                data_file_id,
                table_mode,
                reparse_id=reparse_id,
                parse_token=parse_token,
                event_id=event_id,
            )
    except Exception:
        record_parse_dispatch_failure(
            data_file, parse_token, file_meta, event_id=event_id
        )
        raise
    return parse_token


@shared_task(name=GO_PARSER_TASK_NAME)
def go_parse(
    data_file_id: int,
    reparse_id: int = 0,
    table_mode: str | None = None,
    parse_token="",
    event_id=None,
) -> None:
    """Register the Go parser task name without executing it in Python."""
    raise RuntimeError(
        f"go_parse for data_file_id={data_file_id} is routed to the Go parser worker "
        "and should not execute in the Python worker"
    )


@shared_task(name=GO_PARSER_POST_PARSE_TASK_NAME)
def post_parse(
    data_file_id: int,
    reparse_id: int = 0,
    parse_error: str | None = None,
    table_mode: str | None = None,
    parse_token="",
    event_id=None,
) -> None:
    """Finalize Go parser output in its selected table family."""
    parser_models = _parser_models_for_mode(table_mode)
    data_file = parser_models.data_file_model.objects.get(id=data_file_id)
    is_shadow = _uses_shadow_table(data_file)

    audit_context = {
        "source": "go_parser",
        "event_id": event_id,
        "reparse_meta_id": reparse_id or None,
        "task_name": GO_PARSER_POST_PARSE_TASK_NAME,
    }
    if is_shadow:
        if parse_error and data_file.state == SubmissionState.PARSE_FAILED:
            return
        if data_file.state != SubmissionState.PARSE_STARTED:
            record_shadow_parse_state(
                data_file,
                SubmissionState.PARSE_STARTED,
                note="Go shadow parsing started",
                **audit_context,
            )
        dfs, _ = parser_models.summary_model.objects.get_or_create(
            datafile=data_file,
            defaults={"status": DataFileSummary.Status.PENDING},
        )
        if parse_error:
            dfs.status = DataFileSummary.Status.REJECTED
            dfs.save()
            execution_meta = _get_execution_metadata(
                dfs,
                duration_ms=0,
                parser_class="GoParser",
                data_file=data_file,
            )
            execution_meta["parse_error"] = str(parse_error)
            execution_meta["section"] = data_file.section
            execution_meta["program_type"] = data_file.program_type
            execution_meta["reparse_id"] = reparse_id or None
            record_shadow_parse_state(
                data_file,
                SubmissionState.PARSE_FAILED,
                note=str(parse_error),
                log_fields=execution_meta,
                **audit_context,
            )
            return
        _finalize_parse(
            data_file,
            dfs,
            parser_error_model=parser_models.parser_error_model,
            record_model_resolver=parser_models.record_model_resolver,
            roll_log=False,
        )
        target_state = (
            SubmissionState.PARSE_COMPLETED
            if dfs.status == DataFileSummary.Status.ACCEPTED
            else SubmissionState.PARSED_WITH_ERRORS
        )
        execution_meta = _get_execution_metadata(
            dfs,
            duration_ms=0,
            parser_class="GoParser",
            data_file=data_file,
        )
        execution_meta["parse_summary_status"] = dfs.status
        execution_meta["section"] = data_file.section
        execution_meta["program_type"] = data_file.program_type
        execution_meta["reparse_id"] = reparse_id or None
        record_shadow_parse_state(
            data_file,
            target_state,
            note="Go shadow parsing completed",
            log_fields=execution_meta,
            **audit_context,
        )
        return

    file_meta, parse_token = _resolve_parse_owner(
        data_file,
        reparse_id or None,
        parse_token or None,
    )
    if data_file.state != SubmissionState.PARSE_STARTED:
        begin_parse(
            data_file, parse_token, file_meta, actor="go_parser", event_id=event_id
        )

    with _parse_write_scope(data_file, parse_token):
        dfs, _ = parser_models.summary_model.objects.get_or_create(
            datafile=data_file,
            defaults={"status": DataFileSummary.Status.PENDING},
        )

    if parse_error:
        _reject_dfs(dfs, parse_token=parse_token)
        execution_meta = _get_execution_metadata(
            dfs,
            duration_ms=0,
            parser_class="GoParser",
            data_file=data_file,
        )
        _handle_parse_failure(
            data_file,
            parse_token,
            str(parse_error),
            reparse_id=reparse_id or None,
            event_id=event_id,
            actor="go_parser",
            extra_metadata=execution_meta,
        )
        logger.error(
            "Go parser %s post-parse received parse_error for data_file_id=%s: %s",
            parser_models.label,
            data_file_id,
            parse_error,
        )
        reparse_success = False
    else:
        _finalize_parse(
            data_file,
            dfs,
            parser_error_model=parser_models.parser_error_model,
            record_model_resolver=parser_models.record_model_resolver,
            roll_log=False,
            parse_token=parse_token,
        )
        execution_meta = _get_execution_metadata(
            dfs,
            duration_ms=0,
            parser_class="GoParser",
            data_file=data_file,
        )
        _transition_parse_outcome(
            data_file,
            dfs,
            parse_token,
            reparse_id=reparse_id or None,
            event_id=event_id,
            extra_metadata=execution_meta,
        )
        reparse_success = True
    _finalize_reparse(
        data_file,
        reparse_id or None,
        file_meta,
        dfs,
        reparse_success,
    )


@shared_task
def parse(data_file_id, reparse_id=None, parse_token=None, event_id=None):
    """Send data file for processing."""
    service = ParsingService(
        data_file_id=data_file_id,
        reparse_id=reparse_id,
        parse_token=parse_token,
        event_id=event_id,
    )
    service.fetch_data_file()
    service.validate_preconditions()
    return service.run()
