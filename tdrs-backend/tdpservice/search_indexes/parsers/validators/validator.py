"""Validator for TANF and SSP fatal edit warnings."""
from cerberus import Validator, errors

class FatalEditWarningsValidator(Validator):
    """Validator for TANF and SSP fatal edit warnings."""

    definitions = {
        'gt': 'greater than',
        'lt': 'less than',
        'gte': 'greater than or equal to',
        'lte': 'less than or equal to',
        'in': 'in',
    }

    def _validate_gt(self, constraint, field, value):
        """Validate that value is greater than a constraint."""
        if not value > constraint:
            message = f"{field} is not greater than {constraint}. {field} is {value}."
            self._construct_error_obj(field, constraint, message, value)

    def _validate_lt(self, constraint, field, value):
        """Validate that value is less than a constraint."""
        if not value < constraint:
            message = f"{field} is not less than {constraint}. {field} is {value}."
            self._construct_error_obj(field, constraint, message, value)

    def _validate_gte(self, constraint, field, value):
        """Validate that value is greater than or equal to a constraint."""
        if not value >= constraint:
            message = f"{field} is not greater than or equal to {constraint}. {field} is {value}."
            self._construct_error_obj(field, constraint, message, value)

    def _validate_lte(self, constraint, field, value):
        """Validate that value is less than or equal to a constraint."""
        if not value <= constraint:
            message = f"{field} is not less than or equal to {constraint}. {field} is {value}."
            self._construct_error_obj(field, constraint, message, value)

    def _validate_in(self, constraint, field, value):
        """Validate that value is in a list of constraints."""
        if value not in constraint:
            message = f"{field} is not in {constraint}. {field} is {value}."
            self._construct_error_obj(field, constraint, message, value)

    def _construct_error_obj(self, field, constraint, message, value):
        """Construct the error obj."""
        self._error(field, errors.CUSTOM, {'constraint': constraint,
                                           'message': message,
                                           'field': field,
                                           'value': value})
