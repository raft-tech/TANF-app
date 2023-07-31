# Generated by Django 3.2.15 on 2023-07-24 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_indexes', '0014_auto_20230707_1952'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tanf_t4',
            name='case_number',
        ),
        migrations.RemoveField(
            model_name='tanf_t4',
            name='closure_reason',
        ),
        migrations.RemoveField(
            model_name='tanf_t4',
            name='county_fips_code',
        ),
        migrations.RemoveField(
            model_name='tanf_t4',
            name='disposition',
        ),
        migrations.RemoveField(
            model_name='tanf_t4',
            name='fips_code',
        ),
        migrations.RemoveField(
            model_name='tanf_t4',
            name='rec_food_stamps',
        ),
        migrations.RemoveField(
            model_name='tanf_t4',
            name='rec_med_assist',
        ),
        migrations.RemoveField(
            model_name='tanf_t4',
            name='rec_sub_cc',
        ),
        migrations.RemoveField(
            model_name='tanf_t4',
            name='rec_sub_housing',
        ),
        migrations.RemoveField(
            model_name='tanf_t4',
            name='record',
        ),
        migrations.RemoveField(
            model_name='tanf_t4',
            name='rpt_month_year',
        ),
        migrations.RemoveField(
            model_name='tanf_t4',
            name='stratum',
        ),
        migrations.RemoveField(
            model_name='tanf_t4',
            name='zip_code',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='amount_earned_income',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='amount_unearned_income',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='case_number',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='citizenship_status',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='countable_month_fed_time',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='countable_months_state_tribe',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='date_of_birth',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='education_level',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='employment_status',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='family_affiliation',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='fips_code',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='marital_status',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='needs_of_pregnant_woman',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='parent_minor_child',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='race_amer_indian',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='race_asian',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='race_black',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='race_hawaiian',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='race_hispanic',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='race_white',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='rec_aid_aged_blind',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='rec_aid_totally_disabled',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='rec_federal_disability',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='rec_oasdi_insurance',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='rec_ssi',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='record',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='relationship_hoh',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='rpt_month_year',
        ),
        migrations.RemoveField(
            model_name='tanf_t5',
            name='ssn',
        ),
        migrations.AddField(
            model_name='tanf_t4',
            name='CASE_NUMBER',
            field=models.CharField(max_length=11, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t4',
            name='CLOSURE_REASON',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t4',
            name='COUNTY_FIPS_CODE',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t4',
            name='DISPOSITION',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t4',
            name='REC_FOOD_STAMPS',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t4',
            name='REC_MED_ASSIST',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t4',
            name='REC_SUB_CC',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t4',
            name='REC_SUB_HOUSING',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t4',
            name='RPT_MONTH_YEAR',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t4',
            name='RecordType',
            field=models.CharField(max_length=156, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t4',
            name='STRATUM',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t4',
            name='ZIP_CODE',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='AMOUNT_EARNED_INCOME',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='AMOUNT_UNEARNED_INCOME',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='CASE_NUMBER',
            field=models.CharField(max_length=11, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='CITIZENSHIP_STATUS',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='COUNTABLE_MONTHS_STATE_TRIBE',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='COUNTABLE_MONTH_FED_TIME',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='DATE_OF_BIRTH',
            field=models.CharField(max_length=8, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='EDUCATION_LEVEL',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='EMPLOYMENT_STATUS',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='FAMILY_AFFILIATION',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='GENDER',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='MARITAL_STATUS',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='NEEDS_OF_PREGNANT_WOMAN',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='PARENT_MINOR_CHILD',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='RACE_AMER_INDIAN',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='RACE_ASIAN',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='RACE_BLACK',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='RACE_HAWAIIAN',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='RACE_HISPANIC',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='RACE_WHITE',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='REC_AID_AGED_BLIND',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='REC_AID_TOTALLY_DISABLED',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='REC_FEDERAL_DISABILITY',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='REC_OASDI_INSURANCE',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='REC_SSI',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='RELATIONSHIP_HOH',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='RPT_MONTH_YEAR',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='RecordType',
            field=models.CharField(max_length=156, null=True),
        ),
        migrations.AddField(
            model_name='tanf_t5',
            name='SSN',
            field=models.CharField(max_length=9, null=True),
        ),
    ]
