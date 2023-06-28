# Generated by Django 3.2.15 on 2023-05-25 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_indexes', '0008_auto_20230522_1850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tanf_t1',
            name='AMT_FOOD_STAMP_ASSISTANCE',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='AMT_SUB_CC',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='CASE_NUMBER',
            field=models.CharField(max_length=11, null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='CASH_AMOUNT',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='CC_AMOUNT',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='CC_NBR_MONTHS',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='CHILDREN_COVERED',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='CHILD_SUPPORT_AMT',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='COUNTY_FIPS_CODE',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='DISPOSITION',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='FAILURE_TO_COMPLY',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='FAMILY_CAP',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='FAMILY_CASH_RESOURCES',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='FAMILY_EXEMPT_TIME_LIMITS',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='FAMILY_NEW_CHILD',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='FAMILY_SANC_ADULT',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='FAMILY_TYPE',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='FIPS_CODE',
            field=models.CharField(max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='FUNDING_STREAM',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='NBR_FAMILY_MEMBERS',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='NBR_MONTHS',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='NEW_APPLICANT',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='NON_COOPERATION_CSE',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='OTHER_AMOUNT',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='OTHER_NBR_MONTHS',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='OTHER_NON_SANCTION',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='OTHER_SANCTION',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='OTHER_TOTAL_REDUCTIONS',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='RECEIVES_FOOD_STAMPS',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='RECEIVES_MED_ASSISTANCE',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='RECEIVES_SUB_CC',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='RECEIVES_SUB_HOUSING',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='RECOUPMENT_PRIOR_OVRPMT',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='REDUCTIONS_ON_RECEIPTS',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='RPT_MONTH_YEAR',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='RecordType',
            field=models.CharField(max_length=156, null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='SANC_REDUCTION_AMT',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='SANC_TEEN_PARENT',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='STRATUM',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='TRANSITION_NBR_MONTHS',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='TRANSITION_SERVICES_AMOUNT',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='TRANSP_AMOUNT',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='TRANSP_NBR_MONTHS',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='WAIVER_EVAL_CONTROL_GRPS',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='WORK_REQ_SANCTION',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='tanf_t1',
            name='ZIP_CODE',
            field=models.CharField(max_length=5, null=True),
        ),
    ]
