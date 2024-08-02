"""Meta data model for tracking re-parsed files."""

from django.db import models, transaction
from django.db.utils import DatabaseError
from django.db.models import Max
from tdpservice.search_indexes.util import count_all_records
import logging

logger = logging.getLogger(__name__)


class ReparseMeta(models.Model):
    """
    Meta data model representing a single execution of `clean_and_reparse`.

    Because this model is intended to be queried in a distributed and parrallel fashion, all queries should rely on
    database level locking to ensure race conditions aren't introduced. See `increment_files_reparsed` for an example.
    """

    class Meta:
        """Meta class for the model."""

        verbose_name = "Re-parse Meta"

    created_at = models.DateTimeField(auto_now_add=True)

    finished = models.BooleanField(default=False)

    num_files_to_reparse = models.PositiveIntegerField(default=0)
    files_completed = models.PositiveIntegerField(default=0)
    files_failed = models.PositiveIntegerField(default=0)

    num_records_deleted = models.PositiveIntegerField(default=0)
    num_records_created = models.PositiveIntegerField(default=0)

    total_num_records_initial = models.PositiveBigIntegerField(default=0)
    total_num_records_post = models.PositiveBigIntegerField(default=0)

    db_backup_location = models.CharField(max_length=512)

    # Options used to select the files to re-parse
    fiscal_quarter = models.CharField(max_length=2, null=True)
    fiscal_year = models.PositiveIntegerField(null=True)
    all = models.BooleanField(default=False)
    new_indices = models.BooleanField(default=False)
    delete_old_indices = models.BooleanField(default=False)

    @staticmethod
    def increment_files_completed(reparse_meta_id):
        """
        Increment the count of files that have completed parsing.

        Because this function can be called in parallel we use `select_for_update` because multiple parse tasks can
        referrence the same ReparseMeta object that is being queried below. `select_for_update` provides a DB lock on
        the object and forces other transactions on the object to wait until this one completes.
        """
        if reparse_meta_id is not None:
            with transaction.commit_on_success():
                try:
                    meta = ReparseMeta.objects.select_for_update().get(pk=reparse_meta_id)
                    meta.files_completed += 1
                    if meta.files_completed == meta.num_files_to_reparse:
                        meta.finished = True
                        meta.total_num_records_post = count_all_records()
                    meta.save()
                except DatabaseError:
                    logger.exception("Encountered exception while trying to update the `files_reparsed` field on the "
                                     f"ReparseMeta object with ID: {reparse_meta_id}.")

    @staticmethod
    def increment_files_failed(reparse_meta_id):
        """
        Increment the count of files parsed the datafile's re-parse meta model.

        Because this function can be called in parallel we use `select_for_update` because multiple parse tasks can
        referrence the same ReparseMeta object that is being queried below. `select_for_update` provides a DB lock on
        the object and forces other transactions on the object to wait until this one completes.
        """
        if reparse_meta_id is not None:
            with transaction.commit_on_success():
                try:
                    meta = ReparseMeta.objects.select_for_update().get(pk=reparse_meta_id)
                    meta.num_files_failed += 1
                    meta.save()
                except DatabaseError:
                    logger.exception("Encountered exception while trying to update the `files_failed` field on the "
                                     f"ReparseMeta object with ID: {reparse_meta_id}.")

    @staticmethod
    def increment_records_created(reparse_meta_id, num_created):
        """
        Increment the count of files parsed the datafile's re-parse meta model.

        Because this function can be called in parallel we use `select_for_update` because multiple parse tasks can
        referrence the same ReparseMeta object that is being queried below. `select_for_update` provides a DB lock on
        the object and forces other transactions on the object to wait until this one completes.
        """
        if reparse_meta_id is not None:
            with transaction.commit_on_success():
                try:
                    meta = ReparseMeta.objects.select_for_update().get(pk=reparse_meta_id)
                    meta.num_records_created += num_created
                    meta.save()
                except DatabaseError:
                    logger.exception("Encountered exception while trying to update the `files_failed` field on the "
                                     f"ReparseMeta object with ID: {reparse_meta_id}.")

    @staticmethod
    def get_latest():
      """Get the ReparseMeta model with the greatest pk."""
      max_pk = ReparseMeta.objects.all().aggregate(Max('pk'))
      return ReparseMeta.objects.get(pk=max_pk["pk__max"])
