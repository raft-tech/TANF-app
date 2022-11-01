# Generated by Django 3.2.13 on 2022-06-08 14:43

import csv
import json
from pathlib import Path

from django.core.management import call_command
from django.db import migrations, models



class Migration(migrations.Migration):

    dependencies = [
        ('stts', '0005_stt_stt_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stt',
            name='filenames',
            field=models.JSONField(blank=True, max_length=512, null=True),
        ),
    ]

