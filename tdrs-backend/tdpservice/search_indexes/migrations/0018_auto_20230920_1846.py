# Generated by Django 3.2.15 on 2023-09-20 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_indexes', '0017_auto_20230914_1720'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tanf_t7',
            name='calendar_quarter',
        ),
        migrations.RemoveField(
            model_name='tanf_t7',
            name='families',
        ),
        migrations.RemoveField(
            model_name='tanf_t7',
            name='fips_code',
        ),
        migrations.RemoveField(
            model_name='tanf_t7',
            name='record',
        ),
        migrations.RemoveField(
            model_name='tanf_t7',
            name='rpt_month_year',
        ),
        migrations.RemoveField(
            model_name='tanf_t7',
            name='stratum',
        ),
        migrations.RemoveField(
            model_name='tanf_t7',
            name='tdrs_section_ind',
        ),
        migrations.AddField(
            model_name='tanf_t7',
            name='CALENDAR_QUARTER',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t7',
            name='FAMILIES_MONTH',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t7',
            name='RPT_MONTH_YEAR',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t7',
            name='RecordType',
            field=models.CharField(max_length=156, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t7',
            name='STRATUM',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t7',
            name='TDRS_SECTION_IND',
            field=models.CharField(max_length=1, null=True),
        ),
    ]
