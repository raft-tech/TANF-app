"""Category 3 validators."""
from tdpservice.search_indexes.parsers.validators.validator import FatalEditWarningsValidator


def generate_error_obj(primary_field, primary_comparison, primary_constraint, primary_value,
                       secondary_field, secondary_comparison, secondary_constraint, secondary_value):
    """Generate a category 3 error object."""
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

def validate_cat3(name: str, value: str, condition: dict, model_obj) -> list:
    """Validate category 3 errors."""
    document = {}
    validator = FatalEditWarningsValidator(condition)
    validator.allow_unknown = True

    for field in condition.keys():
        document[field] = getattr(model_obj, field)

    validator.validate(document)

    return create_cat3_error(name, value, validator, model_obj)

def create_cat3_error(primary_field: str, primary_value: str, validator, model_obj) -> list:
    """Generate a category 3 error object.

    Cat3 has primary and secondary checks e.g. if X is greater than 0, Y should be greater than 0.
    All these fields have been validated at the same time, but depending on the success of the
    primary validation check the secondary checks might not matter. e.g. If the primary check fails
    then no error should be returned.

    This function collects the fields and values for primary and secondary checks.
    If the primary check was successful the error message will be generated and added to the return list.


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
    validator_schema = validator.schema

    # Collect all the data the error object needs for the primary field.
    # The validator schema holds both primary and secondary dictionaries
    # We know which one is the primary field because the primary field is a parameter.
    # The primary field is popped off the validator schema so that only secondary fields remain.
    primary_condition = validator_schema.pop(primary_field)
    primary_compare_field = list(primary_condition.keys())[0]
    primary_constraint = primary_condition[primary_compare_field]
    primary_comparison = validator.definitions[primary_compare_field]

    errors = []
    # Collect all the data the error object needs for the secondary field
    # There can be multiple secondary fields so this is done in a loop.
    for secondary_field, secondary_condition in validator_schema.items():
        secondary_value = getattr(model_obj, secondary_field)
        secondary_compare_field = list(secondary_condition.keys())[0]
        secondary_constraint = secondary_condition[secondary_compare_field]
        secondary_comparison = validator.definitions[secondary_compare_field]

        # If the secondary field is in the validator errors then we know it failed and
        # requires an error object to be made and added to the errors list.
        if secondary_field in validator.errors.keys():
            error = generate_error_obj(primary_field, primary_comparison, primary_constraint, primary_value,
                                       secondary_field, secondary_comparison, secondary_constraint, secondary_value)
            errors.append(error)

    # If there is an error with the primary field validation then this validator does not apply and
    # nothing should be returned.
    if primary_field in validator.errors.keys():
        return []
    # Since the primary check is valid we can go ahead and reaturn the errors, if any exist
    return errors
