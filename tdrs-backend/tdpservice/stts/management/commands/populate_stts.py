"""`populate_stts` command."""

import csv
import json
import logging
from pathlib import Path

from django.core.management import BaseCommand
from django.utils import timezone

from tdpservice.data_files.models import Program

from ...models import STT, Region, SttProgramParticipation

DATA_DIR = BASE_DIR = Path(__file__).resolve().parent / "data"
logger = logging.getLogger(__name__)
SSP_PROGRAM_SLUG = "ssp"
SSP_PROGRAM_CODE = "SSP"
SSP_PROGRAM_NAME = "SSP"


def _populate_regions():
    with open(DATA_DIR / "regions.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Region.objects.get_or_create(id=row["Id"], name=row["name"])
        Region.objects.get_or_create(id=1000, name=None)


def _load_csv(filename, entity):
    with open(DATA_DIR / filename) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            stt, stt_created = STT.objects.get_or_create(name=row["Name"])
            if stt_created:  # These lines are spammy, should remove before merge
                logger.debug("Created new entry for " + row["Name"])

            stt.postal_code = row["Code"]
            stt.region_id = row["Region"]
            if filename == "tribes.csv":
                stt.state = STT.objects.get(
                    postal_code=row["Code"], type=STT.EntityType.STATE
                )

            chars = 3 if entity == STT.EntityType.TRIBE else 2
            stt.stt_code = str(row["STT_CODE"]).zfill(chars)

            stt.type = entity
            stt.filenames = json.loads(row["filenames"].replace("'", '"'))
            stt.ssp = _maybe_bool(row["SSP"])
            stt.sample = row["Sample"]
            if "Timezone" in row and row["Timezone"]:
                stt.timezone = row["Timezone"]
            # TODO: Was seeing lots of references to STT.objects.filter(pk=...
            #       We could probably one-line this but we'd miss .save() signals
            #       https://stackoverflow.com/questions/41744096/
            # TODO: we should finish the last columns from the csvs: Sample, SSN_Encrypted
            stt.save()
            _sync_ssp_participation(
                stt,
                row["SSP"],
                inactive_status=SttProgramParticipation.Status.NEVER,
            )


def _maybe_bool(value):
    """Convert common string boolean values to actual booleans."""
    if isinstance(value, str):
        return value.lower() in ("1", "true", "t", "yes", "y")
    return value


def _get_ssp_program():
    """Return the SSP program record."""
    program, _ = Program.objects.get_or_create(
        slug=SSP_PROGRAM_SLUG,
        defaults={"code": SSP_PROGRAM_CODE, "name": SSP_PROGRAM_NAME},
    )
    return program


def _normalize_ssp_status(
    value, inactive_status=SttProgramParticipation.Status.FORMER
):
    """Map SSP override values to participation status values."""
    if isinstance(value, str):
        normalized = value.upper()
        if normalized in SttProgramParticipation.Status.values:
            return normalized
        return (
            SttProgramParticipation.Status.ACTIVE
            if _maybe_bool(value)
            else inactive_status
        )

    if value is True:
        return SttProgramParticipation.Status.ACTIVE
    if value is False:
        return inactive_status
    return SttProgramParticipation.Status.NEVER


def _sync_ssp_participation(
    stt, value, inactive_status=SttProgramParticipation.Status.FORMER
):
    """Create, update, or remove SSP participation for an STT."""
    status = _normalize_ssp_status(value, inactive_status=inactive_status)
    program = _get_ssp_program()

    if status == SttProgramParticipation.Status.NEVER:
        SttProgramParticipation.objects.filter(stt=stt, program=program).delete()
        return

    SttProgramParticipation.objects.update_or_create(
        stt=stt,
        program=program,
        defaults={"status": status},
    )


def _get_override_path(overrides_path):
    return Path(overrides_path) if overrides_path else DATA_DIR / "stt_overrides.json"


def _find_stt_for_override(override):
    """Find an STT to update using name or postal_code (optionally type)."""
    name = override.get("name") or override.get("Name")
    if name:
        return STT.objects.filter(name=name).first()

    postal_code = override.get("postal_code") or override.get("Code")
    if not postal_code:
        return None

    lookup = {"postal_code": postal_code}
    stt_type = override.get("type")
    if stt_type:
        lookup["type"] = stt_type
    return STT.objects.filter(**lookup).first()


def _apply_overrides(overrides_path=None):
    """
    Apply overrides from a JSON file.

        The override file should be a list of objects. Each object must provide a
        lookup key (`name` or `postal_code`) and any fields to override (e.g., `ssp`,
        `sample`, `filenames`, `region_id`, `stt_code`, `type`, `postal_code`). SSP
        overrides also update SSP program participation: true is ACTIVE, false is
        FORMER, and "NEVER" removes the participation row.
    """
    path = _get_override_path(overrides_path)
    if not path.exists():
        logger.info("No STT overrides found at %s; skipping.", path)
        return

    with open(path) as overrides_file:
        overrides = json.load(overrides_file)

    for override in overrides:
        stt = _find_stt_for_override(override)
        if not stt:
            logger.warning("No STT found for override: %s", override)
            continue

        # Only override fields explicitly provided
        bool_fields = {"sample"}
        for field in [
            "sample",
            "filenames",
            "region_id",
            "stt_code",
            "type",
            "postal_code",
            "timezone",
        ]:
            if field in override:
                value = _maybe_bool(override[field]) if field in bool_fields else override[field]
                setattr(stt, field, value)

        if "ssp" in override:
            status = _normalize_ssp_status(override["ssp"])
            stt.ssp = status == SttProgramParticipation.Status.ACTIVE

        stt.save()
        if "ssp" in override:
            _sync_ssp_participation(stt, override["ssp"])
        logger.info("Applied override for STT %s", stt.name)


class Command(BaseCommand):
    """Command class."""

    help = "Populate regions, states, territories, and tribes."

    def add_arguments(self, parser):
        """Register command-line arguments for the populate_stts command."""
        parser.add_argument(
            "--apply-overrides",
            action="store_true",
            help="Apply overrides from stt_overrides.json (or --overrides path).",
        )
        parser.add_argument(
            "--overrides",
            type=str,
            default=None,
            help="Optional path to an overrides JSON file.",
        )

    def handle(self, *args, **options):
        """Populate the various regions, states, territories, and tribes."""
        _populate_regions()

        stt_map = [
            ("states.csv", STT.EntityType.STATE),
            ("territories.csv", STT.EntityType.TERRITORY),
            ("tribes.csv", STT.EntityType.TRIBE),
        ]

        for datafile, entity in stt_map:
            _load_csv(datafile, entity)

        if options.get("apply_overrides"):
            _apply_overrides(options.get("overrides"))

        logger.info("STT import executed by Admin at %s", timezone.now())
