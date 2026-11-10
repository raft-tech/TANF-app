"""Task scheduling and routing for the parsing service."""

import uuid

from tdpservice.data_files.enums import GoParserMode


def _evaluate_go_parser_mode() -> GoParserMode:
    """Evaluate the current feature flag for an unassigned data file."""
    from tdpservice.scheduling import parser_task

    return parser_task._evaluate_go_parser_mode()


def resolve_or_reuse_parser_mode(data_file_id: int) -> GoParserMode:
    """Return one durable parser route for every dispatch of a data file."""
    from tdpservice.scheduling import parser_task

    return parser_task.resolve_or_reuse_parser_mode(data_file_id)


def queue_go_parse(
    data_file_id: int,
    table_mode: GoParserMode,
    reparse_id: int | None = None,
    parse_token=None,
    event_id=None,
) -> None:
    """Queue a Go parser task with routing, ownership, and audit context."""
    from tdpservice.scheduling import parser_task

    return parser_task.queue_go_parse(
        data_file_id,
        table_mode=table_mode,
        reparse_id=reparse_id,
        parse_token=parse_token,
        event_id=event_id,
    )


def queue_parse(
    data_file_id: int,
    reparse_id: int | None = None,
    event_id=None,
) -> uuid.UUID:
    """Route every parse of a data file using its persisted parser mode."""
    from tdpservice.scheduling import parser_task

    return parser_task.queue_parse(
        data_file_id,
        reparse_id=reparse_id,
        event_id=event_id,
    )
