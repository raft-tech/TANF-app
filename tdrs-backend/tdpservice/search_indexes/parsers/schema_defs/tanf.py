"""Houses definitions for TANF datafile schemas."""

from ..util import RowSchema
from ..tanf_validator import *

def t1_schema():
    """Return a RowSchema for T1 records.

                    FAMILY CASE CHARACTERISTIC DATA

    DESCRIPTION         LENGTH  FROM    TO  COMMENTS
    RECORD TYPE         2       1       2   "T1" - SECTION 1
    REPORTING MONTH     6       3       8   Numeric
    CASE NUMBER         11      9       19  Alphanumeric
    COUNTY FIPS CODE    3       20      22  Numeric
    STRATUM             2       23      24  Numeric
    ZIP CODE            5       25      29  Alphanumeric
    FUNDING STREAM      1       30      30  Numeric
    DISPOSITION         1       31      31  Numeric
    NEW APPLICANT       1       32      32  Numeric
    FAMILY MEMBERS      2       33      34  Numeric
    TYPE OF FAMILY      1       35      35  Numeric
    SUBSIDIZED HOUSING  1       36      36  Numeric
    MEDICAL ASSISTANCE  1       37      37  Numeric
    FOOD STAMPS         1       38      38  Numeric
    FOOD STAMP AMOUNT   4       39      42  Numeric
    SUB CHILD CARE      1       43      43  Numeric
    AMT CHILD CARE      4       44      47  Numeric
    AMT CHIILD SUPPORT  4       48      51  Numeric
    FAMILY'S CASH       4       52      55  Numeric
    CASH
    AMOUNT              4       56      59  Numeric
    NBR_MONTH           3       60      62  Numeric
    TANF CHILD CARE
    AMOUNT              4       63      66  Numeric
    CHILDREN_COVERED    2       67      68  Numeric
    NBR_MONTHS          3       69      71  Numeric
    TRANSPORTATION
    AMOUNT              4       72      75  Numeric
    NBR_MONTHS          3       76      78  Numeric
    TRANSITIONAL SERVICES
    AMOUNT              4       79      82  Numeric
    NBR_MONTHS          3       83      85  Numeric
    OTHER
    AMOUNT              4       86      89  Numeric
    NBR_MONTHS          3       90      92  Numeric
    REASON FOR & AMOUNT OF ASSISTANCE
    REDUCTION
    SANCTIONS AMT       4       93      96  Numeric
    WORK REQ            1       97      97  Alphanumeric
    NO DIPLOMA          1       98      98  Alphanumeric
    NOT IN SCHOOL       1       99      99  Alphanumeric
    NOT CHILD SUPPORT   1       100     100 Alphanumeric
    IRP FAILURE         1       101     101 Alphanumeric
    OTHER SANCTION      1       102     102 Alphanumeric
    PRIOR OVERPAYMENT   4       103     106 Alphanumeric
    TOTAL REDUC AMOUNT  4       107     110 Alphanumeric
    FAMILY CAP          1       111     111 Alphanumeric
    LENGTH OF ASSIST    1       112     112 Alphanumeric
    OTHER, NON-SANCTION 1       113     113 Alphanumeric
    WAIVER_CONTROL_GRPS 1       114     114 Alphanumeric
    TANF FAMILY
    EXEMPT TIME_LIMITS  2       115     116 Numeric
    CHILD ONLY FAMILY   1       117     117 Numeric
    BLANK               39      118     156 Spaces
    """
    family_case_schema = RowSchema()
    family_case_schema.add_fields(
        [  # does it make sense to try to include regex (e.g., =r'^T1$')
            ('record_type', 2, 1, 2, "Alphanumeric", []),
            ('reporting_month', 6, 3, 8, "Numeric", [t1_006, t1_007]),
            ('case_number', 11, 9, 19, "Alphanumeric", []),
            ('county_fips_code', 3, 20, 22, "Numeric", []),
            ('stratum', 2, 23, 24, "Numeric", []),
            ('zip_code', 5, 25, 29, "Alphanumeric", []),
            ('funding_stream', 1, 30, 30, "Numeric", []),
            ('disposition', 1, 31, 31, "Numeric", []),
            ('new_applicant', 1, 32, 32, "Numeric", []),
            ('family_size', 2, 33, 34, "Numeric", []),
            ('family_type', 1, 35, 35, "Numeric", []),
            ('receives_sub_housing', 1, 36, 36, "Numeric", []),
            ('receives_medical_assistance', 1, 37, 37, "Numeric", []),
            ('receives_food_stamps', 1, 38, 38, "Numeric", []),
            ('food_stamp_amount', 4, 39, 42, "Numeric", []),
            ('receives_sub_child_care', 1, 43, 43, "Numeric", []),
            ('child_care_amount', 4, 44, 47, "Numeric", []),
            ('child_support_amount', 4, 48, 51, "Numeric", []),
            ('family_cash_recources', 4, 52, 55, "Numeric", []),
            ('family_cash_amount', 4, 56, 59, "Numeric", []),
            ('family_cash_nbr_month', 3, 60, 62, "Numeric", []),
            ('tanf_child_care_amount', 4, 63, 66, "Numeric", []),
            ('children_covered', 2, 67, 68, "Numeric", []),
            ('child_care_nbr_months', 3, 69, 71, "Numeric", []),
            ('transportation_amount', 4, 72, 75, "Numeric", []),
            ('transport_nbr_months', 3, 76, 78, "Numeric", []),
            ('transition_services_amount', 4, 79, 82, "Numeric", []),
            ('transition_nbr_months', 3, 83, 85, "Numeric", []),
            ('other_amount', 4, 86, 89, "Numeric", []),
            ('other_nbr_months', 3, 90, 92, "Numeric", []),
            ('reduction_amount', 4, 93, 96, "Numeric", []),
            ('reduc_work_requirements', 1, 97, 97, "Numeric", []),
            ('reduc_adult_no_hs_diploma', 1, 98, 98, "Numeric", []),
            ('reduc_teen_not_in_school', 1, 99, 99, "Numeric", []),
            ('reduc_noncooperation_child_support', 1, 100, 100, "Numeric", []),
            ('reduc_irp_failure', 1, 101, 101, "Numeric", []),
            ('reduc_other_sanction', 1, 102, 102, "Numeric", []),
            ('reduc_prior_overpayment', 4, 103, 106, "Numeric", []),
            ('total_reduc_amount', 4, 107, 110, "Numeric", []),
            ('reduc_family_cap', 1, 111, 111, "Numeric", []),
            ('reduc_length_of_assist', 1, 112, 112, "Numeric", []),
            ('other_non_sanction', 1, 113, 113, "Numeric", []),
            ('waiver_control_grps', 1, 114, 114, "Numeric", []),
            ('tanf_family_exempt_time_limits', 2, 115, 116, "Numeric", []),
            ('tanf_new_child_only_family', 1, 117, 117, "Numeric", []),
            ('blank', 39, 118, 156, "Spaces", [])
        ]
    )
    return family_case_schema
