# Generated by Django 3.2.15 on 2022-10-31 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    run_before = [
        ('stts', '0006_alter_stt_filenames'),
    ]

    operations = [
        migrations.AddField(
            model_name='stt',
            name='ssp',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
