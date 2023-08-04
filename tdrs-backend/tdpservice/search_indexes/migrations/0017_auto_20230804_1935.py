# Generated by Django 3.2.15 on 2023-08-04 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_indexes', '0016_auto_20230803_1721'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tanf_t6',
            name='adult_recipients',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='applications',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='approved',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='assistance',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='births',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='calendar_quarter',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='child_recipients',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='closed_cases',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='denied',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='families',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='fips_code',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='noncustodials',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='num_1_parents',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='num_2_parents',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='num_no_parents',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='outwedlock_births',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='recipients',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='record',
        ),
        migrations.RemoveField(
            model_name='tanf_t6',
            name='rpt_month_year',
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='CALENDAR_QUARTER',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='CALENDAR_YEAR',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_1_PARENTS',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_2_PARENTS',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_ADULT_RECIPIENTS',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_APPLICATIONS',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_APPROVED',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_ASSISTANCE',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_BIRTHS',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_CHILD_RECIPIENTS',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_CLOSED_CASES',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_DENIED',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_FAMILIES',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_NONCUSTODIALS',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_NO_PARENTS',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_OUTWEDLOCK_BIRTHS',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='NUM_RECIPIENTS',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t6',
            name='RecordType',
            field=models.CharField(max_length=156, null=True),
        ),
    ]
