from copy import deepcopy

from tdpservice.search_indexes.parsers.validators.validator import FatalEditWarningsValidator


def validate_cat3(name: str, value: str, condition: dict, model_obj) -> tuple:
    """Validate categoy 2 errors."""
    document = {name: value}
    validator = FatalEditWarningsValidator(condition)
    validator.allow_unknown = True

    condition_copy = deepcopy(condition)
    condition_copy.pop(name)

    secondary_field = list(condition_copy.keys())[0]
    secondary_value = getattr(model_obj, secondary_field)

    document[secondary_field] = secondary_value
    validator.validate(document)

    return create_cat3_error(name, value, validator, model_obj)


def create_cat3_error(name, value, validator, model_obj):
    """Create a category 3 error."""
    condition = validator.schema
    primary_condition = condition.pop(name)
    secondary_field = list(condition.keys())[0]
    secondary_value = getattr(model_obj, secondary_field)

    primary_compare_field = list(primary_condition.keys())[0]
    primary_compare_value = primary_condition[primary_compare_field]
    primary_comparison = validator.definitions[primary_compare_field]

    secondary_condition = condition[secondary_field]
    secondary_compare_field = list(secondary_condition.keys())[0]
    secondary_compare_value = secondary_condition[secondary_compare_field]
    secondary_comparison = validator.definitions[secondary_compare_field]
    message = f'{name} is {primary_comparison} {primary_compare_value}, so {secondary_field} should be {secondary_comparison} {secondary_compare_value}. {secondary_field} is {secondary_value}.'
    error = {'primary': {'field': name, 'value': value, 'comparison': primary_comparison, 'constraint': primary_compare_value}, 
            'secondary': {'field': secondary_field, 'value': secondary_value, 'comparison': secondary_comparison,  'constraint': secondary_compare_value}, 
            'message': message}

    if name in validator.errors.keys():
        return []
    if len(validator.errors) > 0:
        return error

    return []

def validate(schema, document, name, value, model_obj):
    """Validate the a document."""
    validator = FatalEditWarningsValidator(schema)
    validator.allow_unknown = True
    validator.validate(document)

    return create_cat3_error(name, value, validator, model_obj)

def t1_116(model_obj):
    """Validate reason for & amount of assistance reductions."""
    schema = {
        'SANC_REDUCTION_AMT': {'gt': 0},
        'WORK_REQ_SANCTION': {'in': [1, 2]},
        'FAMILY_SANC_ADULT': {'in': [1, 2]},
        'SANC_TEEN_PARENT': {'in': [1, 2]},
        'NON_COOPERATION_CSE': {'in': [1, 2]},
        'FAILURE_TO_COMPLY': {'in': [1, 2]},
        'OTHER_SANCTION': {'in': [1, 2]}
    }
    document = {}
    for key in schema.keys():
        document[key] = getattr(model_obj, key)

    name = 'SANC_REDUCTION_AMT'
    value = getattr(model_obj, name)
    return validate(schema, document, name, value, model_obj)
