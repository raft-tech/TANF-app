# Generated by Django 3.2.15 on 2022-11-04 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_files', '0011_alter_datafile_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafile',
            name='file_type',
            field=models.CharField(default='tanf', max_length=32),
        ),
    ]
