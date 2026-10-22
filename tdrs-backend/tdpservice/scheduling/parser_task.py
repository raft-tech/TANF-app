"""Celery task entrypoints for parsing workflows."""

from __future__ import absolute_import

from celery import shared_task

from tdpservice.data_files.enums import GoParserMode
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.service import (
    GO_PARSER_FEATURE_FLAG,
    GO_PARSER_POST_PARSE_TASK_NAME,
    GO_PARSER_QUEUE,
    GO_PARSER_TASK_NAME,
    ParsingService,
    logger,
)

# Backward-compatible convenience aliases delegating to ParsingService
_evaluate_go_parser_mode = ParsingService.evaluate_parser_mode
resolve_or_reuse_parser_mode = ParsingService.resolve_or_reuse_parser_mode
queue_go_parse = ParsingService.queue_go_parse
queue_parse = ParsingService.schedule


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
    service = ParsingService.for_post_parse(
        data_file_id=data_file_id,
        table_mode=table_mode,
        reparse_id=reparse_id,
        parse_token=parse_token,
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
        or (service.parse_token is None and not service.uses_shadow_table)
    ):
        if result.error_message:
            raise ValueError(result.error_message)
        raise RuntimeError("Parsing failed before ownership establishment")
    return result.to_dict()


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
    service = ParsingService.for_post_parse(
        data_file_id=data_file_id,
        table_mode=table_mode,
        reparse_id=reparse_id,
        parse_token=parse_token,
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
        or (service.parse_token is None and not service.uses_shadow_table)
    ):
        if result.error_message:
            raise ValueError(result.error_message)
        raise RuntimeError("Parsing failed before ownership establishment")
    return result.to_dict()
