from django.db import models

class ParsedDataRecord(models.model):
    record = models.CharField(max_length=156, null=False, blank=False)
    rpt_month_year = models.IntegerField(null=False, blank=False) # convert to date time?
    case_number = models.CharField(max_length=100, null=False, blank=False)
    disposition = models.IntegerField(null=False, blank=False)
    fips_code = models.CharField(max_length=100, null=False, blank=False)

    @property
    def record_length(self):
        return len(self.record)

# Create your models here.
class T1(ParsedDataRecord):
    county_fips_code = models.CharField(max_length=100, null=False, blank=False)
    stratum = models.IntegerField(null=False, blank=False)
    zip_code = models.CharField(max_length=100, null=False, blank=False)
    funding_stream = models.IntegerField(null=False, blank=False)
    new_applicant = models.IntegerField(null=False, blank=False)
    nbr_of_family_members = models.IntegerField(null=False, blank=False)
    family_type = models.IntegerField(null=False, blank=False)
    receives_sub_housing = models.IntegerField(null=False, blank=False)
    receives_medical_assistance = models.IntegerField(null=False, blank=False)
    receives_food_stamps = models.IntegerField(null=False, blank=False)
    amt_food_stamp_assistance = models.IntegerField(null=False, blank=False)
    receives_sub_cc = models.IntegerField(null=False, blank=False)
    amt_sub_cc = models.IntegerField(null=False, blank=False)
    cc_amount = models.IntegerField(null=False, blank=False)
    family_cash_recources = models.IntegerField(null=False, blank=False)
    cash_amount = models.IntegerField(null=False, blank=False)
    nbr_months = models.IntegerField(null=False, blank=False)
    cc_amount = models.IntegerField(null=False, blank=False)
    children_covered = models.IntegerField(null=False, blank=False)
    cc_nbr_of_months = models.IntegerField(null=False, blank=False)
    transp_amount = models.IntegerField(null=False, blank=False)
    transp_nbr_months = models.IntegerField(null=False, blank=False)
    transition_services_amount = models.IntegerField(null=False, blank=False)
    transition_nbr_months = models.IntegerField(null=False, blank=False)
    other_amount = models.IntegerField(null=False, blank=False)
    other_nbr_of_months = models.IntegerField(null=False, blank=False)
    sanc_reduction_amount = models.IntegerField(null=False, blank=False)
    work_req_sanction = models.IntegerField(null=False, blank=False)
    family_sanct_adult = models.IntegerField(null=False, blank=False)
    sanct_teen_parent = models.IntegerField(null=False, blank=False)
    non_cooperation_cse = models.IntegerField(null=False, blank=False)
    failure_to_comply = models.IntegerField(null=False, blank=False)
    other_sanction = models.IntegerField(null=False, blank=False)
    recoupment_prior_ovrpmt = models.IntegerField(null=False, blank=False)
    other_total_reductions = models.IntegerField(null=False, blank=False)
    family_cap = models.IntegerField(null=False, blank=False)
    reductions_on_receipts = models.IntegerField(null=False, blank=False)
    other_non_sanction = models.IntegerField(null=False, blank=False)
    waiver_evalu_control_grps = models.IntegerField(null=False, blank=False)
    family_exempt_time_limits = models.IntegerField(null=False, blank=False)
    family_new_child = models.IntegerField(null=False, blank=False)
    blank = models.CharField(max_length=100, null=False, blank=False)

class T2(ParsedDataRecord):
    pass

class T3(ParsedDataRecord):
    pass

class T4(ParsedDataRecord):
    pass

class T5(ParsedDataRecord):
    pass

class T6(ParsedDataRecord):
    pass

class T7(ParsedDataRecord):
    pass
