# Generated by Django 3.2.15 on 2022-11-02 16:39 edited by Cameron
import csv
from pathlib import Path
from ..models import STT

from django.db import migrations, models

DATA_DIR = BASE_DIR = Path(__file__).resolve().parent.parent / "management/commands/data"

def _update(path):
    with open(DATA_DIR / path) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            stt = STT.objects.get(code=row["Code"])
            stt.ssp = row["SSP"] == "0"
            stt.save()

def _update_stts(apps, schema_editor):
    _update("states.csv")
    _update("territories.csv")
    _update("tribes.csv")


class Migration(migrations.Migration):

    dependencies = [
        ('stts', '0006_alter_stt_filenames'),
    ]

    operations = [
        migrations.AddField(
            model_name='stt',
            name='ssp',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(_update_stts),
    ]
