"""Models representing parsed TANF data file records submitted to TDP."""

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from tdpservice.parsers.models import ParserError


class TANF_T1(models.Model):
    """
    Parsed record representing a T1 data submission.

    Mapped to an elastic search index.
    """

    # def __is_valid__():
    # TODO: might need a correlating validator to check across fields

    error = GenericRelation(ParserError)
    RecordType = models.CharField(max_length=156, null=False, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=False, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=False, blank=False)
    FIPS_CODE = models.CharField(max_length=2, null=False, blank=False)
    COUNTY_FIPS_CODE = models.CharField(
        max_length=3,
        null=False,
        blank=False
    )
    STRATUM = models.IntegerField(null=False, blank=False)
    ZIP_CODE = models.CharField(max_length=5, null=False, blank=False)
    FUNDING_STREAM = models.IntegerField(null=False, blank=False)
    DISPOSITION = models.IntegerField(null=False, blank=False)
    NEW_APPLICANT = models.IntegerField(null=False, blank=False)
    NBR_FAMILY_MEMBERS = models.IntegerField(null=False, blank=False)
    FAMILY_TYPE = models.IntegerField(null=False, blank=False)
    RECEIVES_SUB_HOUSING = models.IntegerField(null=False, blank=False)
    RECEIVES_MED_ASSISTANCE = models.IntegerField(null=False, blank=False)
    RECEIVES_FOOD_STAMPS = models.IntegerField(null=False, blank=False)
    AMT_FOOD_STAMP_ASSISTANCE = models.IntegerField(null=False, blank=False)
    RECEIVES_SUB_CC = models.IntegerField(null=False, blank=False)
    AMT_SUB_CC = models.IntegerField(null=False, blank=False)
    CHILD_SUPPORT_AMT = models.IntegerField(null=False, blank=False)
    FAMILY_CASH_RESOURCES = models.IntegerField(null=False, blank=False)
    CASH_AMOUNT = models.IntegerField(null=False, blank=False)
    NBR_MONTHS = models.IntegerField(null=False, blank=False)
    CC_AMOUNT = models.IntegerField(null=False, blank=False)
    CHILDREN_COVERED = models.IntegerField(null=False, blank=False)
    CC_NBR_MONTHS = models.IntegerField(null=False, blank=False)
    TRANSP_AMOUNT = models.IntegerField(null=False, blank=False)
    TRANSP_NBR_MONTHS = models.IntegerField(null=False, blank=False)
    TRANSITION_SERVICES_AMOUNT = models.IntegerField(null=False, blank=False)
    TRANSITION_NBR_MONTHS = models.IntegerField(null=False, blank=False)
    OTHER_AMOUNT = models.IntegerField(null=False, blank=False)
    OTHER_NBR_MONTHS = models.IntegerField(null=False, blank=False)
    SANC_REDUCTION_AMT = models.IntegerField(null=False, blank=False)
    WORK_REQ_SANCTION = models.IntegerField(null=False, blank=False)
    FAMILY_SANC_ADULT = models.IntegerField(null=False, blank=False)
    SANC_TEEN_PARENT = models.IntegerField(null=False, blank=False)
    NON_COOPERATION_CSE = models.IntegerField(null=False, blank=False)
    FAILURE_TO_COMPLY = models.IntegerField(null=False, blank=False)
    OTHER_SANCTION = models.IntegerField(null=False, blank=False)
    RECOUPMENT_PRIOR_OVRPMT = models.IntegerField(null=False, blank=False)
    OTHER_TOTAL_REDUCTIONS = models.IntegerField(null=False, blank=False)
    FAMILY_CAP = models.IntegerField(null=False, blank=False)
    REDUCTIONS_ON_RECEIPTS = models.IntegerField(null=False, blank=False)
    OTHER_NON_SANCTION = models.IntegerField(null=False, blank=False)
    WAIVER_EVAL_CONTROL_GRPS = models.IntegerField(null=False, blank=False)
    FAMILY_EXEMPT_TIME_LIMITS = models.IntegerField(null=False, blank=False)
    FAMILY_NEW_CHILD = models.IntegerField(null=False, blank=False)


class TANF_T2(models.Model):
    """
    Parsed record representing a T2 data submission.

    Mapped to an elastic search index.
    """

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)

    FAMILY_AFFILIATION = models.IntegerField(null=True, blank=False)
    NONCUSTODIAL_PARENT = models.IntegerField(null=True, blank=False)
    DOB = models.IntegerField(null=True, blank=False)
    SSN = models.CharField(max_length=9, null=True, blank=False)
    RACE_HISPANIC_OR_LATINO = models.CharField(max_length=1, null=True, blank=False)
    RACE_AMERICAN_INDIAN_OR_ALASKA_NATIVE = models.CharField(max_length=1, null=True, blank=False)
    RACE_ASIAN = models.CharField(max_length=1, null=True, blank=False)
    RACE_BLACK_OR_AFRICAN_AMERICAN = models.CharField(max_length=1, null=True, blank=False)
    RACE_NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER = models.CharField(max_length=1, null=True, blank=False)
    RACE_WHITE = models.CharField(max_length=1, null=True, blank=False)
    GENDER = models.IntegerField(null=True, blank=False)
    RECEIVES_FEDERAL_DISABILITY_INSURANCE_OASDI_PROGRAM = models.CharField(max_length=1, null=True, blank=False)
    RECEIVES_BENEFITS_BASED_ON_FEDERAL_DISABILITY_STATUS = models.CharField(max_length=1, null=True, blank=False)
    RECEIVES_AID_TOTALLY_DISABLED_UNDER_TITLE_XIV_APDT = models.CharField(max_length=1, null=True, blank=False)
    RECEIVES_AID_TO_THE_AGED = models.CharField(max_length=1, null=True, blank=False)
    RECEIVES_SUPPLEMENTAL_SECURITY_INCOME_TITLE_XVI_SSI = models.CharField(max_length=1, null=True, blank=False)
    MARITAL_STATUS = models.CharField(max_length=1, null=True, blank=False)
    RELATIONSHIP_TO_HEAD_OF_HOUSEHOLD = models.IntegerField(null=True, blank=False)
    PARENT_WITH_MINOR_CHILD = models.CharField(max_length=1, null=True, blank=False)
    NEEDS_OF_A_PREGNANT_WOMAN = models.CharField(max_length=1, null=True, blank=False)
    EDUCATION_LEVEL = models.CharField(max_length=2, null=True, blank=False)
    CITIZENSHIP_STATUS = models.CharField(max_length=1, null=True, blank=False)
    COOPERATION_WITH_CHILD_SUPPORT = models.CharField(max_length=1, null=True, blank=False)
    NUMBER_OF_COUNTABLE_MONTHS = models.CharField(max_length=3, null=True, blank=False)
    NUMBER_OF_COUNTABLE_MONTHS_REMAINING = models.CharField(max_length=2, null=True, blank=False)
    CURRENT_MONTH_EXEMPT_FROM_STATE = models.CharField(max_length=1, null=True, blank=False)
    EMPLOYMENT_STATUS = models.CharField(max_length=1, null=True, blank=False)
    WORK_ELIGIBLE_INDIVIDUAL_INDICATOR = models.CharField(max_length=2, null=True, blank=False)
    WORK_PARTICIPATION_STATUS = models.CharField(max_length=2, null=True, blank=False)
    UNSUBSIDIZED_EMPLOYMENT = models.CharField(max_length=2, null=True, blank=False)
    SUBSIDIZED_PRIVATE_EMPLOYMENT = models.CharField(max_length=2, null=True, blank=False)
    SUBSIDIZED_PUBLIC_EMPLOYMENT = models.CharField(max_length=2, null=True, blank=False)
    WORK_EXP_HOURS_OF_PARTICIPATION = models.CharField(max_length=2, null=True, blank=False)
    WORK_EXP_EXCUSED_ABSENCES = models.CharField(max_length=2, null=True, blank=False)
    WORK_EXP_HOLIDAYS = models.CharField(max_length=2, null=True, blank=False)
    ON_THE_JOB_TRAINING = models.CharField(max_length=2, null=True, blank=False)
    JOB_SEARCH_HOURS_OF_PARTICIPATION = models.CharField(max_length=2, null=True, blank=False)
    JOB_SEARCH_EXCUSED_ABSENCES = models.CharField(max_length=2, null=True, blank=False)
    JOB_SEARCH_HOLIDAYS = models.CharField(max_length=2, null=True, blank=False)
    COMMUNITY_SVS_HOURS_OF_PARTICIPATION = models.CharField(max_length=2, null=True, blank=False)
    COMMUNITY_SVS_EXCUSED_ABSENCES = models.CharField(max_length=2, null=True, blank=False)
    COMMUNITY_SVS_HOLIDAYS = models.CharField(max_length=2, null=True, blank=False)
    VOCATIONAL_ED_HOURS_OF_PARTICIPATION = models.CharField(max_length=2, null=True, blank=False)
    VOCATIONAL_ED_EXCUSED_ABSENCES = models.CharField(max_length=2, null=True, blank=False)
    VOCATIONAL_ED_HOLIDAYS = models.CharField(max_length=2, null=True, blank=False)
    JOB_SKILLS_HOURS_OF_PARTICIPATION = models.CharField(max_length=2, null=True, blank=False)
    JOB_SKILLS_EXCUSED_ABSENCES = models.CharField(max_length=2, null=True, blank=False)
    JOB_SKILLS_HOLIDAYS = models.CharField(max_length=2, null=True, blank=False)
    EDUCATION_RELATED_HOURS_OF_PARTICIPATION = models.CharField(max_length=2, null=True, blank=False)
    EDUCATION_RELATED_EXCUSED_ABSENCES = models.CharField(max_length=2, null=True, blank=False)
    EDUCATION_RELATED_HOLIDAYS = models.CharField(max_length=2, null=True, blank=False)
    SCHOOL_ATTENDENCE_HOURS_OF_PARTICIPATION = models.CharField(max_length=2, null=True, blank=False)
    SCHOOL_ATTENDENCE_EXCUSED_ABSENCES = models.CharField(max_length=2, null=True, blank=False)
    SCHOOL_ATTENDENCE_HOLIDAYS = models.CharField(max_length=2, null=True, blank=False)
    CHILD_CARE_HOURS_OF_PARTICIPATION = models.CharField(max_length=2, null=True, blank=False)
    CHILD_CARE_EXCUSED_ABSENCES = models.CharField(max_length=2, null=True, blank=False)
    CHILD_CARE_HOLIDAYS = models.CharField(max_length=2, null=True, blank=False)
    OTHER_WORK_ACTIVITIES = models.CharField(max_length=2, null=True, blank=False)
    NUMBER_OF_DEEMED_CORE_HOURS_FOR_OVERALL_RATE = models.CharField(max_length=2, null=True, blank=False)
    NUMBER_OF_DEEMED_CORE_HOURS_FOR_TWO_PARENT_RATE = models.CharField(max_length=2, null=True, blank=False)
    AMOUNT_OF_EARNED_INCOME = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_INCOME_EARNED_INCOME_TAX_CREDIT = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_INCOME_SOCIAL_SECURITY = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_INCOME_SSI = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_INCOME_WORKERS_COMPENSATION = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_INCOME_OTHER_UNEARNED_INCOME = models.CharField(max_length=4, null=True, blank=False)


class TANF_T3(models.Model):
    """
    Parsed record representing a T3 data submission.

    Mapped to an elastic search index.
    """

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)
    FAMILY_AFFILIATION = models.IntegerField(null=True, blank=False)

    DOB = models.IntegerField(null=True, blank=False)
    SSN = models.CharField(max_length=9, null=True, blank=False)
    RACE_HISPANIC_OR_LATINO = models.CharField(max_length=1,  null=True, blank=False)
    RACE_AMERICAN_INDIAN_OR_ALASKA_NATIVE = models.CharField(max_length=1, null=True, blank=False)
    RACE_ASIAN = models.CharField(max_length=1, null=True, blank=False)
    RACE_BLACK_OR_AFRICAN_AMERICAN = models.CharField(max_length=1, null=True, blank=False)
    RACE_NATIVE_HAWAIIAN_OR_OTHER_PACIFIC_ISLANDER = models.CharField(max_length=1, null=True, blank=False)
    RACE_WHITE = models.CharField(max_length=1, null=True, blank=False)
    GENDER = models.IntegerField(null=True, blank=False)
    RECEIVES_BENEFITS_UNDER_NON_SSA_PROGRAMS = models.CharField(max_length=1, null=True, blank=False)
    RECEIVES_SSI_UNDER_TITLE_XVI_SSI = models.CharField(max_length=1, null=True, blank=False)
    RELATIONSHIP_TO_HEAD_OF_HOUSEHOLD = models.IntegerField(null=True, blank=False)
    PARENT_WITH_MINOR_CHILD = models.CharField(max_length=1, null=True, blank=False)
    EDUCATION_LEVEL = models.CharField(max_length=2, null=True, blank=False)
    CITIZENSHIP_ALIENAGE = models.CharField(max_length=1, null=True, blank=False)
    UNEARNED_INCOME_SSI = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_INCOME_OTHER_UNEARNED_INCOME = models.CharField(max_length=4, null=True, blank=False)


class TANF_T4(models.Model):
    """
    Parsed record representing a T4 data submission.

    Mapped to an elastic search index.
    """

    record = models.CharField(max_length=156, null=False, blank=False)
    rpt_month_year = models.IntegerField(null=False, blank=False)
    case_number = models.CharField(max_length=11, null=False, blank=False)
    disposition = models.IntegerField(null=False, blank=False)
    fips_code = models.CharField(max_length=100, null=False, blank=False)

    county_fips_code = models.CharField(
        max_length=3,
        null=False,
        blank=False
    )
    stratum = models.IntegerField(null=False, blank=False)
    zip_code = models.CharField(max_length=5, null=False, blank=False)
    closure_reason = models.IntegerField(null=False, blank=False)
    rec_sub_housing = models.IntegerField(null=False, blank=False)
    rec_med_assist = models.IntegerField(null=False, blank=False)
    rec_food_stamps = models.IntegerField(null=False, blank=False)
    rec_sub_cc = models.IntegerField(null=False, blank=False)


class TANF_T5(models.Model):
    """
    Parsed record representing a T5 data submission.

    Mapped to an elastic search index.
    """

    record = models.CharField(max_length=156, null=False, blank=False)
    rpt_month_year = models.IntegerField(null=False, blank=False)
    case_number = models.CharField(max_length=11, null=False, blank=False)
    fips_code = models.CharField(max_length=100, null=False, blank=False)

    family_affiliation = models.IntegerField(null=False, blank=False)
    date_of_birth = models.CharField(max_length=8, null=False, blank=False)
    ssn = models.CharField(max_length=9, null=False, blank=False)
    race_hispanic = models.IntegerField(null=False, blank=False)
    race_amer_indian = models.IntegerField(null=False, blank=False)
    race_asian = models.IntegerField(null=False, blank=False)
    race_black = models.IntegerField(null=False, blank=False)
    race_hawaiian = models.IntegerField(null=False, blank=False)
    race_white = models.IntegerField(null=False, blank=False)
    gender = models.IntegerField(null=False, blank=False)
    rec_oasdi_insurance = models.FloatField(null=False, blank=False)
    rec_federal_disability = models.IntegerField(null=False, blank=False)
    rec_aid_totally_disabled = models.FloatField(null=False, blank=False)
    rec_aid_aged_blind = models.FloatField(null=False, blank=False)
    rec_ssi = models.IntegerField(null=False, blank=False)
    marital_status = models.FloatField(null=False, blank=False)
    relationship_hoh = models.IntegerField(null=False, blank=False)
    parent_minor_child = models.IntegerField(null=False, blank=False)
    needs_of_pregnant_woman = models.IntegerField(null=False, blank=False)
    education_level = models.IntegerField(null=False, blank=False)
    citizenship_status = models.IntegerField(null=False, blank=False)
    countable_month_fed_time = models.FloatField(null=False, blank=False)
    countable_months_state_tribe = models.FloatField(null=False, blank=False)
    employment_status = models.FloatField(null=False, blank=False)
    amount_earned_income = models.IntegerField(null=False, blank=False)
    amount_unearned_income = models.IntegerField(null=False, blank=False)


class TANF_T6(models.Model):
    """
    Parsed record representing a T6 data submission.

    Mapped to an elastic search index.
    """

    record = models.CharField(max_length=156, null=False, blank=False)
    rpt_month_year = models.IntegerField(null=False, blank=False)
    fips_code = models.CharField(max_length=100, null=False, blank=False)

    calendar_quarter = models.IntegerField(null=False, blank=False)
    applications = models.IntegerField(null=False, blank=False)
    approved = models.IntegerField(null=False, blank=False)
    denied = models.IntegerField(null=False, blank=False)
    assistance = models.IntegerField(null=False, blank=False)
    families = models.IntegerField(null=False, blank=False)
    num_2_parents = models.IntegerField(null=False, blank=False)
    num_1_parents = models.IntegerField(null=False, blank=False)
    num_no_parents = models.IntegerField(null=False, blank=False)
    recipients = models.IntegerField(null=False, blank=False)
    adult_recipients = models.IntegerField(null=False, blank=False)
    child_recipients = models.IntegerField(null=False, blank=False)
    noncustodials = models.IntegerField(null=False, blank=False)
    births = models.IntegerField(null=False, blank=False)
    outwedlock_births = models.IntegerField(null=False, blank=False)
    closed_cases = models.IntegerField(null=False, blank=False)


class TANF_T7(models.Model):
    """
    Parsed record representing a T7 data submission.

    Mapped to an elastic search index.
    """

    record = models.CharField(max_length=156, null=False, blank=False)
    rpt_month_year = models.IntegerField(null=False, blank=False)
    fips_code = models.CharField(max_length=100, null=False, blank=False)

    calendar_quarter = models.IntegerField(null=False, blank=False)
    tdrs_section_ind = models.CharField(
        max_length=1,
        null=False,
        blank=False
    )
    stratum = models.CharField(max_length=2, null=False, blank=False)
    families = models.IntegerField(null=False, blank=False)
