"""Test preparser functions and tanf_validator."""
import pytest

from tdpservice.search_indexes.models import T1
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
    )


all_t1_cat1_validators = [
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
    ]

@pytest.mark.parametrize('obj', all_t1_cat1_validators)
def test_t1_cat1_validators_valid(obj):
    """Test T1 Category 1 TANF Validations."""
    model_obj = make_valid_t1_model_obj()
    assert obj(model_obj) is True


@pytest.mark.parametrize('obj', all_t1_cat1_validators)
def test_t1_cat1_validators_invalid(obj):
    """Test T1 Category 1 TANF Validations."""
    model_obj = make_invalid_t1_model_obj()
    assert obj(model_obj) is False
