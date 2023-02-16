"""Validate category 2 errors."""
from tdpservice.search_indexes.parsers.validators.validator import FatalEditWarningsValidator


def validate_cat2(name: str, value: str, condition: dict, model_obj) -> tuple:
    """Validate categoy 2 errors."""
    if name in condition.keys():
        schema = condition
    else:
        schema = {name: condition}
    document = {name: value}

    errors = validate(schema, document)
    return errors

def validate(schema, document):
    """Validate the a document."""
    validator = FatalEditWarningsValidator(schema)
    validator.allow_unknown = True
    validator.validate(document)

    return validator.errors

def t1_006(model_obj):
    """Validate model_obj.RPT_MONTH_YEAR for year."""
    # TODO discuss how we should address this edge case:
    # t1_006 and t1_007 are both validating parts of the same field,
    # Either we can pass though the specific name, "YEAR value from RPT_MONTH_YEAR",
    # or we can pass the actual field name, "RPT_MONTH_YEAR".
    # We could add custom logic to the validator to handle this case,
    # but that would be a lot of work for only two validators.
    # The logic would be similar to the logic in create_cat3_error where a custom error message is made.

    name = "YEAR value from RPT_MONTH_YEAR"
    value = int(str(model_obj.RPT_MONTH_YEAR)[0:4])

    schema = {name: {'gte': 1998}}
    document = {name: value}

    return validate(schema, document)

def t1_007(model_obj):
    """Validate model_obj.RPT_MONTH_YEAR for month."""
    name = "MONTH value from RPT_MONTH_YEAR"
    value = int(str(model_obj.RPT_MONTH_YEAR)[4:6])
    schema = {name: {'gte': 1, 'lte': 12}}
    document = {name: value}

    return validate(schema, document)
