# Re-write management command clean_and_reparse as a function without callinf call_command
# should include all the steps in the management command
from tdpservice.data_files.models import DataFile
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.core.utils import log
from django.contrib.admin.models import ADDITION
from tdpservice.users.models import User

import logging

logger = logging.getLogger(__name__)


from tdpservice.search_indexes.utils import (
    backup,
    get_log_context,
    assert_sequential_execution,
    should_exit,
    handle_elastic,
    delete_associated_models,
    count_total_num_records,
    calculate_timeout,
    handle_datafiles,
)

def clean_reparse(selected_file_ids):
    """Reparse selected files."""
    selected_files = [int(file_id) for file_id in selected_file_ids[0].split(",")]
    
    ######
    files = DataFile.objects.filter(id__in=selected_files)
    backup_file_name = "/tmp/reparsing_backup"
    backup_file_name += "_selected_files"
    continue_msg = "You have selected to reparse datafiles for FY {fy} and {q}. The reparsed files "
    continue_msg = continue_msg.format(fy=f"selected files: {str(selected_files)}", q="Q1-4")

    num_files = files.count()

    # add fmt_str

    system_user, created = User.objects.get_or_create(username="system")
    if created:
        logger.info("Created system user")
    log_context = get_log_context(system_user)

    all_fy = "All"
    all_q = "Q1-4"

    log(f"Starting clean_and_reparse for {num_files} files",
        logger_context=log_context,
        level=logging.INFO)
    
    is_sequential = assert_sequential_execution(log_context)
    should_exit(not is_sequential)

    fiscal_quarter = None
    fiscal_year = None
    all_reparse = False
    new_indices = False


    meta_model = ReparseMeta.objects.create(
        fiscal_quarter=fiscal_quarter,
        fiscal_year=fiscal_year,
        all=all_reparse,
        new_indices=new_indices,
        delete_old_indices=new_indices)
    
    # Backup the Postgres DB
    backup_file_name += f"_rpv{meta_model.pk}.pg"
    backup(backup_file_name, log_context)

    meta_model.db_backup_location = backup_file_name
    meta_model.save()

    # Create and delete Elastic indices if necessary
    handle_elastic(new_indices, log_context)

    file_ids = files.values_list('id', flat=True).distinct()
    meta_model.total_num_records_initial = count_total_num_records(log_context)
    meta_model.save()

    delete_associated_models(meta_model, file_ids, new_indices, log_context)

    meta_model.timeout_at = meta_model.created_at + calculate_timeout(
        num_files,                                                                        
        meta_model.num_records_deleted)
    
    meta_model.save()
    logger.info(f"Deleted a total of {meta_model.num_records_deleted} records across {num_files} files.")

    # Delete and re-save datafiles to handle cascading dependencies
    logger.info(f'Deleting and re-parsing {num_files} files')
    handle_datafiles(files, meta_model, log_context)

    log("Database cleansing complete and all files have been re-scheduling for parsing and validation.",
            logger_context=log_context,
            level='info')
    log(f"Clean and reparse command completed. All files for FY {fiscal_year if fiscal_year else all_fy} and "
            f"{fiscal_quarter if fiscal_quarter else all_q} have been queued for parsing.",
            logger_context=log_context,
            level='info')
    logger.info('Done. All tasks have been queued to parse the selected datafiles.')