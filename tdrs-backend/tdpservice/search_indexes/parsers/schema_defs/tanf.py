"""Houses definitions for TANF datafile schemas."""

from ..util import RowSchema
from tdpservice.search_indexes.parsers.tanf_validators import (
    t1_003,
    t1_006,
    t1_007,
    t1_008,
    t1_010,
    t1_011,
    t1_013,
    t1_097,
    t1_099,
    t1_100,
    t1_101,
    t1_102,
    t1_103,
    t1_104,
    t1_105,
    t1_121,
    t1_122,
    t1_123
)

def t1_schema():
    """Return a RowSchema for T1 records."""

    family_case_schema = RowSchema()
    family_case_schema.add_fields(
        [  # does it make sense to try to include regex (e.g., =r'^T1$')
            (None, 'RecordType', 2, 1, 2, "Alphanumeric", []),
            ('4', 'RPT_MONTH_YEAR', 6, 3, 8, "Numeric", [t1_006, t1_007]),
            ('6', 'CASE_NUMBER', 11, 9, 19, "Alphanumeric", []),
            ('2', 'COUNTY_FIPS_CODE', 3, 20, 22, "Numeric", []),
            ('5', 'STRATUM', 2, 23, 24, "Numeric", [t1_003]),
            ('7', 'ZIP_CODE', 5, 25, 29, "Alphanumeric", []),
            ('8', 'FUNDING_STREAM', 1, 30, 30, "Numeric", [t1_097]),
            ('9', 'DISPOSITION', 1, 31, 31, "Numeric", [t1_008]),
            ('10', 'NEW_APPLICANT', 1, 32, 32, "Numeric", []),
            ('11', 'NBR_FAMILY_MEMBERS', 2, 33, 34, "Numeric", [t1_010]),
            ('12', 'FAMILY_TYPE', 1, 35, 35, "Numeric", [t1_011]),
            ('13', 'RECEIVES_SUB_HOUSING', 1, 36, 36, "Numeric", [t1_099]),
            ('14', 'RECEIVES_MED_ASSISTANCE', 1, 37, 37, "Numeric", [t1_100]),
            ('15', 'RECEIVES_FOOD_STAMPS', 1, 38, 38, "Numeric", [t1_101]),
            ('16', 'AMT_FOOD_STAMP_ASSISTANCE', 4, 39, 42, "Numeric", [t1_102]),
            ('17', 'RECEIVES_SUB_CC', 1, 43, 43, "Numeric", [t1_013]),
            ('18', 'AMT_SUB_CC', 4, 44, 47, "Numeric", [t1_103]),
            ('19', 'CHILD_SUPPORT_AMT', 4, 48, 51, "Numeric", [t1_104]),
            ('20', 'FAMILY_CASH_RESOURCES', 4, 52, 55, "Numeric", [t1_105]),
            ('21A', 'CASH_AMOUNT', 4, 56, 59, "Numeric", []),
            ('21B', 'NBR_MONTHS', 3, 60, 62, "Numeric", []),
            ('22A', 'CC_AMOUNT', 4, 63, 66, "Numeric", []),
            ('22B', 'CHILDREN_COVERED', 2, 67, 68, "Numeric", []),
            ('22C', 'CC_NBR_MONTHS', 3, 69, 71, "Numeric", []),
            ('23A', 'TRANSP_AMOUNT', 4, 72, 75, "Numeric", []),
            ('23B', 'TRANSP_NBR_MONTHS', 3, 76, 78, "Numeric", []),
            ('24A', 'TRANSITION_SERVICES_AMOUNT', 4, 79, 82, "Numeric", []),
            ('24B', 'TRANSITION_NBR_MONTHS', 3, 83, 85, "Numeric", []),
            ('25A', 'OTHER_AMOUNT', 4, 86, 89, "Numeric", []),
            ('25B', 'OTHER_NBR_MONTHS', 3, 90, 92, "Numeric", []),
            ('26Ai', 'SANC_REDUCTION_AMT', 4, 93, 96, "Numeric", []),
            ('26Aii', 'WORK_REQ_SANCTION', 1, 97, 97, "Numeric", []),
            ('26Aiii', 'FAMILY_SANC_ADULT', 1, 98, 98, "Numeric", []),
            ('26Aiv', 'SANC_TEEN_PARENT', 1, 99, 99, "Numeric", []),
            ('26Av', 'NON_COOPERATION_CSE', 1, 100, 100, "Numeric", []),
            ('26Avi', 'FAILURE_TO_COMPLY', 1, 101, 101, "Numeric", []),
            ('26Avii', 'OTHER_SANCTION', 1, 102, 102, "Numeric", []),
            ('26B', 'RECOUPMENT_PRIOR_OVRPMT', 4, 103, 106, "Numeric", []),
            ('26Ci', 'OTHER_TOTAL_REDUCTIONS', 4, 107, 110, "Numeric", []),
            ('26Cii', 'FAMILY_CAP', 1, 111, 111, "Numeric", []),
            ('26Ciii', 'REDUCTIONS_ON_RECEIPTS', 1, 112, 112, "Numeric", []),
            ('26Civ', 'OTHER_NON_SANCTION', 1, 113, 113, "Numeric", []),
            ('27', 'WAIVER_EVAL_CONTROL_GRPS', 1, 114, 114, "Numeric", [t1_121]),
            ('28', 'FAMILY_EXEMPT_TIME_LIMITS', 2, 115, 116, "Numeric", [t1_122]),
            ('29', 'FAMILY_NEW_CHILD', 1, 117, 117, "Numeric", [t1_123]),
            ('blank', 'BLANK', 39, 118, 156, "Spaces", []),
        ]
    )
    return family_case_schema
