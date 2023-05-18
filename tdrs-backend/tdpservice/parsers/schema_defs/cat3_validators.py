from .. import validators

def validate_disposition(record):
    value = getattr(record, "DISPOSITION")
    print(f'\n\nDISPOSITION VALUE: {value}\n\n')
    if value == 2:
        items = ["COUNTY_FIPS_CODE", "RPT_MONTH_YEAR", "STRATUM", "CASE_NUMBER"]
        validator = validators.notEmpty()
        for item in items:
            item_value = getattr(record, item)
            validator_is_valid, validator_error = validator(str(item_value))
            print(f'\n\nITEM VALUE: {item_value}, IS_VALID: {validator_is_valid}, ERROR: {validator_error}\n\n')
            if not validator_is_valid:
                return (False, validator_error)
    return (True, None)



t1_validators = {
    "DISPOSITION": [validate_disposition],
}

def cat3_validate_t1(record, fields):
    validator_errors = []
    for field in fields:
        validators = t1_validators.get(field.name, [])
        for validator in validators:
            validator_is_valid, validator_error = validator(record)
            if not validator_is_valid:
                validator_errors.append(validator_error)

    if len(validator_errors):
        return (False, validator_errors)

    return (True, None)

