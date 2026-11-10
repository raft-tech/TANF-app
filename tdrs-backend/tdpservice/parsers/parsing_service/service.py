"""ParsingService for single-DataFile processing and lifecycle orchestration."""

import logging
import time
import uuid
from typing import Any, Optional, Union
from uuid import UUID

from django.conf import settings
from django.db.utils import DatabaseError

from tdpservice.data_files.enums import GoParserMode, SubmissionState
from tdpservice.data_files.error_reports import ErrorReportFactory  # noqa: F401
from tdpservice.data_files.models import (
    DataFile,
    ReparseFileMeta,
    ShadowDataFile,
)
from tdpservice.data_files.submission_lifecycle import (
    PARSE_QUEUEABLE_STATES,
    StaleParseOwnership,
    begin_parse,
    finish_reparse,  # noqa: F401
    record_parse_dispatch_failure,
    record_shadow_parse_state,
)
from tdpservice.email.helpers.data_file import (  # noqa: F401
    send_data_submitted_email,
)
from tdpservice.log_handler import change_log_filename
from tdpservice.parsers.aggregates import (  # noqa: F401
    case_aggregates_by_month,
    fra_total_errors,
    total_errors_by_month,
)
from tdpservice.parsers.error_generator import (  # noqa: F401
    ErrorGeneratorFactory,
)
from tdpservice.parsers.factory import ParserFactory
from tdpservice.parsers.models import (
    DataFileSummary,
    ParserError,
    ShadowDataFileSummary,
    ShadowParserError,
)
from tdpservice.parsers.util import DecoderUnknownException, log_parser_exception

from .classes import ParseResult, ParserModelSet  # noqa: F401
from .dispatch import (  # noqa: F401
    _evaluate_go_parser_mode,
    queue_go_parse,
    queue_parse,
    resolve_or_reuse_parser_mode,
)
from .engine import PythonParserEngine  # noqa: F401
from .lifecycle import (  # noqa: F401
    _add_unexpected_error,
    _calculate_total_records,
    _count_parser_errors,
    _finalize_parse,
    _finalize_reparse,
    _get_execution_metadata,
    _get_summary_status,
    _handle_parse_failure,
    _notify_data_analysts,
    _record_failed_parse,
    _reject_dfs,
    _transition_parse_outcome,
    set_error_report,
    should_send_reparse_notification,
    update_dfs,
)
from .table_family import (  # noqa: F401
    _parse_write_scope,
    _parser_models_for_instance,
    _parser_models_for_mode,
    _production_parser_models,
    _program_code,
    _resolve_parse_owner,
    _section_name,
    _shadow_parser_models,
    _shadow_record_model,
    _uses_shadow_table,
)

logger = getattr(settings, "PARSER_LOGGER", logging.getLogger("tdpservice.parsers"))

GO_PARSER_TASK_NAME = "tdpservice.scheduling.parser_task.go_parse"
GO_PARSER_POST_PARSE_TASK_NAME = "tdpservice.scheduling.parser_task.post_parse"
GO_PARSER_QUEUE = getattr(settings, "GO_PARSER_QUEUE", "go-parser")
GO_PARSER_FEATURE_FLAG = "go_parser_mode"


class ParsingService:
    """Service for orchestrating the parsing flow of a single DataFile."""

    def __init__(
        self,
        data_file: Union[DataFile, ShadowDataFile],
        reparse_id: Optional[int] = None,
        parse_token: Optional[Union[str, UUID]] = None,
        event_id: Optional[Union[str, UUID]] = None,
        file_meta: Optional[ReparseFileMeta] = None,
    ):
        if data_file is None:
            raise ValueError("data_file must be provided to ParsingService.")
        self.data_file = data_file
        self.data_file_id = getattr(data_file, "id", None)
        self.reparse_id = reparse_id
        self.parse_token = str(parse_token) if parse_token else None
        self.event_id = str(event_id or uuid.uuid4())
        self.file_meta = file_meta
        self.dfs: Optional[Union[DataFileSummary, ShadowDataFileSummary]] = None

    @property
    def uses_shadow_table(self) -> bool:
        """Return True if this parsing service operates on a shadow table instance."""
        return _uses_shadow_table(self.data_file)

    @staticmethod
    def evaluate_parser_mode() -> GoParserMode:
        """Evaluate the current feature flag for an unassigned data file."""
        return _evaluate_go_parser_mode()

    @staticmethod
    def resolve_or_reuse_parser_mode(data_file_id: int) -> GoParserMode:
        """Return one durable parser route for every dispatch of a data file."""
        return resolve_or_reuse_parser_mode(data_file_id)

    @classmethod
    def schedule(
        cls,
        data_file_id: int,
        reparse_id: int | None = None,
        event_id=None,
    ) -> uuid.UUID:
        """Route and schedule every parse of a data file using its persisted parser mode."""
        return queue_parse(data_file_id, reparse_id=reparse_id, event_id=event_id)

    queue_parse = schedule

    @staticmethod
    def queue_go_parse(
        data_file_id: int,
        table_mode: GoParserMode,
        reparse_id: int | None = None,
        parse_token=None,
        event_id=None,
    ) -> None:
        """Queue a Go parser task with routing, ownership, and audit context."""
        return queue_go_parse(
            data_file_id=data_file_id,
            table_mode=table_mode,
            reparse_id=reparse_id,
            parse_token=parse_token,
            event_id=event_id,
        )

    @classmethod
    def for_post_parse(
        cls,
        data_file_id: int,
        table_mode: str | None = None,
        reparse_id: int = 0,
        parse_token: str = "",
        event_id=None,
    ) -> "ParsingService":
        """Construct a ParsingService instance for Go post-parse execution."""
        parser_models = _parser_models_for_mode(table_mode)
        data_file = parser_models.data_file_model.objects.get(id=data_file_id)
        return cls(
            data_file=data_file,
            reparse_id=reparse_id or None,
            parse_token=parse_token or None,
            event_id=event_id,
        )

    def fetch_data_file(self) -> Union[DataFile, ShadowDataFile]:
        """Return the target DataFile."""
        return self.data_file

    def validate_preconditions(self) -> None:
        """Validate preconditions for parsing the target DataFile.

        Checks:
        1. File existence (DataFile has an associated file).
        2. Valid submission state for parsing.
        3. Idempotency / parse token ownership guard.
        """
        data_file = self.data_file

        if not getattr(data_file, "file", None) or not getattr(
            data_file.file, "name", None
        ):
            raise ValueError(
                f"DataFile {data_file.id} does not have an associated file."
            )

        valid_states = PARSE_QUEUEABLE_STATES | {SubmissionState.PARSE_STARTED}
        if data_file.state not in valid_states:
            state_val = getattr(data_file.state, "value", str(data_file.state))
            raise ValueError(
                f"Cannot queue parsing for DataFile {data_file.id} from state '{state_val}'."
            )

        if (
            not _uses_shadow_table(data_file)
            and self.parse_token
            and getattr(data_file, "current_parse_token", None)
        ):
            if str(data_file.current_parse_token) != str(self.parse_token):
                raise StaleParseOwnership(
                    f"DataFile {data_file.id} has an active parse token {data_file.current_parse_token} "
                    f"which does not match provided token {self.parse_token}."
                )

    def get_parser(self):
        """Construct and return the parser instance via PythonParserEngine."""
        engine = PythonParserEngine(
            data_file=self.data_file,
            dfs=self.dfs,
            parse_token=self.parse_token,
        )
        return engine.get_parser()

    def parse(self) -> ParseResult:
        """Alias for run()."""
        return self.run()

    def _calculate_total_records(self) -> int:
        """Calculate total records processed from summary case aggregates."""
        return _calculate_total_records(self.dfs)

    def _get_execution_metadata(
        self,
        duration_ms: int,
        parser_class: Optional[str] = None,
        data_file: Optional[Union[DataFile, ShadowDataFile]] = None,
    ) -> dict:
        """Return execution metrics metadata dictionary to append to state transition."""
        return _get_execution_metadata(
            self.dfs,
            duration_ms=duration_ms,
            parser_class=parser_class,
            data_file=data_file or self.data_file,
        )

    def _start_parse_lifecycle(self, data_file: Any, is_shadow: bool) -> None:
        """Initialize parse owner, metadata, and initial state transition."""
        if not is_shadow:
            self.file_meta, self.parse_token = _resolve_parse_owner(
                data_file,
                self.reparse_id,
                self.parse_token,
            )
            begin_parse(
                data_file, self.parse_token, self.file_meta, event_id=self.event_id
            )
        else:
            self.file_meta, self.parse_token = None, None
            if data_file.state != SubmissionState.PARSE_STARTED:
                record_shadow_parse_state(
                    data_file,
                    SubmissionState.PARSE_STARTED,
                    note="Shadow parsing started",
                    event_id=self.event_id,
                    reparse_meta_id=self.reparse_id,
                    source="python_parser",
                )

    def _validate_python_parse_target(self) -> None:
        """Ensure Python parsing is only used for production DataFiles."""
        if self.uses_shadow_table:
            raise ValueError(
                "Python parsing only supports production DataFiles; use post_parse() "
                "for shadow parser output."
            )

    def post_parse(
        self,
        parse_error: Optional[str] = None,
        table_mode: Optional[str] = None,
        task_name: Optional[str] = None,
    ) -> None:
        """Finalize Go parser output for this DataFile in its selected table family."""
        parser_models = (
            _parser_models_for_mode(table_mode)
            if table_mode
            else _parser_models_for_instance(self.data_file)
        )
        data_file = self.data_file
        is_shadow = _uses_shadow_table(data_file)

        audit_context = {
            "source": "go_parser",
            "event_id": self.event_id,
            "reparse_meta_id": self.reparse_id or None,
            "task_name": task_name,
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
            self.dfs = dfs
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
                execution_meta["section"] = _section_name(data_file)
                execution_meta["program_type"] = _program_code(data_file)
                execution_meta["reparse_id"] = self.reparse_id or None
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
            execution_meta["section"] = _section_name(data_file)
            execution_meta["program_type"] = _program_code(data_file)
            execution_meta["reparse_id"] = self.reparse_id or None
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
            self.reparse_id or None,
            self.parse_token or None,
        )
        self.file_meta = file_meta
        self.parse_token = parse_token
        if data_file.state != SubmissionState.PARSE_STARTED:
            begin_parse(
                data_file,
                parse_token,
                file_meta,
                actor="go_parser",
                event_id=self.event_id,
            )

        with _parse_write_scope(data_file, parse_token):
            dfs, _ = parser_models.summary_model.objects.get_or_create(
                datafile=data_file,
                defaults={"status": DataFileSummary.Status.PENDING},
            )
            self.dfs = dfs

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
                reparse_id=self.reparse_id or None,
                event_id=self.event_id,
                actor="go_parser",
                extra_metadata=execution_meta,
                task_name=task_name,
            )
            logger.error(
                "Go parser %s post-parse received parse_error for data_file_id=%s: %s",
                parser_models.label,
                data_file.id,
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
                reparse_id=self.reparse_id or None,
                event_id=self.event_id,
                extra_metadata=execution_meta,
                actor="go_parser",
                task_name=task_name,
            )
            reparse_success = True
        _finalize_reparse(
            data_file,
            self.reparse_id or None,
            file_meta,
            dfs,
            reparse_success,
        )

    def run(self) -> ParseResult:  # noqa: C901
        """Parse a production DataFile and return a ParseResult."""
        self._validate_python_parse_target()

        data_file = None
        reparse_success = True
        stale_owner = False
        error_message = None
        parser_class_name = None
        start_time = time.monotonic()
        total_records_processed = 0
        total_errors_generated = 0

        try:
            data_file = self.data_file
            if self.reparse_id and self.file_meta is None:
                self.file_meta = ReparseFileMeta.objects.get(
                    data_file_id=data_file.id,
                    reparse_meta_id=self.reparse_id,
                )
            self.validate_preconditions()

            models = _parser_models_for_instance(data_file)
            is_shadow = _uses_shadow_table(data_file)
            filename = getattr(
                data_file,
                "filename",
                getattr(data_file, "original_filename", str(data_file)),
            )

            change_log_filename(logger, data_file)
            logger.info(
                f"\n\n\n __ Starting to {'re-' if self.reparse_id else ''}parse datafile {filename}__ \n\n\n"
            )

            self._start_parse_lifecycle(data_file, is_shadow)

            with _parse_write_scope(data_file, self.parse_token):
                self.dfs = models.summary_model.objects.create(
                    datafile=data_file, status=DataFileSummary.Status.PENDING
                )

            parser = self.get_parser()
            parser_class_name = parser.__class__.__name__
            parser.parse_and_validate()
            update_dfs(
                self.dfs,
                data_file,
                parser_error_model=models.parser_error_model,
                record_model_resolver=models.record_model_resolver,
                parse_token=self.parse_token,
            )

            logger.info(f"Parsing finished for file -> {repr(data_file)}.")

            _finalize_parse(
                data_file,
                self.dfs,
                parser_error_model=models.parser_error_model,
                record_model_resolver=models.record_model_resolver,
                parse_token=self.parse_token,
            )
            duration_ms = int((time.monotonic() - start_time) * 1000)
            execution_meta = self._get_execution_metadata(
                duration_ms=duration_ms,
                parser_class=parser_class_name,
                data_file=data_file,
            )
            total_records_processed = execution_meta.get(
                "total_records_processed", 0
            )
            total_errors_generated = execution_meta.get(
                "total_errors_generated", 0
            )

            _transition_parse_outcome(
                data_file,
                self.dfs,
                self.parse_token,
                self.reparse_id,
                self.event_id,
                extra_metadata=execution_meta,
            )

            if not is_shadow:
                try:
                    _notify_data_analysts(
                        data_file, self.dfs, self.file_meta, self.reparse_id
                    )
                except Exception:
                    logger.exception(
                        "Failed to notify data analysts after successful parse.",
                        extra={
                            "data_file_id": self.data_file_id,
                            "reparse_id": self.reparse_id,
                        },
                    )

            return ParseResult(
                success=True,
                data_file=data_file,
                summary=self.dfs,
                status=self.dfs.status if self.dfs else None,
                error_message=None,
                total_records_processed=total_records_processed,
                total_errors_generated=total_errors_generated,
            )

        except StaleParseOwnership as exc:
            stale_owner = True
            reparse_success = False
            error_message = str(exc)
            logger.warning(
                "Ignoring parser work from a stale ownership token.",
                extra={
                    "data_file_id": self.data_file_id,
                    "parse_token": str(self.parse_token),
                    "reparse_id": self.reparse_id,
                },
            )
            return ParseResult(
                success=False,
                data_file=data_file,
                summary=self.dfs,
                status=self.dfs.status if self.dfs else None,
                error_message=error_message,
                total_records_processed=0,
                total_errors_generated=0,
            )
        except DecoderUnknownException as exc:
            reparse_success = False
            error_message = str(exc) or "decoder unknown exception"
            logger.warning(
                "DecoderUnknownException during parse",
                extra={
                    "data_file_id": self.data_file_id,
                    "section": _section_name(data_file) if data_file else None,
                    "program_type": _program_code(data_file) if data_file else None,
                    "reparse_id": self.reparse_id,
                },
            )
            duration_ms = int((time.monotonic() - start_time) * 1000)
            execution_meta = self._get_execution_metadata(
                duration_ms=duration_ms,
                parser_class=parser_class_name,
                data_file=data_file,
            )
            total_records_processed = execution_meta.get(
                "total_records_processed", 0
            )
            total_errors_generated = execution_meta.get(
                "total_errors_generated", 0
            )
            stale_owner = not _record_failed_parse(
                data_file,
                self.dfs,
                self.parse_token,
                "decoder unknown exception",
                self.reparse_id,
                event_id=self.event_id,
                extra_metadata=execution_meta,
            )
            total_errors_generated = execution_meta.get(
                "total_errors_generated", 0
            )
            return ParseResult(
                success=False,
                data_file=data_file,
                summary=self.dfs,
                status=self.dfs.status if self.dfs else None,
                error_message=error_message,
                total_records_processed=total_records_processed,
                total_errors_generated=total_errors_generated,
            )
        except DatabaseError as e:
            reparse_success = False
            error_message = str(e) or "database error during parsing"
            log_parser_exception(
                data_file,
                f"Encountered Database exception in parsing service: \n{e}",
                "error",
            )
            logger.error(
                "DatabaseError during parse",
                extra={
                    "data_file_id": self.data_file_id,
                    "section": _section_name(data_file) if data_file else None,
                    "program_type": _program_code(data_file) if data_file else None,
                    "reparse_id": self.reparse_id,
                },
            )
            duration_ms = int((time.monotonic() - start_time) * 1000)
            execution_meta = self._get_execution_metadata(
                duration_ms=duration_ms,
                parser_class=parser_class_name,
                data_file=data_file,
            )
            total_records_processed = execution_meta.get(
                "total_records_processed", 0
            )
            total_errors_generated = execution_meta.get(
                "total_errors_generated", 0
            )
            stale_owner = not _record_failed_parse(
                data_file,
                self.dfs,
                self.parse_token,
                "database error during parsing",
                self.reparse_id,
                event_id=self.event_id,
                extra_metadata=execution_meta,
            )
            total_errors_generated = execution_meta.get(
                "total_errors_generated", 0
            )
            return ParseResult(
                success=False,
                data_file=data_file,
                summary=self.dfs,
                status=self.dfs.status if self.dfs else None,
                error_message=error_message,
                total_records_processed=total_records_processed,
                total_errors_generated=total_errors_generated,
            )
        except Exception as e:
            reparse_success = False
            error_message = str(e) or "unexpected error during parsing"
            is_shadow = _uses_shadow_table(data_file) if data_file else False
            if (
                data_file is not None
                and not is_shadow
                and self.parse_token
                and data_file.state in PARSE_QUEUEABLE_STATES
            ):
                stale_owner = not record_parse_dispatch_failure(
                    data_file,
                    self.parse_token,
                    self.file_meta,
                    note=f"Parser failed before parse start: {e}",
                    event_id=self.event_id,
                )
                return ParseResult(
                    success=False,
                    data_file=data_file,
                    summary=self.dfs,
                    status=self.dfs.status if self.dfs else None,
                    error_message=error_message,
                    total_records_processed=0,
                    total_errors_generated=0,
                )
            if data_file is None or (self.parse_token is None and not is_shadow):
                # If we failed before resolving data_file or token (e.g. precondition / DoesNotExist)
                logger.exception(
                    "Exception during parse before ownership establishment: %s",
                    e,
                    extra={"data_file_id": self.data_file_id},
                )
                return ParseResult(
                    success=False,
                    data_file=data_file,
                    summary=self.dfs,
                    status=None,
                    error_message=error_message,
                    total_records_processed=0,
                    total_errors_generated=0,
                )

            log_parser_exception(
                data_file,
                (
                    f"Uncaught exception while parsing datafile: {data_file.pk}! Please review the logs to "
                    f"see if manual intervention is required."
                ),
                "exception",
            )
            logger.exception(
                "Unexpected exception during parse",
                extra={
                    "data_file_id": self.data_file_id,
                    "section": _section_name(data_file) if data_file else None,
                    "program_type": _program_code(data_file) if data_file else None,
                    "reparse_id": self.reparse_id,
                },
            )
            duration_ms = int((time.monotonic() - start_time) * 1000)
            execution_meta = self._get_execution_metadata(
                duration_ms=duration_ms,
                parser_class=parser_class_name,
                data_file=data_file,
            )
            total_records_processed = execution_meta.get(
                "total_records_processed", 0
            )
            total_errors_generated = execution_meta.get(
                "total_errors_generated", 0
            )
            stale_owner = not _record_failed_parse(
                data_file,
                self.dfs,
                self.parse_token,
                "unexpected error during parsing",
                self.reparse_id,
                add_unexpected_error=True,
                event_id=self.event_id,
                extra_metadata=execution_meta,
            )
            total_errors_generated = execution_meta.get(
                "total_errors_generated", 0
            )
            return ParseResult(
                success=False,
                data_file=data_file,
                summary=self.dfs,
                status=self.dfs.status if self.dfs else None,
                error_message=error_message,
                total_records_processed=total_records_processed,
                total_errors_generated=total_errors_generated,
            )
        finally:
            if (
                data_file
                and getattr(data_file, "file", None)
                and not getattr(data_file.file, "closed", True)
            ):
                data_file.file.close()

            if not stale_owner and self.reparse_id is not None:
                _finalize_reparse(
                    data_file,
                    self.reparse_id,
                    self.file_meta,
                    self.dfs,
                    reparse_success,
                )


# Re-exports for mock patches and caller convenience
__all__ = [
    "GO_PARSER_FEATURE_FLAG",
    "GO_PARSER_POST_PARSE_TASK_NAME",
    "GO_PARSER_QUEUE",
    "GO_PARSER_TASK_NAME",
    "DataFileSummary",
    "ErrorGeneratorFactory",
    "ParseResult",
    "ParserError",
    "ParserFactory",
    "ParserModelSet",
    "ParsingService",
    "PythonParserEngine",
    "ShadowDataFileSummary",
    "ShadowParserError",
    "_add_unexpected_error",
    "_calculate_total_records",
    "_count_parser_errors",
    "_evaluate_go_parser_mode",
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
    "_program_code",
    "_record_failed_parse",
    "_reject_dfs",
    "_resolve_parse_owner",
    "_section_name",
    "_shadow_parser_models",
    "_shadow_record_model",
    "_transition_parse_outcome",
    "_uses_shadow_table",
    "case_aggregates_by_month",
    "change_log_filename",
    "finish_reparse",
    "fra_total_errors",
    "logger",
    "queue_go_parse",
    "queue_parse",
    "resolve_or_reuse_parser_mode",
    "send_data_submitted_email",
    "set_error_report",
    "should_send_reparse_notification",
    "total_errors_by_month",
    "update_dfs",
]
