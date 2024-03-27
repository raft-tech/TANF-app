# Generated by Django 3.2.15 on 2024-02-28 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0009_alter_datafilesummary_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafilesummary',
            name='total_number_of_records_created',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='datafilesummary',
            name='total_number_of_records_in_file',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
