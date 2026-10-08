"""Celery hook for parsing tasks."""

from __future__ import absolute_import

import logging
import uuid

from django.conf import settings
from django.db import transaction

from celery import current_app, shared_task

from tdpservice.core.utils import get_feature_flag, log
from tdpservice.data_files.enums import GoParserMode
from tdpservice.data_files.models import (
    DataFile,
    ReparseFileMeta,
    create_or_update_shadow_data_file,
)
from tdpservice.data_files.submission_lifecycle import (
    begin_parse,
    claim_parse,
    record_parse_dispatch_failure,
)
from tdpservice.parsers.service import (
    ParsingService,
    _parser_models_for_mode,
    _uses_shadow_table,
)

logger = logging.getLogger("tdpservice.parsers")

GO_PARSER_TASK_NAME = "tdpservice.scheduling.parser_task.go_parse"
GO_PARSER_POST_PARSE_TASK_NAME = "tdpservice.scheduling.parser_task.post_parse"
GO_PARSER_QUEUE = getattr(settings, "GO_PARSER_QUEUE", "go-parser")
GO_PARSER_FEATURE_FLAG = "go_parser_mode"

__all__ = [
    "GO_PARSER_FEATURE_FLAG",
    "GO_PARSER_POST_PARSE_TASK_NAME",
    "GO_PARSER_QUEUE",
    "GO_PARSER_TASK_NAME",
    "go_parse",
    "parse",
    "post_parse",
    "queue_go_parse",
    "queue_parse",
    "resolve_or_reuse_parser_mode",
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
    service = ParsingService(
        data_file=data_file,
        reparse_id=reparse_id or None,
        parse_token=parse_token or None,
        event_id=event_id,
    )
    service.post_parse(
        parse_error=parse_error,
        table_mode=table_mode,
        task_name=GO_PARSER_POST_PARSE_TASK_NAME,
    )


@shared_task
def parse(data_file_id, reparse_id=None, parse_token=None, event_id=None):
    """Send data file for processing."""
    data_file = DataFile.objects.get(id=data_file_id)
    service = ParsingService(
        data_file=data_file,
        reparse_id=reparse_id,
        parse_token=parse_token,
        event_id=event_id,
    )
    result = service.run()
    if not result.success and (
        result.data_file is None
        or (service.parse_token is None and not _uses_shadow_table(result.data_file))
    ):
        if result.error_message:
            raise ValueError(result.error_message)
        raise RuntimeError("Parsing failed before ownership establishment")
    return result
