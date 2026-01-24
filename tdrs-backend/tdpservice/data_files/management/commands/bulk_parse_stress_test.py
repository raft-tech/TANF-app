"""Stress test command to parse files N times."""

import logging

from django.core.management.base import BaseCommand

from tdpservice.data_files.models import DataFile
from tdpservice.parsers.models import DataFileSummary
from tdpservice.scheduling import parser_task

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to stress test parsing by creating and parsing DataFiles N times."""

    help = "Create N copies of specified DataFile(s) and parse each for stress testing."

    def add_arguments(self, parser):
        """Add arguments to the management command."""
        parser.add_argument(
            "-f",
            "--files",
            type=str,
            required=True,
            help="Comma-separated list of DataFile IDs to use as source files.",
        )
        parser.add_argument(
            "-n",
            "--count",
            type=int,
            default=1,
            help="Number of copies to create and parse per source file (default: 1).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without actually creating files or queuing tasks.",
        )

    def handle(self, *args, **options):
        """Create DataFile copies and queue them for parsing."""
        file_ids_str = options["files"]
        count = options["count"]
        dry_run = options.get("dry_run", False)

        # Parse file IDs
        file_ids = [int(f.strip()) for f in file_ids_str.split(",")]

        # Get source files
        source_files = DataFile.objects.filter(pk__in=file_ids)
        found_ids = set(source_files.values_list("pk", flat=True))
        missing_ids = set(file_ids) - found_ids

        if missing_ids:
            self.stderr.write(
                self.style.WARNING(f"DataFile IDs not found: {missing_ids}")
            )

        if not source_files.exists():
            self.stderr.write(self.style.ERROR("No valid DataFiles found."))
            return

        self.stdout.write("\nSource files:")
        for f in source_files:
            self.stdout.write(
                f"  [{f.pk}] {f.original_filename} - {f.stt} - {f.section}"
            )

        total_files = source_files.count() * count
        self.stdout.write(f"\nTotal new DataFiles to create and parse: {total_files}")
        self.stdout.write(f"  ({source_files.count()} source files × {count} copies)")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("\n[DRY RUN] No files will be created.")
            )
            return

        # Confirm
        confirm = input(f"\nCreate {total_files} DataFiles and queue for parsing? [y/N] ")
        if confirm.lower() not in ["y", "yes"]:
            self.stdout.write("Cancelled.")
            return

        for source_file in source_files:
            for i in range(count):
                try:
                    # Create new DataFile with incremented version
                    new_file = DataFile.create_new_version({
                        "original_filename": source_file.original_filename,
                        "slug": f"{source_file.slug}-stress-{i}",
                        "extension": source_file.extension,
                        "section": source_file.section,
                        "program_type": source_file.program_type,
                        "quarter": source_file.quarter,
                        "year": source_file.year,
                        "user": source_file.user,
                        "stt": source_file.stt,
                        "file": source_file.file,
                        "s3_versioning_id": source_file.s3_versioning_id,
                        "is_program_audit": source_file.is_program_audit,
                    })

                    # Queue parse task
                    parser_task.parse.delay(new_file.pk)


                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Error creating file from source {source_file.pk} "
                            f"(iteration {i}): {e}"
                        )
                    )
