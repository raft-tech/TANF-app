"""Tests for generic validator functions."""

import pytest
from .. import validators
from ..schema_defs import cat3_validators
from tdpservice.parsers.test.factories import TanfT1Factory


def test_matches_returns_valid():
    """Test `matches` gives a valid result."""
    value = 'TEST'

    validator = validators.matches('TEST')
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_matches_returns_invalid():
    """Test `matches` gives an invalid result."""
    value = 'TEST'

    validator = validators.matches('test')
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == 'TEST does not match test.'


def test_oneOf_returns_valid():
    """Test `oneOf` gives a valid result."""
    value = 17
    options = [17, 24, 36]

    validator = validators.oneOf(options)
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_oneOf_returns_invalid():
    """Test `oneOf` gives an invalid result."""
    value = 64
    options = [17, 24, 36]

    validator = validators.oneOf(options)
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == '64 is not in [17, 24, 36].'


def test_between_returns_valid():
    """Test `between` gives a valid result for integers."""
    value = 47

    validator = validators.between(3, 400)
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_between_returns_valid_for_string_value():
    """Test `between` gives a valid result for strings."""
    value = '047'

    validator = validators.between(3, 400)
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_between_returns_invalid():
    """Test `between` gives an invalid result for integers."""
    value = 47

    validator = validators.between(48, 400)
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == '47 is not between 48 and 400.'


def test_between_returns_invalid_for_string_value():
    """Test `between` gives an invalid result for strings."""
    value = '047'

    validator = validators.between(100, 400)
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == '047 is not between 100 and 400.'


def test_hasLength_returns_valid():
    """Test `hasLength` gives a valid result."""
    value = 'abcd123'

    validator = validators.hasLength(7)
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_hasLength_returns_invalid():
    """Test `hasLength` gives an invalid result."""
    value = 'abcd123'

    validator = validators.hasLength(22)
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == 'Value length 7 does not match 22.'


def test_contains_returns_valid():
    """Test `contains` gives a valid result."""
    value = '12345abcde'

    validator = validators.contains('2345')
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_contains_returns_invalid():
    """Test `contains` gives an invalid result."""
    value = '12345abcde'

    validator = validators.contains('6789')
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == '12345abcde does not contain 6789.'


def test_startsWith_returns_valid():
    """Test `startsWith` gives a valid result."""
    value = '12345abcde'

    validator = validators.startsWith('1234')
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_startsWith_returns_invalid():
    """Test `startsWith` gives an invalid result."""
    value = '12345abcde'

    validator = validators.startsWith('abc')
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == '12345abcde does not start with abc.'


def test_notEmpty_returns_valid_full_string():
    """Test `notEmpty` gives a valid result for a full string."""
    value = '1        '

    validator = validators.notEmpty()
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_notEmpty_returns_invalid_full_string():
    """Test `notEmpty` gives an invalid result for a full string."""
    value = '         '

    validator = validators.notEmpty()
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == '          contains blanks between positions 0 and 9.'


def test_notEmpty_returns_valid_substring():
    """Test `notEmpty` gives a valid result for a partial string."""
    value = '11122333'

    validator = validators.notEmpty(start=3, end=5)
    is_valid, error = validator(value)

    assert is_valid is True
    assert error is None


def test_notEmpty_returns_invalid_substring():
    """Test `notEmpty` gives an invalid result for a partial string."""
    value = '111  333'

    validator = validators.notEmpty(start=3, end=5)
    is_valid, error = validator(value)

    assert is_valid is False
    assert error == "111  333 contains blanks between positions 3 and 5."



@pytest.mark.usefixtures('db')
class TanfSection1TestCat3ValidatorsBase:
    @pytest.fixture
    def record(self):
        raise NotImplementedError()


class TestT1Cat3Validators(TanfSection1TestCat3ValidatorsBase):
    @pytest.fixture
    def record(self):
        return TanfT1Factory.create()
    
    def test_validate_disposition(self, record):
        result = cat3_validators.validate_disposition(record)
        assert result == (True, None)

        record.DISPOSITION = 2
        record.COUNTY_FIPS_CODE = ' '
        record.RPT_MONTH_YEAR = ' '
        record.STRATUM = ' '
        record.CASE_NUMBER = ' '
        result = cat3_validators.validate_disposition(record)
        assert result == (False, "FATAL: IF ITEM 9 = 2, THEN ITEMS 1,4-6 MUST NOT BE BLANK")
    
    def test_validate_cash_amount_and_nbr_months(self, record):
        result = cat3_validators.validate_cash_amount_and_nbr_months(record)
        assert result == (True, None)

        record.CASH_AMOUNT = 0
        record.NBR_MONTHS = -1
        result = cat3_validators.validate_cash_amount_and_nbr_months(record)
        assert result == (False, "WARNING: ITEM 21A AND ITEM 21B MUST => 0")

        record.CASH_AMOUNT = 100
        record.NBR_MONTHS = 0
        result = cat3_validators.validate_cash_amount_and_nbr_months(record)
        assert result == (False, "WARNING: IF ITEM 21A > 0, ITEM 21B MUST > 0")
    
    def test_validate_child_care(self, record):
        result = cat3_validators.validate_child_care(record)
        assert result == (True, None)

        record.CC_AMOUNT = 0
        record.CHILDREN_COVERED = -1
        result = cat3_validators.validate_child_care(record)
        assert result == (False, "WARNING: ITEM 22A AND ITEM 22B MUST => 0")

        record.CC_AMOUNT = 10
        record.CHILDREN_COVERED = -1
        record.CC_NBR_MONTHS = -1
        result = cat3_validators.validate_child_care(record)
        assert result == (False, "WARNING: IF ITEM 22A > 0, ITEM 22B MUST > 0, ITEM 22C MUST > 0")

    def test_validate_transportation(self, record):
        result = cat3_validators.validate_transportation(record)
        assert result == (True, None)

        record.TRANSP_AMOUNT = 0
        record.TRANSP_NBR_MONTHS = -1
        result = cat3_validators.validate_transportation(record)
        assert result == (False, "WARNING: ITEM 23A AND ITEM 23B MUST => 0")

        record.TRANSP_AMOUNT = 100
        record.TRANSP_NBR_MONTHS = 0
        result = cat3_validators.validate_transportation(record)
        assert result == (False, "WARNING: IF ITEM 23A > 0, ITEM 23B MUST > 0")

    def test_validate_transitional_services(self, record):
        result = cat3_validators.validate_transitional_services(record)
        assert result == (True, None)

        record.TRANSITION_SERVICES_AMOUNT = 0
        record.TRANSITION_NBR_MONTHS = -1
        result = cat3_validators.validate_transitional_services(record)
        assert result == (False, "WARNING: ITEM 24A AND ITEM 24B MUST => 0")

        record.TRANSITION_SERVICES_AMOUNT = 100
        record.TRANSITION_NBR_MONTHS = 0
        result = cat3_validators.validate_transitional_services(record)
        assert result == (False, "WARNING: IF ITEM 24A > 0, ITEM 24B MUST > 0")

    def test_validate_other(self, record):
        result = cat3_validators.validate_other(record)
        assert result == (True, None)

        record.OTHER_AMOUNT = 0
        record.OTHER_NBR_MONTHS = -1
        result = cat3_validators.validate_other(record)
        assert result == (False, "WARNING: ITEM 25A AND ITEM 25B MUST => 0")

        record.OTHER_AMOUNT = 100
        record.OTHER_NBR_MONTHS = 0
        result = cat3_validators.validate_other(record)
        assert result == (False, "WARNING: IF ITEM 25A > 0, ITEM 25B MUST > 0")
        
    def test_validate_reasons_for_amount_of_assistance_reductions(self, record):
        record.SANC_REDUCTION_AMT = 0
        record.OTHER_TOTAL_REDUCTIONS = 0
        result = cat3_validators.validate_reasons_for_amount_of_assistance_reductions(record)
        assert result == (True, None)

        record.SANC_REDUCTION_AMT = 10
        record.WORK_REQ_SANCTION = -1
        result = cat3_validators.validate_reasons_for_amount_of_assistance_reductions(record)
        assert result == (False, "WARNING: IF ITEM 26Ai > 0, ITEMS 26Aii THRU")

        record.SANC_REDUCTION_AMT = 0
        record.OTHER_TOTAL_REDUCTIONS = 100
        record.OTHER_NON_SANCTION = -1
        result = cat3_validators.validate_reasons_for_amount_of_assistance_reductions(record)
        assert result == (False, "WARNING: IF ITEM 26Ci > 0, ITEMS 26Cii THRU")
