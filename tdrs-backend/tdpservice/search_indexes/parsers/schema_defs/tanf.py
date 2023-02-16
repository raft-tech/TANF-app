"""Houses definitions for TANF datafile schemas."""

from tdpservice.search_indexes.parsers.validators.category2 import t1_006, t1_007
from tdpservice.search_indexes.parsers.validators.category3 import t1_116

def row(item_number, description, length, start, end, data_type, cat2_conditions={}, cat3_conditions={}):
    """Return a dictionary representing a row in a schema."""
    return {
        'item_number': item_number,
        'description': description,
        'length': length,
        'start': start,
        'end': end,
        'data_type': data_type,
        'cat2_conditions': cat2_conditions,
        'cat3_conditions': cat3_conditions,
    }

"""
T1-099 13 RECEIVES SUBSIDIZED HOUSING ITEM 13 MUST = 1-3 WARNING
T1-100 14 RECEIVES MEDICAL ASSISTANCE ITEM 14 MUST = 1-2 WARNING
T1-101 15 RECEIVES FOOD STAMPS ITEM 15 MUST = 1-2 WARNING
T1-102 16 AMOUNT OF FOOD STAMP ASSISTANCE ITEM 16 MUST BE => 0 WARNING
T1-103 18 AMOUNT OF SUBSIDIZED CHILD CARE ITEM 18 MUST => 0 WARNING
T1-104 19 AMOUNT OF CHILD SUPPORT ITEM 19 MUST => 0 WARNING
T1-105 20 AMOUNT OF FAMILY'S CASH RESOURCES ITEM 20 MUST => 0 WARNING
T1-106 21 CASH AND CASH EQUIVALENTS IF ITEM 21A > 0, ITEM 21B MUST > 0 WARNING
T1-107 ITEM 21A AND ITEM 21B MUST => 0
T1-108 22 TANF CHILD CARE ITEM 22A AND ITEM 22B MUST => 0 WARNING
T1-109 IF ITEM 22A > 0, ITEM 22B MUST > 0
T1-139 IF ITEM 22A > 0, ITEM 22C MUST > 0
T1-110 23 TRANSPORTATION ITEM 23A AND ITEM 23B MUST => 0 WARNING
T1-111 IF ITEM 23A > 0, ITEM 23B MUST > 0
T1-112 24 TRANSITIONAL SERVICES ITEM 24A AND ITEM 24B MUST => 0 WARNING
T1-113 IF ITEM 24A > 0, ITEM 24B MUST > 0
T1-114 25 OTHER ITEM 25A AND ITEM 25B MUST => 0 WARNING
T1-115 IF ITEM 25A > 0, ITEM 25B MUST > 0
T1-116 26 REASON FOR & AMOUNT OF ASSISTANCE REDUCTIONS IF ITEM 26Ai > 0, ITEMS 26Aii THRU WARNING
ITEM 26vii MUST = 1 OR 2
T1-117 ITEM 26B MUST => 0
T1-118 IF ITEM 26Ci > 0, ITEMS 26Cii THRU
ITEM 26Civ MUST = 1OR 2
T1-121 27 WAIVER EVALUATION EXPERIMENTAL & CONTROL GROUPS ITEM 27 MUST = 9 OR BLANK WARNING
T1-122 28 IS TANF FAMILY EXEMPT FROM FEDERAL TIME-LIMIT PROVISIONS ITEM 28 MUST = 01-04, 06-09 WARNING
T1-123 29 IS TANF FAMILY A NEW CHILD-ONLY FAMILY ITEM 29 MUST = 1-2 WARNING
"""

def t1_schema():
    """Return a list of rows for T1 records."""
    return [
        row(None, 'RecordType', 2, 1, 2, "Alphanumeric"),
        row('4', 'RPT_MONTH_YEAR', 6, 3, 8, "Numeric", cat2_conditions={'custom': [t1_006, t1_007]}),
        row('6', 'CASE_NUMBER', 11, 9, 19, "Alphanumeric"),
        row('2', 'COUNTY_FIPS_CODE', 3, 20, 22, "Numeric"),
        row('5', 'STRATUM', 2, 23, 24, "Numeric", cat2_conditions={'gt': 0, 'lt': 100}),
        row('7', 'ZIP_CODE', 5, 25, 29, "Alphanumeric"),
        row('8', 'FUNDING_STREAM', 1, 30, 30, "Numeric", cat2_conditions={'in': [1, 2]}),
        row('9', 'DISPOSITION', 1, 31, 31, "Numeric", cat2_conditions={'in': [1, 2]}),
        row('10', 'NEW_APPLICANT', 1, 32, 32, "Numeric"),
        row('11', 'NBR_FAMILY_MEMBERS', 2, 33, 34, "Numeric", cat2_conditions={'gt': 0}),
        row('12', 'FAMILY_TYPE', 1, 35, 35, "Numeric", cat2_conditions={'in': [1, 2, 3]}),
        row('13', 'RECEIVES_SUB_HOUSING', 1, 36, 36, "Numeric", cat2_conditions={'in': [1, 2]}),
        row('14', 'RECEIVES_MED_ASSISTANCE', 1, 37, 37, "Numeric", cat2_conditions={'in': [1, 2]}),
        row('15', 'RECEIVES_FOOD_STAMPS', 1, 38, 38, "Numeric", cat2_conditions={'in': [1, 2]}),
        row('16', 'AMT_FOOD_STAMP_ASSISTANCE', 4, 39, 42, "Numeric", cat2_conditions={'gte': 0}),
        row('17', 'RECEIVES_SUB_CC', 1, 43, 43, "Numeric", cat2_conditions={'in': [1, 2, 3]}),
        row('18', 'AMT_SUB_CC', 4, 44, 47, "Numeric", cat2_conditions={'gte': 0}),
        row('19', 'CHILD_SUPPORT_AMT', 4, 48, 51, "Numeric", cat2_conditions={'gte': 0}),
        row('20', 'FAMILY_CASH_RESOURCES', 4, 52, 55, "Numeric", cat2_conditions={'gte': 0}),
        row('21A', 'CASH_AMOUNT', 4, 56, 59, "Numeric", cat2_conditions={'CASH_AMOUNT': {'gte': 0}, 'NBR_MONTHS': {'gte': 0}}, cat3_conditions={'NBR_MONTHS': {'gt': 0}, 'CASH_AMOUNT': {'gt': 0}}),
        row('21B', 'NBR_MONTHS', 3, 60, 62, "Numeric"),
        row('22A', 'CC_AMOUNT', 4, 63, 66, "Numeric", cat2_conditions={'CC_AMOUNT': {'gte': 0}, 'CHILDREN_COVERED': {'gte': 0}}, cat3_conditions={'CC_AMOUNT': {'gt': 0}, 'CHILDREN_COVERED': {'gt': 0}, 'CC_NBR_MONTHS': {'gt': 0}}),
        row('22B', 'CHILDREN_COVERED', 2, 67, 68, "Numeric"),
        row('22C', 'CC_NBR_MONTHS', 3, 69, 71, "Numeric"),
        row('23A', 'TRANSP_AMOUNT', 4, 72, 75, "Numeric", cat2_conditions={'TRANSP_AMOUNT': {'gte': 0}, 'TRANSP_NBR_MONTHS': {'gte': 0}}),
        row('23B', 'TRANSP_NBR_MONTHS', 3, 76, 78, "Numeric"),
        row('24A', 'TRANSITION_SERVICES_AMOUNT', 4, 79, 82, "Numeric", cat2_conditions={'TRANSITION_SERVICES_AMOUNT': {'gte': 0}, 'TRANSITION_NBR_MONTHS': {'gte': 0}}),
        row('24B', 'TRANSITION_NBR_MONTHS', 3, 83, 85, "Numeric"),
        row('25A', 'OTHER_AMOUNT', 4, 86, 89, "Numeric", cat2_conditions={'OTHER_AMOUNT': {'gte': 0}, 'OTHER_NBR_MONTHS': {'gte': 0}}, cat3_conditions={'OTHER_NBR_MONTHS': {'gt': 0}, 'OTHER_AMOUNT': {'gt': 0}}),
        row('25B', 'OTHER_NBR_MONTHS', 3, 90, 92, "Numeric"),
        row('26Ai', 'SANC_REDUCTION_AMT', 4, 93, 96, "Numeric", cat3_conditions={'custom': [t1_116]}),
        row('26Aii', 'WORK_REQ_SANCTION', 1, 97, 97, "Numeric"),
        row('26Aiii', 'FAMILY_SANC_ADULT', 1, 98, 98, "Numeric"),
        row('26Aiv', 'SANC_TEEN_PARENT', 1, 99, 99, "Numeric"),
        row('26Av', 'NON_COOPERATION_CSE', 1, 100, 100, "Numeric"),
        row('26Avi', 'FAILURE_TO_COMPLY', 1, 101, 101, "Numeric"),
        row('26Avii', 'OTHER_SANCTION', 1, 102, 102, "Numeric"),
        row('26B', 'RECOUPMENT_PRIOR_OVRPMT', 4, 103, 106, "Numeric"),
        row('26Ci', 'OTHER_TOTAL_REDUCTIONS', 4, 107, 110, "Numeric"),
        row('26Cii', 'FAMILY_CAP', 1, 111, 111, "Numeric"),
        row('26Ciii', 'REDUCTIONS_ON_RECEIPTS', 1, 112, 112, "Numeric"),
        row('26Civ', 'OTHER_NON_SANCTION', 1, 113, 113, "Numeric"),
        row('27', 'WAIVER_EVAL_CONTROL_GRPS', 1, 114, 114, "Numeric"),
        row('28', 'FAMILY_EXEMPT_TIME_LIMITS', 2, 115, 116, "Numeric", cat2_conditions={'in': [1, 2, 3, 4, 6, 7, 8, 9]}),
        row('29', 'FAMILY_NEW_CHILD', 1, 117, 117, "Numeric", cat2_conditions={'in': [1, 2]}),
        row('blank', 'BLANK', 39, 118, 156, "Spaces"),
    ]
