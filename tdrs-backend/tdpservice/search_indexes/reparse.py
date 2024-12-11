# Re-write management command clean_and_reparse as a function without callinf call_command
# should include all the steps in the management command
#
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.paginator import Paginator
from django.db.utils import DatabaseError
from elasticsearch.exceptions import ElasticsearchException
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.models import DataFileSummary, ParserError
from tdpservice.scheduling import parser_task
from tdpservice.search_indexes.util import DOCUMENTS, count_all_records
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.core.utils import log
from django.contrib.admin.models import ADDITION
from tdpservice.users.models import User
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def _get_log_context(system_user):
        """Return logger context."""
        context = {'user_id': system_user.id,
                   'action_flag': ADDITION,
                   'object_repr': "Clean and Reparse"
                   }
        return context

def _assert_sequential_execution(log_context):
    """Assert that no other reparse commands are still executing."""
    latest_meta_model = ReparseMeta.get_latest()
    now = timezone.now()
    is_not_none = latest_meta_model is not None
    if (is_not_none and latest_meta_model.timeout_at is None):
        log(f"The latest ReparseMeta model's (ID: {latest_meta_model.pk}) timeout_at field is None. "
            "Cannot safely execute reparse, please fix manually.",
            logger_context=log_context,
            level='error')
        return False
    if (is_not_none and not ReparseMeta.assert_all_files_done(latest_meta_model) and
            not now > latest_meta_model.timeout_at):
        log('A previous execution of the reparse command is RUNNING. Cannot execute in parallel, exiting.',
            logger_context=log_context,
            level='warn')
        return False
    elif (is_not_none and latest_meta_model.timeout_at is not None and now > latest_meta_model.timeout_at and not
            ReparseMeta.assert_all_files_done(latest_meta_model)):
        log("Previous reparse has exceeded the timeout. Allowing execution of the command.",
            logger_context=log_context,
            level='warn')
        return True
    return True

def _should_exit(condition):
    """Exit on condition."""
    if condition:
        exit(1)

def clean_reparse(selected_file_ids):
    """Reparse selected files."""
    selected_files = [int(file_id) for file_id in selected_file_ids[0].split(",")]
    
    files = files.filter(id__in=selected_files)
    backup_file_name += "_selected_files"
    continue_msg = continue_msg.format(fy=f"selected files: {str(selected_files)}", q="Q1-4")

    num_files = files.count()

    # add fmt_str

    system_user, created = User.objects.get_or_create(username="system")
    if created:
        logger.info("Created system user")
    log_context = _get_log_context(system_user)

    all_fy = "All"
    all_q = "Q1-4"

    log(f"Starting clean_and_reparse for {num_files} files",
        logger_context=log_context,
        level=logging.INFO)
    
    is_sequential = _assert_sequential_execution(log_context)
    _should_exit(not is_sequential)

    meta_model = ReparseFileMeta.objects.create(
        fiscal_quarter=fiscal_quarter,
        fiscal_year=fiscal_year,
        all=all_reparse,
        new_indices=new_indices,
        delete_old_indices=new_indices)
    
    # Backup the Postgres DB
    backup_file_name += f"_rpv{meta_model.pk}.pg"
    _backup(backup_file_name, log_context)

    meta_model.db_backup_location = backup_file_name
    meta_model.save()

    # Create and delete Elastic indices if necessary
    _handle_elastic(new_indices, log_context)