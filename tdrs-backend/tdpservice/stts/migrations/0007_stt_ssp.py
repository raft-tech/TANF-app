# Generated by Django 3.2.15 on 2022-11-02 16:39

from django.db import migrations, models


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
    ]
