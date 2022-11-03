"""`populate_stts` command."""

import csv
import json
import logging
from pathlib import Path

from django.core.management import BaseCommand
from django.utils import timezone

from ...models import STT, Region

DATA_DIR = BASE_DIR = Path(__file__).resolve().parent / "data"
logger = logging.getLogger(__name__)


def _populate_regions():
    with open(DATA_DIR / "regions.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Region.objects.get_or_create(id=row["Id"])
        Region.objects.get_or_create(id=1000)


def _get_states():
    with open(DATA_DIR / "states.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        return [
            STT(
                code=row["Code"],
                name=row["Name"],
                region_id=row["Region"],
                type=STT.EntityType.STATE,
                filenames=json.loads(row["filenames"].replace('\'', '"')),
                stt_code=row["STT_CODE"],
            )
            for row in reader
        ]



def _get_territories():
    with open(DATA_DIR / "territories.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        return [
            STT(
                code=row["Code"],
                name=row["Name"],
                region_id=row["Region"],
                type=STT.EntityType.TERRITORY,
                filenames=json.loads(row["filenames"].replace('\'', '"')),
                stt_code=row["STT_CODE"],
            )
            for row in reader
        ]


def _populate_tribes():
    with open(DATA_DIR / "tribes.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        stts = [
            STT(
                name=row["Name"],
                region_id=row["Region"],
                state=STT.objects.get(code=row["Code"]),
                type=STT.EntityType.TRIBE,
                filenames=json.loads(row["filenames"].replace('\'', '"')),
                stt_code=row["STT_CODE"],
            )
            for row in reader
        ]
        STT.objects.bulk_create(stts, ignore_conflicts=True)

def _load_csv(filename, entity):
    with open(DATA_DIR / filename) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            stt, stt_created = STT.objects.get_or_create(name=row["Name"])
            if stt_created:
                logger.debug("Created new entry for " + row["Name"])
            else:
                logger.debug("Found STT " + row["Name"] + ", will sync with data csv.")

            stt.code = row["Code"]
            stt.region_id = row["Region"]
            if filename == "tribes.csv":
                stt.state = STT.objects.get(code=row["Code"], type=STT.EntityType.STATE)

            stt.type = entity
            stt.filenames = json.loads(row["filenames"].replace('\'', '"'))
            stt.stt_code = row["STT_CODE"]
            stt.ssp = row["SSP"]
            # TODO: Was seeing lots of references to STT.objects.filter(pk=...
            #       We could probably one-line this but we'd miss .save() signals
            #       https://stackoverflow.com/questions/41744096/
            # TODO: we should finish the last columns from the csvs: Sample, SSN_Encrypted
            stt.save()


class Command(BaseCommand):
    """Command class."""

    help = "Populate regions, states, territories, and tribes."

    def handle(self, *args, **options):
        """Populate the various regions, states, territories, and tribes."""
        _populate_regions()


        stt_map = [
            ("states.csv", STT.EntityType.STATE),
            ("territories.csv", STT.EntityType.TERRITORY),
            ("tribes.csv", STT.EntityType.TRIBE)
        ]

        for csv, entity in stt_map:
            stts = _load_csv(csv, entity)

        #stts = _get_states()
        #stts.extend(_get_territories())
        #STT.objects.bulk_create(stts, ignore_conflicts=True)

        #_populate_tribes()
        logger.info("STT import executed by Admin at %s", timezone.now())
