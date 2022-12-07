from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
"""Wrapper around Django's RegexValidator."""

# TODO: dynamic regex for numbers with input length
# wrapper for boolean validator
# wrapper for date validator


def record_validator(row):
    rv = RegexValidator(regex="^T[0-9]$", message="Record type format incorrect.", code="invalid")
    rv(row)
    
def rpt_month_year(row):
    rv = RegexValidator(regex="^[0-9]{6}$", message="Report month/year format incorrect.", code="invalid")
    rv(row)

def case_number(row):
    rv = RegexValidator(regex="^[0-9]{11}$", message="Case number format incorrect.", code="invalid")
    rv(row)

def disposition(row):
    rv = RegexValidator(regex="^[A-Z]{2}$", message="Disposition format incorrect.", code="invalid")
    rv(row)

def county_fips_code(row):
    rv = RegexValidator(regex="^[0-9]{3}$", message="County FIPS code format incorrect.", code="invalid")
    rv(row)
    
def stratum(row):
    rv = RegexValidator(regex="^[0-9]{2}$", message="Stratum format incorrect.", code="invalid")
    rv(row)

'''
zip_code 
funding_stream 
new_applicant 
nbr_of_family_members 
family_type 
receives_sub_housing 
receives_medical_assistance 
receives_food_stamps 
amt_food_stamp_assistance 
receives_sub_cc 
amt_sub_cc 
child_support_amount 
family_cash_recources 
cash_amount 
nbr_months 
cc_amount 
children_covered 
cc_nbr_of_months 
transp_amount 
transp_nbr_months 
transition_services_amount 
transition_nbr_months 
other_amount 
other_nbr_of_months 
sanc_reduction_amount 
work_req_sanction 
family_sanct_adult 
sanct_teen_parent 
non_cooperation_cse 
failure_to_comply 
other_sanction 
recoupment_prior_ovrpmt 
other_total_reductions 
family_cap 
reductions_on_receipts 
other_non_sanction 
waiver_evalu_control_grps 
family_exempt_time_limits 
family_new_child 
blank 
'''