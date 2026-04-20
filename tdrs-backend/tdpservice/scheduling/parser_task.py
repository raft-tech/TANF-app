"""Celery hook for parsing tasks."""

from __future__ import absolute_import

from django.conf import settings
from django.core.files import File
from django.db.utils import DatabaseError
from django.utils import timezone

from celery import shared_task

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.error_reports import ErrorReportFactory
from tdpservice.data_files.models import DataFile, ReparseFileMeta
from tdpservice.data_files.submission_lifecycle import transition_datafile
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


def set_reparse_file_meta_model_state(reparse_id, file_meta, is_success):
    """Set ReparseFileMeta fields to indicate a parse failure."""
    if reparse_id:
        file_meta.finished = True
        file_meta.success = is_success
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


def _transition_parse_outcome(data_file, dfs):
    """Transition DataFile state based on parse outcome (initial submissions only)."""
    if dfs.status == DataFileSummary.Status.ACCEPTED:
        transition_datafile(
            data_file,
            SubmissionState.PARSE_COMPLETED,
            note="parsing completed successfully",
        )
    elif dfs.status in (
        DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
        DataFileSummary.Status.PARTIALLY_ACCEPTED,
    ):
        transition_datafile(
            data_file,
            SubmissionState.PARSED_WITH_ERRORS,
            note="parsing completed with errors",
        )
    elif dfs.status == DataFileSummary.Status.REJECTED:
        transition_datafile(
            data_file,
            SubmissionState.PARSE_FAILED,
            note="file rejected during parsing",
        )


def _notify_data_analysts(data_file, dfs):
    """Send submission email to relevant data analysts (initial submissions only)."""
    qs = User.objects.filter(
        stt=data_file.stt,
        account_approval_status=AccountApprovalStatusChoices.APPROVED,
        groups__name="Data Analyst",
    )

    if data_file.program_type == DataFile.ProgramType.FRA:
        qs = qs.filter(user_permissions__codename="has_fra_access")

    recipients = qs.values_list("username", flat=True).distinct()
    send_data_submitted_email(dfs, recipients)


def _handle_parse_failure(data_file, reparse_id, note):
    """Transition to PARSE_FAILED for initial submissions."""
    if reparse_id is None:
        transition_datafile(
            data_file,
            SubmissionState.PARSE_FAILED,
            note=note,
        )


@shared_task
def parse(data_file_id, reparse_id=None):
    """Send data file for processing."""
    # passing the data file FileField across redis was rendering non-serializable failures, doing the below lookup
    # to avoid those. I suppose good practice to not store/serializer large file contents in memory when stored in redis
    # for undetermined amount of time.
    dfs = None
    try:
        data_file = DataFile.objects.get(id=data_file_id)
        change_log_filename(logger, data_file)
        logger.info(
            f"\n\n\n __ Starting to {'re-' if reparse_id else ''}parse datafile {data_file.filename}__ \n\n\n"
        )

        file_meta = None
        reparse_success = True
        if reparse_id:
            file_meta = ReparseFileMeta.objects.get(
                data_file_id=data_file_id, reparse_meta_id=reparse_id
            )
            file_meta.started_at = timezone.now()
            file_meta.save()

        if reparse_id is None:
            transition_datafile(
                data_file,
                SubmissionState.PARSE_STARTED,
                note="parser worker started",
            )

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

        logger.info(f"Parsing finished for file -> {repr(data_file)}.")

        if reparse_id is None:
            _transition_parse_outcome(data_file, dfs)
            _notify_data_analysts(data_file, dfs)

    except DecoderUnknownException:
        if dfs is not None:
            dfs.set_status(DataFileSummary.Status.REJECTED)
            dfs.save()
        _handle_parse_failure(data_file, reparse_id, "decoder unknown exception")
        reparse_success = False
    except DatabaseError as e:
        log_parser_exception(
            data_file,
            f"Encountered Database exception in parser_task.py: \n{e}",
            "error",
        )
        _handle_parse_failure(data_file, reparse_id, "database error during parsing")
        reparse_success = False
    except Exception:
        if dfs is None:
            raise

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
        if dfs is not None:
            dfs.set_status(DataFileSummary.Status.REJECTED)
            dfs.save()
        log_parser_exception(
            data_file,
            (
                f"Uncaught exception while parsing datafile: {data_file.pk}! Please review the logs to "
                f"see if manual intervention is required."
            ),
            "exception",
        )
        _handle_parse_failure(data_file, reparse_id, "unexpected error during parsing")
        reparse_success = False
    finally:
        logger.info(f"DataFile parsing finished for file -> {repr(data_file)}.")
        if dfs is not None:
            error_report_generator = ErrorReportFactory.get_error_report_generator(
                data_file
            )
            error_report = error_report_generator.generate()
            set_error_report(dfs, error_report)
            logger.handlers[2].doRollover(data_file)
            update_dfs(dfs, data_file)

        if reparse_id is not None:
            file_meta.num_records_created = dfs.total_number_of_records_created
            file_meta.cat_4_errors_generated = ParserError.objects.filter(
                file_id=data_file_id,
                error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY,
            ).count()
            ReparseMeta.set_total_num_records_post(
                ReparseMeta.objects.get(pk=reparse_id)
            )
            set_reparse_file_meta_model_state(reparse_id, file_meta, reparse_success)
