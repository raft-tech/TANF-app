"""Category 3 unit tests."""
from tdpservice.search_indexes.models import T1
from tdpservice.search_indexes.parsers.validators import category3
from tdpservice.search_indexes.parsers.validators.category3 import generate_error_obj, validate_cat3, create_cat3_error

def test_generate_error_obj():
    """Test generate_error_obj."""
    primary_field = 'OTHER_AMOUNT'
    primary_comparison = 'greater than'
    primary_constraint = 0
    primary_value = 1
    secondary_field = 'OTHER_NBR_MONTHS'
    secondary_comparison = 'greater than'
    secondary_constraint = 0
    secondary_value = 0

    errors = generate_error_obj(primary_field, primary_comparison, primary_constraint, primary_value,
                                secondary_field, secondary_comparison, secondary_constraint, secondary_value)
    assert errors['primary']['field'] == primary_field
    assert errors['secondary']['field'] == secondary_field

def test_validate_cat3(mocker):
    """Test validate_cat3."""
    mocker.patch(
        'tdpservice.search_indexes.parsers.validators.category3.create_cat3_error',
        return_value=[])
    spy_create_cat3_error = mocker.spy(category3, 'create_cat3_error')

    condition = {'OTHER_AMOUNT': {'gt': 0}, 'OTHER_NBR_MONTHS': {'gt': 0}}
    name = 'OTHER_AMOUNT'
    value = 1
    model_obj = T1(OTHER_AMOUNT=1, OTHER_NBR_MONTHS=0)
    validate_cat3(name, value, condition, model_obj)
    assert spy_create_cat3_error.call_count == 1

def test_create_cat3_error():
    """Test create_cat3_error."""
    from tdpservice.search_indexes.parsers.validators.validator import FatalEditWarningsValidator

    condition = {'OTHER_AMOUNT': {'gt': 0}, 'OTHER_NBR_MONTHS': {'gt': 0}}
    model_obj = T1(OTHER_AMOUNT=1, OTHER_NBR_MONTHS=0)
    primary_field = 'OTHER_AMOUNT'
    primary_value = 1
    secondary_field = 'OTHER_NBR_MONTHS'
    secondary_value = 0
    validator = FatalEditWarningsValidator(condition)
    validator.validate({secondary_field: secondary_value})

    errors = create_cat3_error(primary_field, primary_value, validator, model_obj)
    assert len(errors) == 1
