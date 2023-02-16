"""Test preparser functions and tanf_validator."""
import pytest

from tdpservice.search_indexes.models import T1
from tdpservice.search_indexes.parsers.tanf_parser import validate
from tdpservice.search_indexes.parsers.schema_defs.tanf import t1_schema
from tdpservice.search_indexes.parsers.validators.category2 import validate_cat2
from tdpservice.search_indexes.parsers.validators.category3 import validate_cat3

def make_valid_t1_model_obj():
    """Make a T1 model object."""
    return T1(
        RPT_MONTH_YEAR=202003,
        DISPOSITION=1,
        STRATUM=1,
        FUNDING_STREAM=1,
        NBR_FAMILY_MEMBERS=1,
        FAMILY_TYPE=1,
        RECEIVES_SUB_CC=1,
        RECEIVES_SUB_HOUSING=1,
        RECEIVES_MED_ASSISTANCE=1,
        RECEIVES_FOOD_STAMPS=1,
        AMT_FOOD_STAMP_ASSISTANCE=1,
        AMT_SUB_CC=1,
        CHILD_SUPPORT_AMT=1,
        FAMILY_CASH_RESOURCES=1,
        WAIVER_EVAL_CONTROL_GRPS=9,
        FAMILY_EXEMPT_TIME_LIMITS=1,
        FAMILY_NEW_CHILD=1,
        CASH_AMOUNT=0,
        NBR_MONTHS=0,
        CC_AMOUNT=0,
        CHILDREN_COVERED=0,
        TRANSP_AMOUNT=0,
        TRANSP_NBR_MONTHS=0,
        TRANSITION_SERVICES_AMOUNT=0,
        TRANSITION_NBR_MONTHS=0,
        OTHER_AMOUNT=0,
        OTHER_NBR_MONTHS=0,
        RECOUPMENT_PRIOR_OVRPMT=0,
        SANC_REDUCTION_AMT=1,
        WORK_REQ_SANCTION=1,
        FAMILY_SANC_ADULT=1,
        SANC_TEEN_PARENT=1,
        NON_COOPERATION_CSE=1,
        FAILURE_TO_COMPLY=1,
        OTHER_SANCTION=1,
        OTHER_TOTAL_REDUCTIONS=1,
        FAMILY_CAP=1,
        REDUCTIONS_ON_RECEIPTS=1,
        OTHER_NON_SANCTION=1,
        CASE_NUMBER=1,
    )

def make_invalid_t1_model_obj():
    """Make a T1 model object."""
    return T1(
        RPT_MONTH_YEAR=199700,
        DISPOSITION=0,
        STRATUM=-1,
        FUNDING_STREAM=0,
        NBR_FAMILY_MEMBERS=-1,
        FAMILY_TYPE=0,
        RECEIVES_SUB_CC=0,
        RECEIVES_SUB_HOUSING=0,
        RECEIVES_MED_ASSISTANCE=0,
        RECEIVES_FOOD_STAMPS=0,
        AMT_FOOD_STAMP_ASSISTANCE=-1,
        AMT_SUB_CC=-1,
        CHILD_SUPPORT_AMT=-1,
        FAMILY_CASH_RESOURCES=-1,
        WAIVER_EVAL_CONTROL_GRPS=8,
        FAMILY_EXEMPT_TIME_LIMITS=0,
        FAMILY_NEW_CHILD=0,
        CASH_AMOUNT=-1,
        NBR_MONTHS=-1,
        CC_AMOUNT=-1,
        CHILDREN_COVERED=-1,
        TRANSP_AMOUNT=-1,
        TRANSP_NBR_MONTHS=-1,
        TRANSITION_SERVICES_AMOUNT=-1,
        TRANSITION_NBR_MONTHS=-1,
        OTHER_AMOUNT=-5,
        OTHER_NBR_MONTHS=-1,
        RECOUPMENT_PRIOR_OVRPMT=-1,
        SANC_REDUCTION_AMT=1,
        WORK_REQ_SANCTION=0,
        FAMILY_SANC_ADULT=0,
        SANC_TEEN_PARENT=0,
        NON_COOPERATION_CSE=0,
        FAILURE_TO_COMPLY=0,
        OTHER_SANCTION=0,
        OTHER_TOTAL_REDUCTIONS=1,
        FAMILY_CAP=0,
        REDUCTIONS_ON_RECEIPTS=0,
        OTHER_NON_SANCTION=0,
        CASE_NUMBER='',
        CC_NBR_MONTHS=1,
    )

def test_validate_2():
    """Test the validate_cat2 function."""
    t1 = make_valid_t1_model_obj()
    family_case_schema = t1_schema()
    errors = validate(family_case_schema, t1, 'cat2_conditions', validate_cat2)
    print(errors)
    assert len(errors) == 0

cat2_expected_error_messages = [
    'MONTH value from RPT_MONTH_YEAR is not greater than or equal to 1. MONTH value from RPT_MONTH_YEAR is 0.',
    'YEAR value from RPT_MONTH_YEAR is not greater than or equal to 1998. YEAR value from RPT_MONTH_YEAR is 1997.',
    'FUNDING_STREAM is not in [1, 2]. FUNDING_STREAM is 0.',
]

@pytest.mark.parametrize('error_message', cat2_expected_error_messages)
def test_validate_2_invalid(error_message):
    """Test the validate_cat2 function."""
    t1 = make_invalid_t1_model_obj()
    family_case_schema = t1_schema()
    errors = validate(family_case_schema, t1, 'cat2_conditions', validate_cat2)

    assert error_message in str(errors)

def test_validate_3():
    """Test the validate_cat3 function."""
    model_obj = make_valid_t1_model_obj()
    model_obj.CASH_AMOUNT = 1
    model_obj.NBR_MONTHS = 1
    model_obj.CC_AMOUNT = 1
    model_obj.CC_NBR_MONTHS = 1
    model_obj.CHILDREN_COVERED = 1
    model_obj.TRANSP_AMOUNT = 1
    model_obj.TRANSP_NBR_MONTHS = 1
    model_obj.TRANSITION_SERVICES_AMOUNT = 1
    model_obj.TRANSITION_NBR_MONTHS = 1
    model_obj.OTHER_AMOUNT = 1
    model_obj.OTHER_NBR_MONTHS = 1
    model_obj.DISPOSITION = 2

    family_case_schema = t1_schema()
    errors = validate(family_case_schema, model_obj, 'cat3_conditions', validate_cat3)
    print(errors)
    assert len(errors) == 0

cat3_expected_error_messages = [
    'OTHER_AMOUNT is greater than 0, so OTHER_NBR_MONTHS should be greater than 0. OTHER_NBR_MONTHS is -1.',
]   

@pytest.mark.parametrize('expected_error_message', cat3_expected_error_messages)
def test_validate_3_invalid(expected_error_message):
    """Test the validate_cat3 function."""
    model_obj = make_invalid_t1_model_obj()
    model_obj.OTHER_AMOUNT = 1
    model_obj.OTHER_NBR_MONTHS = -1
    model_obj.NBR_MONTHS = 0
    model_obj.SANC_REDUCTION_AMT = 0

    family_case_schema = t1_schema()
    errors = validate(family_case_schema, model_obj, 'cat3_conditions', validate_cat3)

    assert expected_error_message in str(errors)
