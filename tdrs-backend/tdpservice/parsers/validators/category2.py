"""Overloaded base validators and custom validators for category 2 validation (field validation)."""

from tdpservice.parsers.util import clean_options_string
from . import base
from .util import ValidationErrorArgs, validator, make_validator


def format_error_context(eargs: ValidationErrorArgs):
    """Format the error message for consistency across cat2 validators."""
    return f'{eargs.row_schema.record_type} Item {eargs.item_num} ({eargs.friendly_name}):'


@validator(1, base.isEqual)
def isEqual(option, **kwargs):
    """Return a custom message for the isEqual validator."""
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not match {option}."


@validator(1, base.isNotEqual)
def isNotEqual(option, **kwargs):
    """Return a custom message for the isNotEqual validator."""
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} matches {option}."


@validator(1, base.isOneOf)
def isOneOf(options, **kwargs):
    """Return a custom message for the isOneOf validator."""
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not in {clean_options_string(options)}."


@validator(1, base.isNotOneOf)
def isNotOneOf(options, **kwargs):
    """Return a custom message for the isNotOneOf validator."""
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} is in {clean_options_string(options)}."


@validator(1, base.isGreaterThan)
def isGreaterThan(option, inclusive=False, **kwargs):
    """Return a custom message for the isGreaterThan validator."""
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not larger than {option}."


@validator(1, base.isLessThan)
def isLessThan(option, inclusive=False, **kwargs):
    """Return a custom message for the isLessThan validator."""
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not smaller than {option}."


@validator(1, base.isBetween)
def isBetween(min, max, inclusive=False, **kwargs):
    """Return a custom message for the isBetween validator."""
    def inclusive_err(eargs):
        return f"{format_error_context(eargs)} {eargs.value} is not in range [{min}, {max}]."

    def exclusive_err(eargs):
        return f"{format_error_context(eargs)} {eargs.value} is not between {min} and {max}."

    return inclusive_err if inclusive else exclusive_err


@validator(1, base.startsWith)
def startsWith(substr, **kwargs):
    """Return a custom message for the startsWith validator."""
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not start with {substr}."


@validator(1, base.contains)
def contains(substr, **kwargs):
    """Return a custom message for the contains validator."""
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not contain {substr}."


@validator(1, base.isNumber)
def isNumber(**kwargs):
    """Return a custom message for the isNumber validator."""
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not a number."


@validator(1, base.isAlphaNumeric)
def isAlphaNumeric(**kwargs):
    """Return a custom message for the isAlphaNumeric validator."""
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not alphanumeric."


@validator(1, base.isEmpty)
def isEmpty(start=0, end=None, **kwargs):
    """Return a custom message for the isEmpty validator."""
    return lambda eargs: (
        f'{format_error_context(eargs)} {eargs.value} is not blank '
        f'between positions {start} and {end if end else len(eargs.value)}.'
    )


@validator(1, base.isNotEmpty)
def isNotEmpty(start=0, end=None, **kwargs):
    """Return a custom message for the isNotEmpty validator."""
    return lambda eargs: (
        f'{format_error_context(eargs)} {str(eargs.value)} contains blanks '
        f'between positions {start} and {end if end else len(str(eargs.value))}.'
    )


@validator(1, base.isBlank)
def isBlank(**kwargs):
    """Return a custom message for the isBlank validator."""
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not blank."


@validator(1, base.hasLength)
def hasLength(length, **kwargs):
    """Return a custom message for the hasLength validator."""
    return lambda eargs: (
        f"{format_error_context(eargs)} field length "
        f"is {len(eargs.value)} characters but must be {length}."
    )


@validator(1, base.hasLengthGreaterThan)
def hasLengthGreaterThan(length, inclusive=False, **kwargs):
    """Return a custom message for the hasLengthGreaterThan validator."""
    return lambda eargs: (
        f"{format_error_context(eargs)} Value length {len(eargs.value)} is not greater than {length}."
    )


@validator(1, base.intHasLength)
def intHasLength(length, **kwargs):
    """Return a custom message for the intHasLength validator."""
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} does not have exactly {length} digits."


@validator(1, base.isNotZero)
def isNotZero(number_of_zeros=1, **kwargs):
    """Return a custom message for the isNotZero validator."""
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} is zero."


# custom validators, written using the previous validator functions
def dateYearIsLargerThan(year, **kwargs):
    """Validate that in a monthyear combination, the year is larger than the given year."""
    _validator = base.dateYearIsLargerThan(year, **kwargs)
    return make_validator(
        lambda value: _validator(int(str(value)[:4])),
        lambda eargs: f"{format_error_context(eargs)} Year {str(eargs.value)[:4]} must be larger than {year}.", 1
    )


def dateMonthIsValid(**kwargs):
    """Validate that in a monthyear combination, the month is a valid month."""
    _validator = base.dateMonthIsValid(**kwargs)
    return make_validator(
        lambda val: _validator(int(str(val)[4:6])),
        lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[4:6]} is not a valid month.", 1
    )


def dateDayIsValid(**kwargs):
    """Validate that in a monthyearday combination, the day is a valid day."""
    _validator = base.dateDayIsValid(**kwargs)
    return make_validator(
        lambda value: _validator(int(str(value)[6:])),
        lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[6:]} is not a valid day.", 1
    )


def quarterIsValid(**kwargs):
    """Validate in a year quarter combination, the quarter is valid."""
    _validator = base.quarterIsValid(**kwargs)
    return make_validator(
        lambda value: _validator(int(str(value)[-1])),
        lambda eargs: f"{format_error_context(eargs)} {str(eargs.value)[-1]} is not a valid quarter.", 1
    )


def validateRace():
    """Validate race."""
    return make_validator(
        base.isBetween(0, 2, inclusive=True),
        lambda eargs:
            f"{format_error_context(eargs)} {eargs.value} is not in range [0, 2].", 1
    )


def validateHeaderUpdateIndicator():
    """Validate the header update indicator."""
    return make_validator(
        base.isEqual('D'),
        lambda eargs:
            f"HEADER Update Indicator must be set to D instead of {eargs.value}. "
            "Please review Exporting Complete Data Using FTANF in the Knowledge Center.", 1
    )
