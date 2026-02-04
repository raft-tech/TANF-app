"""Celery hook for parsing tasks."""

from __future__ import absolute_import

from django.conf import settings
from django.core.files import File
from django.db.utils import DatabaseError
from django.utils import timezone

from celery import shared_task

from tdpservice.data_files.error_reports import ErrorReportFactory
from tdpservice.data_files.models import DataFile, ReparseFileMeta
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
)
from tdpservice.parsers.util import DecoderUnknownException, log_parser_exception
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.users.models import AccountApprovalStatusChoices, User

logger = settings.PARSER_LOGGER


def set_reparse_file_meta_model_failed_state(reparse_id, file_meta):
    """Set ReparseFileMeta fields to indicate a parse failure."""
    if reparse_id and file_meta is not None:
        file_meta.finished = True
        file_meta.success = False
        file_meta.finished_at = timezone.now()
        file_meta.save()


def update_dfs(dfs, data_file):
    """Update DataFileSummary fields."""
    dfs.status = dfs.get_status()

    if data_file.program_type == DataFile.ProgramType.FRA:
        dfs.case_aggregates = fra_total_errors(data_file)
    else:
        if "Case Data" in data_file.section:
            dfs.case_aggregates = case_aggregates_by_month(data_file, dfs.status)
        else:
            dfs.case_aggregates = total_errors_by_month(data_file, dfs.status)
    dfs.save()


def set_error_report(dfs, error_report):
    """Update DataFileSummary error_report."""
    dfs.error_report = File(
        error_report, name=f"{dfs.datafile.original_filename}_error_report"
    )
    dfs.save()


def _start_reparse_file_meta(reparse_id, data_file_id):
    """Start tracking a reparse event if a reparse id is provided."""
    if reparse_id:
        file_meta = ReparseFileMeta.objects.get(
            data_file_id=data_file_id, reparse_meta_id=reparse_id
        )
        file_meta.started_at = timezone.now()
        file_meta.save()
        return file_meta
    return None


def _finalize_reparse_success(reparse_id, data_file_id, dfs, file_meta):
    """Finalize successful reparse metadata updates."""
    if reparse_id is None or file_meta is None:
        return
    file_meta.num_records_created = dfs.total_number_of_records_created
    file_meta.cat_4_errors_generated = ParserError.objects.filter(
        file_id=data_file_id,
        error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY,
    ).count()
    file_meta.finished = True
    file_meta.success = True
    file_meta.finished_at = timezone.now()
    file_meta.save()
    ReparseMeta.set_total_num_records_post(ReparseMeta.objects.get(pk=reparse_id))


def _send_submission_email(data_file, dfs):
    """Send submission notification to relevant data analysts."""
    qs = User.objects.filter(
        stt=data_file.stt,
        account_approval_status=AccountApprovalStatusChoices.APPROVED,
        groups__name="Data Analyst",
    )

    if data_file.program_type == DataFile.ProgramType.FRA:
        qs = qs.filter(user_permissions__codename="has_fra_access")

    recipients = qs.values_list("username", flat=True).distinct()
    send_data_submitted_email(dfs, recipients)


def _reject_dfs(dfs):
    """Mark DataFileSummary as rejected."""
    if dfs is not None:
        dfs.set_status(DataFileSummary.Status.REJECTED)
        dfs.save()


def _handle_decoder_unknown(dfs, reparse_id, file_meta):
    """Handle decode errors with reject status and reparse failure state."""
    _reject_dfs(dfs)
    set_reparse_file_meta_model_failed_state(reparse_id, file_meta)


def _handle_database_error(data_file, reparse_id, file_meta, exc):
    """Handle database exceptions during parsing."""
    if data_file is not None:
        log_parser_exception(
            data_file,
            f"Encountered Database exception in parser_task.py: \n{exc}",
            "error",
        )
    set_reparse_file_meta_model_failed_state(reparse_id, file_meta)


def _handle_generic_exception(data_file, dfs, reparse_id, file_meta):
    """Handle unexpected exceptions during parsing."""
    if data_file is not None:
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
        error.save()
        log_parser_exception(
            data_file,
            (
                f"Uncaught exception while parsing datafile: {data_file.pk}! Please review the logs to "
                f"see if manual intervention is required."
            ),
            "exception",
        )
    _reject_dfs(dfs)
    set_reparse_file_meta_model_failed_state(reparse_id, file_meta)


def _finalize_parse(data_file, dfs):
    """Generate error report and refresh aggregates after parsing."""
    error_report_generator = ErrorReportFactory.get_error_report_generator(data_file)
    error_report = error_report_generator.generate()
    set_error_report(dfs, error_report)
    logger.handlers[2].doRollover(data_file)
    update_dfs(dfs, data_file)


@shared_task
def parse(data_file_id, reparse_id=None):
    """Send data file for processing."""
    # passing the data file FileField across redis was rendering non-serializable failures, doing the below lookup
    # to avoid those. I suppose good practice to not store/serializer large file contents in memory when stored in redis
    # for undetermined amount of time.
    data_file = None
    dfs = None
    file_meta = None
    try:
        data_file = DataFile.objects.get(id=data_file_id)
        change_log_filename(logger, data_file)
        logger.info(
            f"\n\n\n __ Starting to {'re-' if reparse_id else ''}parse datafile {data_file.filename}__ \n\n\n"
        )

        file_meta = _start_reparse_file_meta(reparse_id, data_file_id)

        dfs = DataFileSummary.objects.create(
            datafile=data_file, status=DataFileSummary.Status.PENDING
        )
        parser = ParserFactory.get_instance(
            datafile=data_file,
            dfs=dfs,
            section=data_file.section,
            program_type=data_file.program_type,
            is_program_audit=data_file.is_program_audit,
        )
        parser.parse_and_validate()
        update_dfs(dfs, data_file)

        logger.info(
            f"Parsing finished for file -> {repr(data_file)} with status "
            f"{dfs.status}."
        )

        if reparse_id is not None:
            _finalize_reparse_success(reparse_id, data_file_id, dfs, file_meta)
        else:
            _send_submission_email(data_file, dfs)

    except DecoderUnknownException:
        _handle_decoder_unknown(dfs, reparse_id, file_meta)
    except DatabaseError as e:
        _handle_database_error(data_file, reparse_id, file_meta, e)
    except Exception:
        _handle_generic_exception(data_file, dfs, reparse_id, file_meta)
    finally:
        if data_file is not None:
            logger.info(f"DataFile parsing finished for file -> {repr(data_file)}.")
        if data_file is not None and dfs is not None:
            _finalize_parse(data_file, dfs)
