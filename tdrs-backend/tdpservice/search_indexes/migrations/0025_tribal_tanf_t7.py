# Generated by Django 3.2.15 on 2023-11-29 19:49

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('data_files', '0012_datafile_s3_versioning_id'),
        ('search_indexes', '0024_tribal_tanf_t6'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tribal_TANF_T7',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('RecordType', models.CharField(max_length=156, null=True)),
                ('CALENDAR_QUARTER', models.IntegerField(blank=True, null=True)),
                ('RPT_MONTH_YEAR', models.IntegerField(null=True)),
                ('TDRS_SECTION_IND', models.CharField(max_length=1, null=True)),
                ('STRATUM', models.CharField(max_length=2, null=True)),
                ('FAMILIES_MONTH', models.IntegerField(null=True)),
                ('datafile', models.ForeignKey(blank=True, help_text='The parent file from which this record was created.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tribal_t7_parent', to='data_files.datafile')),
            ],
        ),
    ]
