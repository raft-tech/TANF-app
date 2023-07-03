"""Generic parser validator functions for use in schema definitions."""

from .util import generate_parser_error
from .models import ParserErrorCategoryChoices
from tdpservice.data_files.models import DataFile

# higher order validator func

def make_validator(validator_func, error_func):
    """Return a function accepting a value input and returning (bool, string) to represent validation state."""
    return lambda value: (True, None) if validator_func(value) else (False, error_func(value))


# validator combinators

def or_validators(validator1, validator2):
    """Return a validator that is true only if one of the two validators is true."""
    return lambda value: (True, None) if (validator1(value)[0] or validator2(value)[0])\
        else (False, validator1(value)[1] + ' or ' + validator2(value)[1])


def if_then_validator(condition_field, condition_function,
                      result_field, result_function):
    """Return second validation if the first validator is true.

    :param validator1: function that returns (bool, string) to represent validation state
    :param validator2: function that returns (bool, string) to represent validation state
    :param args: list of two strings representing the keys of the values to be validated
    """
    def if_then_validator_func(value):
        value1 = value[condition_field] if type(value) is dict else getattr(value, condition_field)
        value2 = value[result_field] if type(value) is dict else getattr(value, result_field)

        validator1_result = condition_function(value1)
        validator2_result = result_function(value2)
        return (True, None) if validator1_result[0] and validator2_result[0] else (validator1_result[0] &
                                                                                   validator2_result[0], 'if ' +
                                                                                   (validator1_result[1] if
                                                                                    validator1_result[1] is not None
                                                                                    else "validator1 passed") + ' then '
                                                                                   + (validator2_result[1] if
                                                                                       validator2_result[1] is not None
                                                                                       else "validator2 passed"))

    return lambda value: if_then_validator_func(value)

def sumIsLarger(fields, val):
    """Validate that the sum of the fields is larger than val."""
    def sumIsLargerFunc(value):
        sum = 0
        for field in fields:
            sum += value[field] if type(value) is dict else getattr(value, field)

        return (True, None) if sum > val else (False, f"The sum of {fields} is not larger than {val}.")

    return lambda value: sumIsLargerFunc(value)


# generic validators

def matches(option):
    """Validate that value is equal to option."""
    return make_validator(
        lambda value: value == option,
        lambda value: f'{value} does not match {option}.'
    )

def notMatches(option):
    """Validate that value is not equal to option."""
    return make_validator(
        lambda value: value != option,
        lambda value: f'{value} should not match {option}.'
    )


def oneOf(options=[]):
    """Validate that value does not exist in the provided options array."""
    return make_validator(
        lambda value: value in options,
        lambda value: f'{value} should not be in {options}.'
    )


def notOneOf(options=[]):
    """Validate that value exists in the provided options array."""
    return make_validator(
        lambda value: value not in options,
        lambda value: f'{value} is in {options}.'
    )


def between(min, max):
    """Validate value, when casted to int, is greater than min and less than max."""
    return make_validator(
        lambda value: int(value) > min and int(value) < max,
        lambda value: f'{value} is not between {min} and {max}.'
    )


def hasLength(length, error_func=None):
    """Validate that value (string or array) has a length matching length param."""
    return make_validator(
        lambda value: len(value) == length,
        lambda value: error_func(value, length) if error_func else f'Value length {len(value)} does not match {length}.'
    )


def contains(substring):
    """Validate that string value contains the given substring param."""
    return make_validator(
        lambda value: value.find(substring) != -1,
        lambda value: f'{value} does not contain {substring}.'
    )


def startsWith(substring):
    """Validate that string value starts with the given substring param."""
    return make_validator(
        lambda value: value.startswith(substring),
        lambda value: f'{value} does not start with {substring}.'
    )


def isNumber():
    """Validate that value can be casted to a number."""
    return make_validator(
        lambda value: value.isnumeric(),
        lambda value: f'{value} is not a number.'
    )

def isBlank():
    """Validate that string value is blank."""
    return make_validator(
        lambda value: value.isspace(),
        lambda value: f'{value} is blank.'
    )

def notEmpty(start=0, end=None):
    """Validate that string value isn't only blanks."""
    return make_validator(
        lambda value: not str(value)[start:end if end else len(str(value))].isspace(),
        lambda value: f'{str(value)} contains blanks between positions {start} and {end if end else len(str(value))}.'
    )

def isEmpty(start=0, end=None):
    """Validate that string value is only blanks."""
    return make_validator(
        lambda value: value[start:end if end else len(value)].isspace(),
        lambda value: f'{value} is not blank between positions {start} and {end if end else len(value)}.'
    )


def notZero(number_of_zeros=1):
    """Validate that value is not zero."""
    return make_validator(
        lambda value: value != '0' * number_of_zeros,
        lambda value: f'{value} is zero.'
    )


def isLargerThan(LowerBound):
    """Validate that value is larger than the given value."""
    return make_validator(
        lambda value: float(value) > LowerBound if value is not None else False,
        lambda value: f'{value} is not larger than {LowerBound}.'
    )


def isSmallerThan(UpperBound):
    """Validate that value is smaller than the given value."""
    return make_validator(
        lambda value: value < UpperBound,
        lambda value: f'{value} is not smaller than {UpperBound}.'
    )

def isLargerThanOrEqualTo(LowerBound):
    """Validate that value is larger than the given value."""
    return make_validator(
        lambda value: value >= LowerBound,
        lambda value: f'{value} is not larger than {LowerBound}.'
    )

def isSmallerThanOrEqualTo(UpperBound):
    """Validate that value is smaller than the given value."""
    return make_validator(
        lambda value: value <= UpperBound,
        lambda value: f'{value} is not smaller than {UpperBound}.'
    )

def isInLimits(LowerBound, UpperBound):
    """Validate that value is in a range including the limits."""
    return make_validator(
        lambda value: value >= LowerBound and value <= UpperBound,
        lambda value: f'{value} is not larger and equal to {LowerBound} and smaller and equal to {UpperBound}.'
    )


# custom validators

def month_year_monthIsValid():
    """Validate that in a monthyear combination, the month is a valid month."""
    return make_validator(
        lambda value: int(str(value)[4:]) in range(1, 13),
        lambda value: f'{str(value)[4:]} is not a valid month.'
    )


def month_year_yearIsLargerThan(year):
    """Validate that in a monthyear combination, the year is larger than the given year."""
    return make_validator(
        lambda value: int(str(value)[:4]) > year,
        lambda value: f'{str(value)[:4]} year must be larger than {year}.'
    )


def validate_single_header_trailer(datafile):
    """Validate that a raw datafile has one trailer and one footer."""
    line_number = 0
    headers = 0
    trailers = 0
    is_valid = True
    error_message = None

    for rawline in datafile.file:
        line = rawline.decode()
        line_number += 1

        if line.startswith('HEADER'):
            headers += 1
        elif line.startswith('TRAILER'):
            trailers += 1

        if headers > 1:
            is_valid = False
            error_message = 'Multiple headers found.'
            break

        if trailers > 1:
            is_valid = False
            error_message = 'Multiple trailers found.'
            break

    if headers == 0:
        is_valid = False
        error_message = 'No headers found.'

    error = None
    if not is_valid:
        error = generate_parser_error(
            datafile=datafile,
            line_number=line_number,
            schema=None,
            error_category=ParserErrorCategoryChoices.PRE_CHECK,
            error_message=error_message,
            record=None,
            field=None
        )

    return is_valid, error


def validate_header_section_matches_submission(datafile, program_type, section):
    """Validate header section matches submission section."""
    section_names = {
        'TAN': {
            'A': DataFile.Section.ACTIVE_CASE_DATA,
            'C': DataFile.Section.CLOSED_CASE_DATA,
            'G': DataFile.Section.AGGREGATE_DATA,
            'S': DataFile.Section.STRATUM_DATA,
        },
        'SSP': {
            'A': DataFile.Section.SSP_ACTIVE_CASE_DATA,
            'C': DataFile.Section.SSP_CLOSED_CASE_DATA,
            'G': DataFile.Section.SSP_AGGREGATE_DATA,
            'S': DataFile.Section.SSP_STRATUM_DATA,
        },
    }

    is_valid = datafile.section == section_names.get(program_type, {}).get(section)

    error = None
    if not is_valid:
        error = generate_parser_error(
            datafile=datafile,
            line_number=1,
            schema=None,
            error_category=ParserErrorCategoryChoices.PRE_CHECK,
            error_message=f"Data does not match the expected layout for {datafile.section}.",
            record=None,
            field=None
        )

    return is_valid, error
