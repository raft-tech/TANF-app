"""Catagory 3 validators."""
from copy import deepcopy

from tdpservice.search_indexes.parsers.validators.validator import FatalEditWarningsValidator


def validate_cat3(name: str, value: str, condition: dict, model_obj) -> list:
    """Validate categoy 2 errors."""
    document = {name: value}
    validator = FatalEditWarningsValidator(condition)
    validator.allow_unknown = True

    condition_copy = deepcopy(condition)
    condition_copy.pop(name)

    for field in condition_copy.keys():
        document[field] = getattr(model_obj, field)

    validator.validate(document)

    return create_cat3_error(name, value, validator, model_obj)


def create_cat3_error(primary_field: str, primary_value: str, validator, model_obj) -> list:
    """Generate a catagory 3 error object.

    Parameters
    ----------
    primary_field : str
        The name of the primary field that is to be checked.
    primary_value : str
       The value of the primary field, taken from the model object
    validator : Cerberus Validator
        This validator has already been run and contains errors
    model_obj : Django model
        A django model object

    Returns
    -------
    list
        Returns an empty list if the primary condition is not met, or if there are no errors.
        Returns a dictionary holding the field, comparison, and constraint infomation for the error.
    """
    # The primary field is the value that needs to be checked first.
    validator_schema = validator.schema
    primary_condition = validator_schema.pop(primary_field)

    primary_compare_field = list(primary_condition.keys())[0]
    primary_constraint = primary_condition[primary_compare_field]
    primary_comparison = validator.definitions[primary_compare_field]

    secondary_field = list(validator_schema.keys())[0]
    secondary_value = getattr(model_obj, secondary_field)

    secondary_condition = validator_schema[secondary_field]
    secondary_compare_field = list(secondary_condition.keys())[0]
    secondary_constraint = secondary_condition[secondary_compare_field]
    secondary_comparison = validator.definitions[secondary_compare_field]

    errors = []
    for secondary_field, secondary_condition in validator_schema.items():
        secondary_value = getattr(model_obj, secondary_field)
        secondary_compare_field = list(secondary_condition.keys())[0]
        secondary_constraint = secondary_condition[secondary_compare_field]
        secondary_comparison = validator.definitions[secondary_compare_field]

        if secondary_field in validator.errors.keys():
            error = generate_error_obj(primary_field, primary_comparison, primary_constraint, primary_value,
                                       secondary_field, secondary_comparison, secondary_constraint, secondary_value)
            errors.append(error)

    # If there is an error with the primary field validation then this validator does not apply
    if primary_field in validator.errors.keys():
        return []
    # Since the primary check is valid we can go ahead and reaturn the errors, if any exist
    return errors

def generate_error_obj(primary_field, primary_comparison, primary_constraint, primary_value,
                       secondary_field, secondary_comparison, secondary_constraint, secondary_value):
    """Generate a catagory 3 error object."""
    message = f'{primary_field} is {primary_comparison} {primary_constraint}, '
    message += f'so {secondary_field} should be {secondary_comparison} {secondary_constraint}. '
    message += f'{secondary_field} is {secondary_value}.'

    error = {'primary': {'field': primary_field, 'value': primary_value,
                         'comparison': primary_comparison,
                         'constraint': primary_constraint},
             'secondary': {'field': secondary_field,
                           'value': secondary_value,
                           'comparison': secondary_comparison,
                           'constraint': secondary_constraint},
             'message': message}

    return error
