"""Tests for generic validator functions."""

import pytest
from .. import validators
from tdpservice.parsers.test.factories import TanfT5Factory, TanfT6Factory


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
class TestCat3ValidatorsBase:
    """A base test class for tests that evaluate category three validators."""

    @pytest.fixture
    def record(self):
        """Record instance that returns a valid Section 1 record.

        This fixture must be overridden in all child classes.
        """
        raise NotImplementedError()


class TestT5Cat3Validators(TestCat3ValidatorsBase):
    """Test category three validators for TANF T5 records."""

    @pytest.fixture
    def record(self):
        """Override default record with TANF T5 record."""
        return TanfT5Factory.create()

    def test_validate_ssn(self, record):
        """Test cat3 validator for SSN."""
        val = validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.notMatches(1),
                  result_field='SSN', result_function=validators.isNumber()
                  )

        result = val(record)
        assert result == (True, None)

        record.SSN = "abc"
        record.FAMILY_AFFILIATION = 2

        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :2 validator1 passed then SSN abc is not a number.')

    def test_validate_ssn_citizenship(self, record):
        """Test cat3 validator for SSN/citizenship."""
        val = validators.validate__FAM_AFF__SSN()

        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 2
        record.SSN = "000000000"

        result = val(record)
        assert result == (False, "If FAMILY_AFFILIATION ==2 and CITIZENSHIP_STATUS==1 or 2, then SSN " +
                          "!= 000000000 -- 999999999.")

    def test_validate_race_ethnicity(self, record):
        """Test cat3 validator for race/ethnicity."""
        races = ["RACE_HISPANIC", "RACE_AMER_INDIAN", "RACE_ASIAN", "RACE_BLACK", "RACE_HAWAIIAN", "RACE_WHITE"]
        record.FAMILY_AFFILIATION = 1
        for race in races:
            val = validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field='RACE_HISPANIC', result_function=validators.isInLimits(1, 2)
                  )
            result = val(record)
            assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.RACE_HISPANIC = 0
        record.RACE_AMER_INDIAN = 0
        record.RACE_ASIAN = 0
        record.RACE_BLACK = 0
        record.RACE_HAWAIIAN = 0
        record.RACE_WHITE = 0
        for race in races:
            val = validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field=race, result_function=validators.isInLimits(1, 2)
                  )
            result = val(record)
            assert result == (False, f'if FAMILY_AFFILIATION :1 validator1 passed then {race} 0 is not ' +
                              'larger and equal to 1 and smaller and equal to 2.')

    def test_validate_marital_status(self, record):
        """Test cat3 validator for marital status."""
        val = validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                    result_field='MARITAL_STATUS', result_function=validators.isInLimits(0, 5)
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 2
        record.MARITAL_STATUS = 6

        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :2 validator1 passed then MARITAL_STATUS 6 is not ' +
                          'larger and equal to 0 and smaller and equal to 5.')

    def test_validate_parent_minor(self, record):
        """Test cat3 validator for parent with minor."""
        val = validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 2),
                    result_field='PARENT_MINOR_CHILD', result_function=validators.isInLimits(1, 3)
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 2
        record.PARENT_MINOR_CHILD = 0

        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :2 validator1 passed then PARENT_MINOR_CHILD 0 is not ' +
                          'larger and equal to 1 and smaller and equal to 3.')

    def test_validate_education(self, record):
        """Test cat3 validator for education level."""
        val = validators.if_then_validator(
                  condition_field='FAMILY_AFFILIATION', condition_function=validators.isInLimits(1, 3),
                  result_field='EDUCATION_LEVEL', result_function=validators.or_validators(
                      validators.isInStringRange(1, 16, 2),
                      validators.isInStringRange(98, 99)
                      )
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 2
        record.EDUCATION_LEVEL = "0"

        result = val(record)
        assert result == (False, "if FAMILY_AFFILIATION :2 validator1 passed then EDUCATION_LEVEL 0 is not in range " +
                          "[1, 16]. or 0 is not in range [98, 99].")

    def test_validate_citizenship_status(self, record):
        """Test cat3 validator for citizenship status."""
        val = validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                    result_field='CITIZENSHIP_STATUS', result_function=validators.isInLimits(1, 2)
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.CITIZENSHIP_STATUS = 0

        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :1 validator1 passed then CITIZENSHIP_STATUS 0 is not ' +
                          'larger and equal to 1 and smaller and equal to 2.')

    def test_validate_hoh_fed_time(self, record):
        """Test cat3 validator for federal disability."""
        val = validators.validate__FAM_AFF__HOH__FEDTIME()

        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.RELATIONSHIP_HOH = 1
        record.COUNTABLE_MONTH_FED_TIME = 1

        result = val(record)
        assert result == (False, "If FAMILY_AFFILIATION == 1 and RELATIONSHIP_HOH == 1 or 2, "
                          + "then COUNTABLE_MONTH_FED_TIME >= 001.")

    def test_validate_oasdi_insurance(self, record):
        """Test cat3 validator for OASDI insurance."""
        val = validators.if_then_validator(
                    condition_field='DATE_OF_BIRTH', condition_function=validators.olderThan(18),
                    result_field='REC_OASDI_INSURANCE', result_function=validators.isInLimits(1, 2)
                  )

        record.DATE_OF_BIRTH = 0
        result = val(record)
        assert result == (True, None)

        record.DATE_OF_BIRTH = 200001
        record.REC_OASDI_INSURANCE = 0

        result = val(record)
        assert result == (False, 'if DATE_OF_BIRTH :200001 validator1 passed then REC_OASDI_INSURANCE 0 is not ' +
                          'larger and equal to 1 and smaller and equal to 2.')

    def test_validate_federal_disability(self, record):
        """Test cat3 validator for federal disability."""
        val = validators.if_then_validator(
                    condition_field='FAMILY_AFFILIATION', condition_function=validators.matches(1),
                    result_field='REC_FEDERAL_DISABILITY', result_function=validators.isInLimits(1, 2)
                  )

        record.FAMILY_AFFILIATION = 0
        result = val(record)
        assert result == (True, None)

        record.FAMILY_AFFILIATION = 1
        record.REC_FEDERAL_DISABILITY = 0

        result = val(record)
        assert result == (False, 'if FAMILY_AFFILIATION :1 validator1 passed then REC_FEDERAL_DISABILITY 0 is not ' +
                          'larger and equal to 1 and smaller and equal to 2.')


class TestT6Cat3Validators(TestCat3ValidatorsBase):
    """Test category three validators for TANF T6 records."""

    @pytest.fixture
    def record(self):
        """Override default record with TANF T6 record."""
        return TanfT6Factory.create()

    def test_sum_of_applications(self, record):
        """Test cat3 validator for sum of applications."""
        val = validators.sumIsEqual("NUM_APPLICATIONS", ["NUM_APPROVED", "NUM_DENIED"])

        record.NUM_APPLICATIONS = 2
        result = val(record)

        assert result == (True, None)

        record.NUM_APPLICATIONS = 1
        result = val(record)

        assert result == (False, f"The sum of ['NUM_APPROVED', 'NUM_DENIED'] does not equal NUM_APPLICATIONS.")

    def test_sum_of_families(self, record):
        """Test cat3 validator for sum of families."""
        val = validators.sumIsEqual("NUM_FAMILIES", ["NUM_2_PARENTS", "NUM_1_PARENTS", "NUM_NO_PARENTS"])

        record.NUM_FAMILIES = 3
        result = val(record)

        assert result == (True, None)

        record.NUM_FAMILIES = 1
        result = val(record)

        assert result == (False, "The sum of ['NUM_2_PARENTS', 'NUM_1_PARENTS', 'NUM_NO_PARENTS'] does not equal " +
                          "NUM_FAMILIES.")

    def test_sum_of_recipients(self, record):
        """Test cat3 validator for sum of recipients."""
        val = validators.sumIsEqual("NUM_RECIPIENTS", ["NUM_ADULT_RECIPIENTS", "NUM_CHILD_RECIPIENTS"])

        record.NUM_RECIPIENTS = 2
        result = val(record)

        assert result == (True, None)

        record.NUM_RECIPIENTS = 1
        result = val(record)

        assert result == (False, "The sum of ['NUM_ADULT_RECIPIENTS', 'NUM_CHILD_RECIPIENTS'] does not equal " +
                          "NUM_RECIPIENTS.")
