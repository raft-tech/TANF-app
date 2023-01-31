"""Houses definitions for TANF datafile schemas."""

from ..util import RowSchema
from ..tanf_validator import *


def header_schema():
    """Return a RowSchema for header records."""
    header_schema = RowSchema()
    header_schema.add_fields()


def t1_schema():
    """Return a RowSchema for T1 records."""
    family_case_schema = RowSchema()
    family_case_schema.add_fields(
        [  # does it make sense to try to include regex (e.g., =r'^T1$')
            (None, 'record_type', 2, 1, 2, 'Alphanumeric', []),
            ('4', 'reporting_month', 6, 3, 8, 'Numeric', [t1_006, t1_007]),
            ('6', 'case_number', 11, 9, 19, 'Alphanumeric', [t1_004]),
            ('2', 'county_fips_code', 3, 20, 22, 'Numeric', []),
            ('5', 'stratum', 2, 23, 24, 'Numeric', [t1_003]),
            ('7', 'zip_code', 5, 25, 29, 'Alphanumeric', []),
            ('8', 'funding_stream', 1, 30, 30, 'Numeric', []),
            ('9', 'disposition', 1, 31, 31, 'Numeric', [t1_008]),
            ('10', 'new_applicant', 1, 32, 32, 'Numeric', []),
            ('11', 'family_size', 2, 33, 34, 'Numeric', [t1_010]),
            ('12', 'family_type', 1, 35, 35, 'Numeric', [t1_011]),
            ('13', 'receives_sub_housing', 1, 36, 36, 'Numeric', []),
            ('14', 'receives_medical_assistance', 1, 37, 37, 'Numeric', []),
            ('15', 'receives_food_stamps', 1, 38, 38, 'Numeric', []),
            ('16', 'food_stamp_amount', 4, 39, 42, 'Numeric', []),
            ('17', 'receives_sub_child_care', 1, 43, 43, 'Numeric', [t1_013]),
            ('18', 'child_care_amount', 4, 44, 47, 'Numeric', []),
            ('19', 'child_support_amount', 4, 48, 51, 'Numeric', []),
            ('20', 'family_cash_recources', 4, 52, 55, 'Numeric', []),
            ('21A', 'family_cash_amount', 4, 56, 59, 'Numeric', []),
            ('21B', 'family_cash_nbr_month', 3, 60, 62, 'Numeric', []),
            ('22A', 'tanf_child_care_amount', 4, 63, 66, 'Numeric', []),
            ('22B', 'children_covered', 2, 67, 68, 'Numeric', []),
            ('22C', 'child_care_nbr_months', 3, 69, 71, 'Numeric', []),
            ('23A', 'transportation_amount', 4, 72, 75, 'Numeric', []),
            ('23B', 'transport_nbr_months', 3, 76, 78, 'Numeric', []),
            ('24A', 'transition_services_amount', 4, 79, 82, 'Numeric', []),
            ('24B', 'transition_nbr_months', 3, 83, 85, 'Numeric', []),
            ('25A', 'other_amount', 4, 86, 89, 'Numeric', []),
            ('25B', 'other_nbr_months', 3, 90, 92, 'Numeric', []),
            ('26Ai', 'reduction_amount', 4, 93, 96, 'Numeric', []),
            ('26Aii', 'reduc_work_requirements', 1, 97, 97, 'Numeric', []),
            ('26Aiii', 'reduc_adult_no_hs_diploma', 1, 98, 98, 'Numeric', []),
            ('26Aiv', 'reduc_teen_not_in_school', 1, 99, 99, 'Numeric', []),
            ('26Av', 'reduc_noncooperation_child_support', 1, 100, 100, 'Numeric', []),
            ('26Avi', 'reduc_irp_failure', 1, 101, 101, 'Numeric', []),
            ('26Avii', 'reduc_other_sanction', 1, 102, 102, 'Numeric', []),
            ('26B', 'reduc_prior_overpayment', 4, 103, 106, 'Numeric', []),
            ('26Ci', 'total_reduc_amount', 4, 107, 110, 'Numeric', []),
            ('26Cii', 'reduc_family_cap', 1, 111, 111, 'Numeric', []),
            ('26Ciii', 'reduc_length_of_assist', 1, 112, 112, 'Numeric', []),
            ('26Civ', 'other_non_sanction', 1, 113, 113, 'Numeric', []),
            ('27', 'waiver_control_grps', 1, 114, 114, 'Numeric', []),
            ('28', 'tanf_family_exempt_time_limits', 2, 115, 116, 'Numeric', []),
            ('29', 'tanf_new_child_only_family', 1, 117, 117, 'Numeric', []),
            ('blank', 39, 118, 156, 'Spaces', [])
        ]
    )

    '''
    TOWARD FEDERAL TIME-LIMIT 3 60 62 Alphanumeric
    45 NUMBER OF COUNTABLE MONTHS REMAINING
    UNDER STATE/TRIBE TIME-LIMIT 2 63 64 Alphanumeric
    46 CURRENT MONTH EXEMPT FROM STATE
    TRIBE TIME-LIMIT 1 65 65 Alphanumeric
    47 EMPLOYMENT STATUS 1 66 66 Alphanumeric
    48 WORK ELIGIBLE INDIVIDUAL INDICATOR 2 67 68 Alphanumeric
    49 WORK PARTICIPATION STATUS 2 69 70 Alphanumeric
    50 UNSUBSIDIZED EMPLOYMENT 2 71 72 Alphanumeric
    51 SUBSIDIZED PRIVATE EMPLOYMENT 2 73 74 Alphanumeric
    52 SUBSIDIZED PUBLIC EMPLOYMENT 2 75 76 Alphanumeric
    53 WORK EXPERIENCE
    ITEM53A_HOURS OF PARTICIPATION 2 77 78 Alphanumeric
    ITEM53B_EXCUSED ABSENCES 2 79 80 Alphanumeric
    ITEM53C_HOLIDAYS 2 81 82 Alphanumeric
    54 ON THE JOB TRAINING 2 83 84 Alphanumeric
    55 JOB SEARCH & JOB READINESS
    ITEM55A_HOURS OF PARTICIPATION 2 85 86 Alphanumeric
    ITEM55B_EXCUSED ABSENCES 2 87 88 Alphanumeric
    ITEM55C_HOLIDAYS 2 89 90 Alphanumeric
    56 COMMUNITY SVS PROG.
    ITEM56A_HOURS OF PARTICIPATION 2 91 92 Alphanumeric
    ITEM56B_EXCUSED ABSENCES 2 93 94 Alphanumeric
    ITEM56C_HOLIDAYS 2 95 96 Alphanumeric
    57 VOCATIONAL EDUCATION TRAINING
    ITEM57A_HOURS OF PARTICIPATION 2 97 98 Alphanumeric
    ITEM57B_EXCUSED ABSENCES 2 99 100 Alphanumeric
    ITEM57C_HOLIDAYS 2 101 102 Alphanumeric
    58 JOB SKILLS TRAINING EMPLOYMENT RELATED
    EMPLOYMENT
    ITEM58A_HOURS OF PARTICIPATION 2 103 104 Alphanumeric
    ITEM58B_EXCUSED ABSENCES 2 105 106 Alphanumeric
    ITEM58C_HOLIDAYS 2 107 108 Alphanumeric
    59 EDUCATION RELATED TO EMPLOYMENT WITH
    NO HIGH SCHOOL DIPLOMA
    ITEM59A_HOURS OF PARTICIPATION 2 109 110 Alphanumeric
    ITEM59B_EXCUSED ABSENCES 2 111 112 Alphanumeric
    ITEM59C_HOLIDAYS 2 113 114 Alphanumeric
    60 SATISFACTORY SCHOOL ATTENDENCE
    ITEM60A_HOURS OF PARTICIPATION 2 115 116 Alphanumeric
    ITEM60B_EXCUSED ABSENCES 2 117 118 Alphanumeric
    ITEM60C_HOLIDAYS 2 119 120 Alphanumeric
    61 PROVIDING CHILD CARE
    ITEM61A_HOURS OF PARTICIPATION 2 121 122 Alphanumeric
    ITEM61B_EXCUSED ABSENCES 2 123 124 Alphanumeric
    ITEM61C_HOLIDAYS 2 125 126 Alphanumeric
    62 OTHER WORK ACTIVITIES 2 127 128 Alphanumeric
    63 NUMBER OF DEEMED CORE HOURS FOR 2 129 130 Alphanumeric
    OVERALL RATE
    64 NUMBER OF DEEMED CORE HOURS FOR 2 131 132 Alphanumeric
    THE TWO-PARENT RATE
    65 AMOUNT OF EARNED INCOME 4 133 136 Alphanumeric
    66 AMOUNT OF UNEARNED INCOME
    ITEM66A_EARNED INCOME TAX CREDIT 4 137 140 Alphanumeric
    ITEM66B_SOCIAL SECURITY 4 141 144 Alphanumeric
    ITEM66C_SSI 4 145 148 Alphanumeric
    ITEM66D_WORKER'S COMPENSATION 4 149 152 Alphanumeric
    ITEM66E_OTHER UNEARNED INCOME 4 153 156 Alphanumeric

    '''


    adult_case_schema = RowSchema()
    # use the comment above to generate the schema
    adult_case_schema.add_fields(
        [
            (None, 'record_type', 2, 1, 2, 'Alphanumeric', []),
            ('4', 'reporting_month', 6, 3, 8, 'Numeric', []),
            ('6', 'case_number', 11, 9, 19, 'Alphanumeric', []),
            ('30', 'family_affiliation', 1, 20, 20, 'Alphanumeric', []),
            ('31', 'noncustodial_parent', 1, 21, 21, 'Alphanumeric', []),
            ('32', 'date_of_birth', 8, 22, 29, 'Numeric', []),
            ('33', 'social_security_number', 9, 30, 38, 'Alphanumeric', []),
            ('34A', 'hispanic_or_latino', 1, 39, 39, 'Alphanumeric', []),
            ('34B', 'american_indian_or_alaska_native', 1, 40, 40, 'Alphanumeric', []),
            ('34C', 'asian', 1, 41, 41, 'Alphanumeric', []),
            ('34D', 'black_or_african_american', 1, 42, 42, 'Alphanumeric', []),
            ('34E', 'native_hawaiian_or_other_pacific_islander', 1, 43, 43, 'Alphanumeric', []),
            ('34F', 'white', 1, 44, 44, 'Alphanumeric', []),
            ('35', 'gender', 1, 45, 45, 'Alphanumeric', []),
            ('36A', 'recieves_oasdi', 1, 46, 46, 'Alphanumeric', []),
            ('36B', 'recieves_non_ssc_act', 1, 47, 47, 'Alphanumeric', []),
            ('36C', 'recieves_title_xiv_apdt', 1, 48, 48, 'Alphanumeric', []),
            ('36D', 'recieves_title_xvi_aabd', 1, 49, 49, 'Alphanumeric', []),
            ('36E', 'recieves_title_xvi_ssi', 1, 50, 50, 'Alphanumeric', []),
            ('37', 'marital_status', 1, 51, 51, 'Alphanumeric', []),
            ('38', 'relationship_to_head_of_house', 2, 52, 53, 'Numeric', []),
            ('39', 'parent_with_minor_child', 1, 54, 54, 'Alphanumeric', []),
            ('40', 'needs_of_pregnant_woman', 1, 55, 55, 'Alphanumeric', []),
            ('41', 'education_level', 2, 56, 57, 'Alphanumeric', []),
            ('42' 'citizenship_status', 1, 58, 58, 'Alphanumeric', []),
            ('43', 'cooperation_with_child_support', 1, 59, 59, 'Alphanumeric', []),
            ('44', 'cooperation_with_child_support', 1, 60, 62, 'Alphanumeric', []),
            ('45', 'remaining_state_or_tribe_months', 2, 63, 64, 'Alphanumeric', []),
            ('46', 'current_month_exempt_from_time_limit')
        ]
    )


    return family_case_schema
