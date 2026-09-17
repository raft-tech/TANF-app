"""ParsingService for single-DataFile processing and lifecycle orchestration."""

import logging
import uuid
from contextlib import nullcontext
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Union
from uuid import UUID

from django.apps import apps
from django.core.files import File
from django.db.models import Case, Count, IntegerField, When
from django.db.utils import DatabaseError

from tdpservice.data_files.enums import GoParserMode, SubmissionState
from tdpservice.data_files.error_reports import ErrorReportFactory
from tdpservice.data_files.models import (
    DataFile,
    ReparseFileMeta,
    ShadowDataFile,
)
from tdpservice.data_files.submission_lifecycle import (
    PARSE_QUEUEABLE_STATES,
    StaleParseOwnership,
    begin_parse,
    claim_parse,
    finish_reparse,
    parse_write_scope,
    record_parse_failure,
    record_parse_outcome,
)
from tdpservice.email.helpers.data_file import send_data_submitted_email
from tdpservice.log_handler import change_log_filename
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
    ParserErrorCategoryChoices,
    ShadowDataFileSummary,
    ShadowParserError,
)
from tdpservice.parsers.util import DecoderUnknownException, log_parser_exception
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.users.models import AccountApprovalStatusChoices, User

logger = logging.getLogger("tdpservice.parsers")


@dataclass(frozen=True)
class ParserModelSet:
    """Models and lookup hooks for a parser output table family."""

    data_file_model: type
    summary_model: type
    parser_error_model: type
    record_model_resolver: Callable[[type], type]
    label: str


@dataclass
class ParseResult:
    """Structured result of a single DataFile parsing execution."""

    success: bool
    data_file: Optional[DataFile] = None
    summary: Optional[DataFileSummary] = None
    status: Optional[str] = None
    errors: list[Any] = field(default_factory=list)
    error_message: Optional[str] = None


def _shadow_record_model(production_model):
    """Return the Django model for the Go parser shadow copy of a record table."""
    shadow_table_name = f"shadow_{production_model._meta.db_table}"
    for model in apps.get_app_config("search_indexes").get_models():
        if model._meta.db_table == shadow_table_name:
            return model
    raise LookupError(
        f"No shadow model found for table {production_model._meta.db_table}"
    )


def _production_parser_models():
    """Return parser models for production parser output."""
    return ParserModelSet(
        data_file_model=DataFile,
        summary_model=DataFileSummary,
        parser_error_model=ParserError,
        record_model_resolver=lambda production_model: production_model,
        label="production",
    )


def _shadow_parser_models():
    """Return parser models for Go parser shadow output."""
    return ParserModelSet(
        data_file_model=ShadowDataFile,
        summary_model=ShadowDataFileSummary,
        parser_error_model=ShadowParserError,
        record_model_resolver=_shadow_record_model,
        label="shadow",
    )


def _uses_shadow_table(model_or_instance):
    """Return whether a model or instance belongs to a shadow table family."""
    return model_or_instance._meta.db_table.startswith("shadow_")


def _parse_write_scope(data_file, parse_token=None):
    """Return an ownership fence for production parser writes."""
    if parse_token is None or _uses_shadow_table(data_file):
        return nullcontext()
    return parse_write_scope(data_file.id, parse_token)


def _parser_models_for_instance(model_or_instance):
    """Return the model set matching the table family of a model or instance."""
    if _uses_shadow_table(model_or_instance):
        return _shadow_parser_models()
    return _production_parser_models()


def _parser_models_for_mode(table_mode: str | None) -> ParserModelSet:
    """Return the exact table family selected when the task was dispatched."""
    if table_mode == GoParserMode.GO_SHADOW.value:
        return _shadow_parser_models()
    if table_mode == GoParserMode.GO_ONLY.value:
        return _production_parser_models()
    raise ValueError(f"Unsupported Go parser table mode: {table_mode!r}")


def _resolve_parse_owner(data_file, reparse_id=None, parse_token=None):
    """Resolve one task's reparse metadata and exclusive ownership token."""
    file_meta = None
    if reparse_id:
        file_meta = ReparseFileMeta.objects.get(
            data_file_id=data_file.id,
            reparse_meta_id=reparse_id,
        )
    if parse_token is None:
        parse_token = claim_parse(data_file, reparse_file_meta=file_meta)
    return file_meta, str(parse_token)


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

    if data_file.program_type == DataFile.ProgramType.FRA:
        dfs.case_aggregates = fra_total_errors(
            data_file, parser_error_model=parser_error_model
        )
    else:
        if "Case Data" in data_file.section:
            dfs.case_aggregates = case_aggregates_by_month(
                data_file,
                dfs.status,
                parser_error_model=parser_error_model,
                record_model_resolver=record_model_resolver,
            )
        else:
            dfs.case_aggregates = total_errors_by_month(
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


def _transition_parse_outcome(data_file, dfs, parse_token, reparse_id=None, event_id=None):
    """Report a parse outcome to the lifecycle controller."""
    parse_context = {
        "section": data_file.section,
        "program_type": data_file.program_type,
        "parse_summary_status": dfs.status,
        "reparse_id": reparse_id,
    }

    record_parse_outcome(
        data_file,
        parse_token,
        dfs.status,
        log_fields=parse_context,
        event_id=event_id,
        reparse_meta_id=reparse_id,
    )


def should_send_reparse_notification(dfs, file_meta, reparse_id):
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
    qs = User.objects.filter(
        stt=data_file.stt,
        account_approval_status=AccountApprovalStatusChoices.APPROVED,
        groups__name="Data Analyst",
    )

    if data_file.program_type == DataFile.ProgramType.FRA:
        qs = qs.filter(user_permissions__codename="has_fra_access")

    recipients = qs.values_list("username", flat=True).distinct()
    if should_send_reparse_notification(dfs, file_meta, reparse_id):
        send_data_submitted_email(
            dfs, recipients, is_reprocessed=(reparse_id is not None)
        )


def _handle_parse_failure(
    data_file, parse_token, note, reparse_id=None, event_id=None, actor="python_parser"
):
    """Report a technical parser failure to the lifecycle controller."""
    return record_parse_failure(
        data_file,
        parse_token,
        note=note,
        event_id=event_id,
        reparse_meta_id=reparse_id,
        actor=actor,
        log_fields={
            "section": data_file.section,
            "program_type": data_file.program_type,
            "reparse_id": reparse_id,
            **({"parse_error": note} if actor == "go_parser" else {}),
        },
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

    finalized = finish_reparse(
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
    generate_error = ErrorGeneratorFactory(data_file).get_generator(
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


def _record_failed_parse(
    data_file,
    dfs,
    parse_token,
    note,
    reparse_id=None,
    add_unexpected_error=False,
    event_id=None,
):
    """Best-effort failure artifacts, followed by the authoritative outcome."""
    try:
        if add_unexpected_error and data_file is not None:
            _add_unexpected_error(data_file, parse_token=parse_token)
        if dfs is not None:
            _reject_dfs(dfs, parse_token=parse_token)
            _finalize_parse(data_file, dfs, parse_token=parse_token)
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
    if data_file is not None and parse_token is not None:
        return _handle_parse_failure(data_file, parse_token, note, reparse_id, event_id)
    return False


class ParsingService:
    """Service for orchestrating the parsing flow of a single DataFile."""

    def __init__(
        self,
        data_file_id: Optional[int] = None,
        data_file: Optional[DataFile] = None,
        reparse_id: Optional[int] = None,
        parse_token: Optional[Union[str, UUID]] = None,
        event_id: Optional[Union[str, UUID]] = None,
        file_meta: Optional[ReparseFileMeta] = None,
    ):
        self.data_file_id = data_file_id or (data_file.id if data_file else None)
        self.data_file = data_file
        self.reparse_id = reparse_id
        self.parse_token = str(parse_token) if parse_token else None
        self.event_id = str(event_id or uuid.uuid4())
        self.file_meta = file_meta
        self.dfs: Optional[DataFileSummary] = None

    def fetch_data_file(self) -> DataFile:
        """Fetch the target DataFile if not already populated."""
        if self.data_file is None:
            if self.data_file_id is None:
                raise ValueError("Neither data_file nor data_file_id was provided.")
            self.data_file = DataFile.objects.get(id=self.data_file_id)
        return self.data_file

    def validate_preconditions(self) -> None:
        """Validate preconditions for parsing the target DataFile.

        Checks:
        1. File existence (DataFile has an associated file).
        2. Valid submission state for parsing.
        3. Idempotency / parse token ownership guard.
        """
        data_file = self.fetch_data_file()

        if not data_file.file or not getattr(data_file.file, "name", None):
            raise ValueError(f"DataFile {data_file.id} does not have an associated file.")

        valid_states = PARSE_QUEUEABLE_STATES | {SubmissionState.PARSE_STARTED}
        if data_file.state not in valid_states:
            state_val = getattr(data_file.state, "value", str(data_file.state))
            raise ValueError(
                f"Cannot queue parsing for DataFile {data_file.id} from state '{state_val}'."
            )

        if self.parse_token and data_file.current_parse_token:
            if str(data_file.current_parse_token) != str(self.parse_token):
                raise StaleParseOwnership(
                    f"DataFile {data_file.id} has an active parse token {data_file.current_parse_token} "
                    f"which does not match provided token {self.parse_token}."
                )

    def get_parser(self):
        """Construct and return the appropriate parser instance."""
        data_file = self.fetch_data_file()
        return ParserFactory.get_instance(
            datafile=data_file,
            dfs=self.dfs,
            section=data_file.section,
            program_type=data_file.program_type,
            is_program_audit=data_file.is_program_audit,
            parse_token=self.parse_token,
        )

    def parse(self) -> ParseResult:
        """Alias for run()."""
        return self.run()

    def run(self) -> ParseResult:
        """Execute parsing flow for the target DataFile and return a ParseResult."""
        data_file = None
        reparse_success = True
        stale_owner = False
        error_message = None

        try:
            data_file = self.fetch_data_file()
            self.validate_preconditions()

            change_log_filename(logger, data_file)
            logger.info(
                f"\n\n\n __ Starting to {'re-' if self.reparse_id else ''}parse datafile {data_file.filename}__ \n\n\n"
            )

            self.file_meta, self.parse_token = _resolve_parse_owner(
                data_file,
                self.reparse_id,
                self.parse_token,
            )

            begin_parse(data_file, self.parse_token, self.file_meta, event_id=self.event_id)

            with _parse_write_scope(data_file, self.parse_token):
                self.dfs = DataFileSummary.objects.create(
                    datafile=data_file, status=DataFileSummary.Status.PENDING
                )

            parser = self.get_parser()
            parser.parse_and_validate()
            update_dfs(self.dfs, data_file, parse_token=self.parse_token)

            logger.info(f"Parsing finished for file -> {repr(data_file)}.")

            _finalize_parse(data_file, self.dfs, parse_token=self.parse_token)
            _transition_parse_outcome(data_file, self.dfs, self.parse_token, self.reparse_id, self.event_id)

            try:
                _notify_data_analysts(data_file, self.dfs, self.file_meta, self.reparse_id)
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
                errors=list(data_file.parser_errors.all()) if data_file else [],
                error_message=None,
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
            )
        except DecoderUnknownException as exc:
            reparse_success = False
            error_message = str(exc) or "decoder unknown exception"
            logger.warning(
                "DecoderUnknownException during parse",
                extra={
                    "data_file_id": self.data_file_id,
                    "section": getattr(data_file, "section", None),
                    "program_type": getattr(data_file, "program_type", None),
                    "reparse_id": self.reparse_id,
                },
            )
            stale_owner = not _record_failed_parse(
                data_file,
                self.dfs,
                self.parse_token,
                "decoder unknown exception",
                self.reparse_id,
                event_id=self.event_id,
            )
            return ParseResult(
                success=False,
                data_file=data_file,
                summary=self.dfs,
                status=self.dfs.status if self.dfs else None,
                error_message=error_message,
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
                    "section": getattr(data_file, "section", None),
                    "program_type": getattr(data_file, "program_type", None),
                    "reparse_id": self.reparse_id,
                },
            )
            stale_owner = not _record_failed_parse(
                data_file,
                self.dfs,
                self.parse_token,
                "database error during parsing",
                self.reparse_id,
                event_id=self.event_id,
            )
            return ParseResult(
                success=False,
                data_file=data_file,
                summary=self.dfs,
                status=self.dfs.status if self.dfs else None,
                error_message=error_message,
            )
        except Exception as e:
            reparse_success = False
            error_message = str(e) or "unexpected error during parsing"
            if data_file is None or self.parse_token is None:
                # If we failed before resolving data_file or token (e.g. precondition / DoesNotExist)
                logger.exception(
                    "Exception during parse before ownership establishment: %s", e,
                    extra={"data_file_id": self.data_file_id},
                )
                return ParseResult(
                    success=False,
                    data_file=data_file,
                    summary=self.dfs,
                    status=None,
                    error_message=error_message,
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
                    "section": getattr(data_file, "section", None),
                    "program_type": getattr(data_file, "program_type", None),
                    "reparse_id": self.reparse_id,
                },
            )
            stale_owner = not _record_failed_parse(
                data_file,
                self.dfs,
                self.parse_token,
                "unexpected error during parsing",
                self.reparse_id,
                add_unexpected_error=True,
                event_id=self.event_id,
            )
            return ParseResult(
                success=False,
                data_file=data_file,
                summary=self.dfs,
                status=self.dfs.status if self.dfs else None,
                error_message=error_message,
            )
        finally:
            if not stale_owner and self.reparse_id is not None:
                _finalize_reparse(
                    data_file,
                    self.reparse_id,
                    self.file_meta,
                    self.dfs,
                    reparse_success,
                )
