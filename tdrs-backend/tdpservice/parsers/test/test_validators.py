"""Tests for generic validator functions."""

import pytest
from .. import validators
from ..schema_defs import cat3_validators
from tdpservice.parsers.test.factories import TanfT1Factory, TanfT2Factory, TanfT3Factory


def test_or_validators():
    value = "2"
    validator = validators.or_validators(validators.matches(("2")), validators.matches(("3","4")))
    assert validator(value)==(True, None)

    validator = validators.or_validators(validators.matches(("5")), validators.matches(("3","4")))
    print(validator(value))
    assert validator(value)==(False, "2 does not match 5. and 2 does not match ('3', '4').")


def test_if_validators():
    value = "2"
    validator = validators.if_then_validator(validators.matches(("2")), validators.matches(("3","4")))
    assert validator(value)==(False, "2 does not match ('3', '4').")

    validator = validators.if_then_validator(validators.matches(("3")), validators.matches(("3","4")))
    assert validator(value)==(True, None)

def test_or_cross_field_validators():
    value1 = "2"
    value2 = "3"
    validator = validators.or_validators(validators.matches(("4")), validators.matches(("4")))
    assert validator(value1, value2)==(False, '2 does not match 4. and 3 does not match 4.')


def test_month_year_yearIsLargerThan():
    value = "061998"
    validator = validators.month_year_yearIsLargerThan(1999)
    assert validator(value)==(False, '1998 year must be larger than 1999.')


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
    """A base test class for tests that evaluate category three validators."""

    @pytest.fixture
    def record(self):
        """Record instance that returns a valid Section 1 record.

        This fixture must be overridden in all child classes.
        """
        raise NotImplementedError()


class TestT1Cat3Validators(TanfSection1TestCat3ValidatorsBase):
    """Test category three validators for TANF T1 records."""

    @pytest.fixture
    def record(self):
        """Override default record with TANF T1 record."""
        return TanfT1Factory.create()

    def test_validate_food_stamps(self, record):
        """Test cat3 validator for food stamps."""
        record.RECEIVES_FOOD_STAMPS = 0
        record.AMT_FOOD_STAMP_ASSISTANCE = 0
        result = cat3_validators.validate_food_stamps(record)
        assert result == (True, None)

        record.AMT_FOOD_STAMP_ASSISTANCE = 1
        result = cat3_validators.validate_food_stamps(record)
        assert result == (False, "IF ITEM 16 > 0 THEN ITEM 15 == 1")

    def test_validate_subsidized_child_care(self, record):
        """Test cat3 validator for subsidized child care."""
        result = cat3_validators.validate_subsidized_child_care(record)
        assert result == (True, None)

        record.RECEIVES_SUB_CC = 3
        record.AMT_SUB_CC = 1
        result = cat3_validators.validate_subsidized_child_care(record)
        assert result == (False, "IF ITEM 18 > 0 THEN ITEM 17 != 3")

    def test_validate_cash_amount_and_nbr_months(self, record):
        """Test cat3 validator for cash amount and number of months."""
        result = cat3_validators.validate_cash_amount_and_nbr_months(record)
        assert result == (True, None)

        record.CASH_AMOUNT = 0
        record.NBR_MONTHS = -1
        result = cat3_validators.validate_cash_amount_and_nbr_months(record)
        assert result == (False, "ITEM 21A AND ITEM 21B MUST => 0")

        record.CASH_AMOUNT = 100
        record.NBR_MONTHS = 0
        result = cat3_validators.validate_cash_amount_and_nbr_months(record)
        assert result == (False, "IF ITEM 21A > 0, ITEM 21B MUST > 0")

    def test_validate_child_care(self, record):
        """Test cat3 validator for child care."""
        result = cat3_validators.validate_child_care(record)
        assert result == (True, None)

        record.CC_AMOUNT = 0
        record.CHILDREN_COVERED = -1
        result = cat3_validators.validate_child_care(record)
        assert result == (False, "ITEM 22A AND ITEM 22B MUST => 0")

        record.CC_AMOUNT = 10
        record.CHILDREN_COVERED = -1
        record.CC_NBR_MONTHS = -1
        result = cat3_validators.validate_child_care(record)
        assert result == (False, "IF ITEM 22A > 0, ITEM 22B MUST > 0, ITEM 22C MUST > 0")

    def test_validate_transportation(self, record):
        """Test cat3 validator for transportation."""
        result = cat3_validators.validate_transportation(record)
        assert result == (True, None)

        record.TRANSP_AMOUNT = 0
        record.TRANSP_NBR_MONTHS = -1
        result = cat3_validators.validate_transportation(record)
        assert result == (False, "ITEM 23A AND ITEM 23B MUST => 0")

        record.TRANSP_AMOUNT = 100
        record.TRANSP_NBR_MONTHS = 0
        result = cat3_validators.validate_transportation(record)
        assert result == (False, "IF ITEM 23A > 0, ITEM 23B MUST > 0")

    def test_validate_transitional_services(self, record):
        """Test cat3 validator for transitional services."""
        result = cat3_validators.validate_transitional_services(record)
        assert result == (True, None)

        record.TRANSITION_SERVICES_AMOUNT = 0
        record.TRANSITION_NBR_MONTHS = -1
        result = cat3_validators.validate_transitional_services(record)
        assert result == (False, "ITEM 24A AND ITEM 24B MUST => 0")

        record.TRANSITION_SERVICES_AMOUNT = 100
        record.TRANSITION_NBR_MONTHS = 0
        result = cat3_validators.validate_transitional_services(record)
        assert result == (False, "IF ITEM 24A > 0, ITEM 24B MUST > 0")

    def test_validate_other(self, record):
        """Test cat3 validator for other."""
        result = cat3_validators.validate_other(record)
        assert result == (True, None)

        record.OTHER_AMOUNT = 0
        record.OTHER_NBR_MONTHS = -1
        result = cat3_validators.validate_other(record)
        assert result == (False, "ITEM 25A AND ITEM 25B MUST => 0")

        record.OTHER_AMOUNT = 100
        record.OTHER_NBR_MONTHS = 0
        result = cat3_validators.validate_other(record)
        assert result == (False, "IF ITEM 25A > 0, ITEM 25B MUST > 0")

    def test_validate_reasons_for_amount_of_assistance_reductions(self, record):
        """Test cat3 validator for assistance reductions."""
        record.SANC_REDUCTION_AMT = 0
        record.OTHER_TOTAL_REDUCTIONS = 0
        result = cat3_validators.validate_reasons_for_amount_of_assistance_reductions(record)
        assert result == (True, None)

        record.SANC_REDUCTION_AMT = 10
        record.WORK_REQ_SANCTION = -1
        result = cat3_validators.validate_reasons_for_amount_of_assistance_reductions(record)
        assert result == (False, "IF ITEM 26Ai > 0, ITEMS 26Aii THRU")

        record.SANC_REDUCTION_AMT = 0
        record.OTHER_TOTAL_REDUCTIONS = 100
        record.OTHER_NON_SANCTION = -1
        result = cat3_validators.validate_reasons_for_amount_of_assistance_reductions(record)
        assert result == (False, "IF ITEM 26Ci > 0, ITEMS 26Cii THRU")


class TestT2Cat3Validators(TanfSection1TestCat3ValidatorsBase):
    """Test category three validators for TANF T2 records."""

    @pytest.fixture
    def record(self):
        """Override default record with TANF T2 record."""
        return TanfT2Factory.create()

    def test_validate_ssn(self, record):
        """Test cat3 validator for social security number."""
        record.SSN = "999999999"
        record.FAMILY_AFFILIATION = ""
        result = cat3_validators.validate_ssn(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = "1"
        result = cat3_validators.validate_ssn(record)
        assert result == (False, "IF ITEM 30 == 1 THEN ITEM 33 != 000000000 -- 999999999")

    def test_validate_race_ethnicity(self, record):
        """Test cat3 validator for race/ethnicity."""
        races = ["RACE_HISPANIC", "RACE_AMER_INDIAN", "RACE_ASIAN", "RACE_BLACK", "RACE_HAWAIIAN", "RACE_WHITE"]
        items = ["34A", "34B", "34C", "34D", "34E", "34F"]
        record.FAMILY_AFFILIATION = 0
        for race, item in zip(races, items):
            result = cat3_validators.validate_race_ethnicity(record)
            assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        for race, item in zip(races, items):
            ref = getattr(record, race)
            ref = ""
            assert ref == ""
            result = cat3_validators.validate_race_ethnicity(record)
            assert result == (False, "IF ITEM 30 == 1, 2, OR 3, THEN ITEMS 34A-34F == 1 OR 2")

    def test_validate_marital_status(self, record):
        """Test cat3 validator for marital status."""
        record.FAMILY_AFFILIATION = 0
        result = cat3_validators.validate_marital_status(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 3
        record.MARITAL_STATUS = ""
        result = cat3_validators.validate_marital_status(record)
        assert result == (False, "IF ITEM 30 == 1, 2, OR 3, THEN ITEM 37 == 1, 2, 3, 4, or 5")

    def test_validate_parent_with_minor(self, record):
        """Test cat3 validator for parent with a minor child."""
        record.FAMILY_AFFILIATION = 0
        result = cat3_validators.validate_parent_with_minor(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 2
        record.PARENT_WITH_MINOR_CHILD = ""
        result = cat3_validators.validate_parent_with_minor(record)
        assert result == (False, "IF ITEM 30 == 1, 2 THEN ITEM 39 MUST = 1-3")

    def test_validate_education_level(self, record):
        """Test cat3 validator for education level."""
        record.FAMILY_AFFILIATION = 5
        result = cat3_validators.validate_education_level(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.EDUCATION_LEVEL = "00"
        result = cat3_validators.validate_education_level(record)
        assert result == (False, "IF ITEM 30 == 1-3 ITEM 41 MUST == 01-16,98,99")

    def test_validate_citizenship(self, record):
        """Test cat3 validator for citizenship."""
        record.FAMILY_AFFILIATION = 0
        result = cat3_validators.validate_citizenship(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 2
        record.CITIZENSHIP_STATUS = "2"
        record.SSN = "999999999"
        result = cat3_validators.validate_citizenship(record)
        assert result == (False, "IF ITEM 30 == 2 AND ITEM 42 == 1 OR 2, THEN ITEM 33 != 000000000 -- 999999999")

        record.FAMILY_AFFILIATION = 1
        record.CITIZENSHIP_STATUS = "3"
        result = cat3_validators.validate_citizenship(record)
        assert result == (False, "IF ITEM 30 == 1 THEN ITEM 42 == 1 OR 2")

    def test_validate_cooperation_with_child_support(self, record):
        """Test cat3 validator for cooperation with child support."""
        record.FAMILY_AFFILIATION = 0
        result = cat3_validators.validate_cooperation_with_child_support(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.COOPERATION_CHILD_SUPPORT = ""
        result = cat3_validators.validate_cooperation_with_child_support(record)
        assert result == (False, "IF ITEM 30 == 1, 2, or 3, THEN ITEM 43 == 1,2, or 9")

    def test_validate_months_federal_time_limit(self, record):
        """Test cat3 validator for federal time limit."""
        record.FAMILY_AFFILIATION = 0
        result = cat3_validators.validate_months_federal_time_limit(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.MONTHS_FED_TIME_LIMIT = 0
        record.RELATIONSHIP_HOH = 1
        result = cat3_validators.validate_months_federal_time_limit(record)
        assert result == (False, "IF ITEM 30 = 1 AND ITEM 38=1 OR 2, THEN ITEM 44 MUST => 1")

    def test_validate_employment_status(self, record):
        """Test cat3 validator for employment status."""
        record.FAMILY_AFFILIATION = 0
        result = cat3_validators.validate_employment_status(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 3
        record.EMPLOYMENT_STATUS = "4"
        result = cat3_validators.validate_employment_status(record)
        assert result == (False, "IF ITEM 30 = 1-4 THEN ITEM 47 MUST = 1-3")

    def test_validate_work_eligible_indicator(self, record):
        """Test cat3 validator for work eligibility."""
        record.FAMILY_AFFILIATION = 0
        result = cat3_validators.validate_work_eligible_indicator(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.WORK_ELIGIBLE_INDICATOR = "00"
        result = cat3_validators.validate_work_eligible_indicator(record)
        assert result == (False, "IF ITEM 30 == 1 or 2, THEN ITEM 48 == 01-09, OR 12")

    def test_validate_work_participation(self, record):
        """Test cat3 validator for work participation."""
        record.FAMILY_AFFILIATION = 0
        result = cat3_validators.validate_work_participation(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 2
        record.WORK_PART_STATUS = "00"
        result = cat3_validators.validate_work_participation(record)
        assert result == (False, "IF ITEM 30 == 1 or 2, THEN ITEM 49 MUST = 01-02, 05, 07, 09, 15-19, or 99")

        record.WORK_PART_STATUS = "99"
        record.WORK_ELIGIBLE_INDICATOR = "01"
        result = cat3_validators.validate_work_participation(record)
        assert result == (False, "IF ITEM 48 == 01-05, THEN ITEM 49 != 99")


class TestT3Cat3Validators(TanfSection1TestCat3ValidatorsBase):
    """Test category three validators for TANF T3 records."""

    @pytest.fixture
    def record(self):
        """Override default record with TANF T3 record."""
        return TanfT3Factory.create()

    def test_validate_t3_race_ethnicity(self, record):
        """Test cat3 validator for race/ethnicity."""
        races = ["RACE_HISPANIC", "RACE_AMER_INDIAN", "RACE_ASIAN", "RACE_BLACK", "RACE_HAWAIIAN", "RACE_WHITE"]
        record.FAMILY_AFFILIATION = 0
        for race in races:
            result = cat3_validators.validate_t3_race_ethnicity(record)
            assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        for race in races:
            ref = getattr(record, race)
            ref = ""
            assert ref == ""
            result = cat3_validators.validate_t3_race_ethnicity(record)
            assert result == (False, "IF ITEM 67 == 1, 2, OR 3, THEN ITEMS 70A-70F == 1 OR 2")

    def test_validate_relationship_hoh(self, record):
        """Test cat3 validator for relationship to head of household."""
        record.FAMILY_AFFILIATION = 0
        record.RELATIONSHIP_HOH = "04"
        result = cat3_validators.validate_relationship_hoh(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 2
        record.RELATIONSHIP_HOH = ""
        result = cat3_validators.validate_relationship_hoh(record)
        assert result == (False, "IF ITEM 67 == 1 or 2, THEN ITEM 73 == 04-09")

    def test_validate_t3_education_level(self, record):
        """Test cat3 validator for education level."""
        record.FAMILY_AFFILIATION = 0
        result = cat3_validators.validate_t3_education_level(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.EDUCATION_LEVEL = "99"
        result = cat3_validators.validate_t3_education_level(record)
        assert result == (False, "IF ITEM 67 == 1 THEN ITEM 75 != 99")

    def test_validate_t3_citizenship(self, record):
        """Test cat3 validator for citizenship."""
        record.FAMILY_AFFILIATION = 0
        result = cat3_validators.validate_t3_citizenship(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.CITIZENSHIP_STATUS = "00"
        result = cat3_validators.validate_t3_citizenship(record)
        assert result == (False, "IF ITEM 67 == 1 THEN ITEM 76 == 1 OR 2")

        record.FAMILY_AFFILIATION = 2
        result = cat3_validators.validate_t3_citizenship(record)
        assert result == (False, "IF ITEM 67 == 2 THEN ITEM 76 == 2 OR 9")
