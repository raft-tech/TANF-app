"""
Delete and reparse a set of datafiles
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from tdpservice.data_files.models import DataFile
from tdpservice.scheduling import parser_task
from tdpservice.search_indexes.documents import tanf, ssp, tribal
from tdpservice.users.models import User
from tdpservice.core.utils import log
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command class."""

    help = "Delete and reparse a set of datafiles. All reparsed data will be moved into a new set of Elastic indexes."

    def add_arguments(self, parser):
        """Add arguments to the management command."""
        parser.add_argument("--fiscal_quarter", type=str)
        parser.add_argument("--fiscal_year", type=str)
        parser.add_argument("--all", action='store_true')

    def handle(self, *args, **options):
        """Delete datafiles matching a query."""
        fiscal_year = options.get('fiscal_year', None)
        fiscal_quarter = options.get('fiscal_quarter', None)
        delete_all = options.get('all', False)

        backup_file_name = f"/tmp/reparsing_backup"
        files = None
        if delete_all:
            files = DataFile.objects.all()
            print(
                f'This will delete ALL ({files.count()}) '
                'data files for ALL submission periods.'
            )
            backup_file_name += "_FY_all_Q1-4"
        else:
            if not fiscal_year and not fiscal_quarter:
                print(
                    'Options --fiscal_year and --fiscal_quarter not set. '
                    'Provide either option to continue, or --all to wipe all submissions.'
                )
                return
            files = DataFile.objects.all()
            if (fiscal_year and fiscal_quarter):
                files = files.filter(year=fiscal_year, quarter=fiscal_quarter)
                backup_file_name += f"_FY_{fiscal_year}_Q{fiscal_quarter}"
            elif fiscal_year:
                files = files.filter(year=fiscal_year)
                backup_file_name += f"_FY_{fiscal_year}_Q1-4"
            elif fiscal_quarter:
                files = files.filter(quarter=fiscal_quarter)
                backup_file_name += f"_FY_all_Q{fiscal_quarter}"
            print(
                f'This will delete {files.count()} datafiles, '
                'create new elasticsearch indices, '
                'and re-parse each of the datafiles.'
            )

        c = str(input('Continue [y/n]? ')).lower()
        if c not in ['y', 'yes']:
            print('Cancelled.')
            return

        try:
            logger.info("Begining reparse DB Backup.")
            pattern = "%d-%m-%Y_%H:%M:%S"
            backup_file_name += f"_{datetime.now().strftime(pattern)}.pg"
            call_command('backup_restore_db', '-b', '-f', f'{backup_file_name}')
            logger.info("Backup complete! Commencing clean and reparse.")
        except Exception as e:
            logger.critical('Database backup FAILED. Clean and re-parse NOT executed. Database IS consistent!')
            raise e

        call_command('tdp_search_index', '--create', '-f')

        file_ids = files.values_list('id', flat=True).distinct()

        model_types = [
            tanf.TANF_T1, tanf.TANF_T2, tanf.TANF_T3, tanf.TANF_T4, tanf.TANF_T5, tanf.TANF_T6, tanf.TANF_T7,
            ssp.SSP_M1, ssp.SSP_M2, ssp.SSP_M3, ssp.SSP_M4, ssp.SSP_M5, ssp.SSP_M6, ssp.SSP_M7,
            tribal.Tribal_TANF_T1, tribal.Tribal_TANF_T2, tribal.Tribal_TANF_T3, tribal.Tribal_TANF_T4, tribal.Tribal_TANF_T5, tribal.Tribal_TANF_T6, tribal.Tribal_TANF_T7
        ]

        for m in model_types:
            objs = m.objects.all().filter(datafile_id__in=file_ids)
            logger.info(f'Deleting {objs.count()}, {m} objects')

            # atomic delete?
            try:
                objs._raw_delete(objs.db)
            except Exception as e:
                logger.critical(f'_raw_delete failed for model {m}. Database is now inconsistent! Restore the DB from '
                                'the backup as soon as possible!')
                raise e

        logger.info(f'Deleting and reparsing {files.count()} files')
        for f in files:
            try:
                f.delete()
            except Exception as e:
                logger.error(f'DataFile.delete failed for id: {f.pk}')
                raise e

            try:
                f.save()
            except Exception as e:
                logger.error(f'DataFile.save failed for id: {f.pk}')
                raise e

            # latest version only? -> possible new ticket
            parser_task.parse.delay(f.pk, should_send_submission_email=False)
        logger.info('Done. All tasks have been queued to re-parse the selected datafiles.')
