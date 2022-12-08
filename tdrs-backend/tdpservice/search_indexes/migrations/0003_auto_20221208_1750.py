# Generated by Django 3.2.15 on 2022-12-08 17:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search_indexes', '0002_parserlog'),
    ]

    operations = [
        migrations.RenameField(
            model_name='t1',
            old_name='amt_sub_cc',
            new_name='child_care_amount',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='cc_nbr_of_months',
            new_name='child_care_nbr_months',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='cash_amount',
            new_name='family_cash_amount',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='nbr_months',
            new_name='family_cash_nbr_month',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='nbr_of_family_members',
            new_name='family_size',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='amt_food_stamp_assistance',
            new_name='food_stamp_amount',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='receives_sub_cc',
            new_name='receives_sub_child_care',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='record',
            new_name='record_type',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='family_sanct_adult',
            new_name='reduc_adult_no_hs_diploma',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='family_cap',
            new_name='reduc_family_cap',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='failure_to_comply',
            new_name='reduc_irp_failure',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='reductions_on_receipts',
            new_name='reduc_length_of_assist',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='non_cooperation_cse',
            new_name='reduc_noncooperation_child_support',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='other_sanction',
            new_name='reduc_other_sanction',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='recoupment_prior_ovrpmt',
            new_name='reduc_prior_overpayment',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='sanct_teen_parent',
            new_name='reduc_teen_not_in_school',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='work_req_sanction',
            new_name='reduc_work_requirements',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='sanc_reduction_amount',
            new_name='reduction_amount',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='rpt_month_year',
            new_name='reporting_month',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='cc_amount',
            new_name='tanf_child_care_amount',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='family_exempt_time_limits',
            new_name='tanf_family_exempt_time_limits',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='family_new_child',
            new_name='tanf_new_child_only_family',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='other_total_reductions',
            new_name='total_reduc_amount',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='transp_amount',
            new_name='transportation_amount',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='waiver_evalu_control_grps',
            new_name='waiver_control_grps',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='other_nbr_of_months',
            new_name='other_nbr_months',
        ),
        migrations.RenameField(
            model_name='t1',
            old_name='transp_nbr_months',
            new_name='transport_nbr_months',
        ),
        migrations.RemoveField(
            model_name='t1',
            name='blank',
        ),
        migrations.RemoveField(
            model_name='t1',
            name='fips_code',
        ),
        migrations.RemoveField(
            model_name='t3',
            name='blank',
        ),
        migrations.RemoveField(
            model_name='t4',
            name='blank',
        ),
    ]
