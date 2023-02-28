"""Unit tests for category2.py."""

from tdpservice.search_indexes.models import T1
from tdpservice.search_indexes.parsers.validators import category2
from tdpservice.search_indexes.parsers.validators.category2 import validate_cat2, validate, create_document


def test_validate_cat2(mocker):
    """Test validate_cat2."""
    mocker.patch(
        'tdpservice.search_indexes.parsers.validators.category2.create_document',
        return_value=())
    mocker.patch(
        'tdpservice.search_indexes.parsers.validators.category2.validate',
        return_value=())

    spy_create_document = mocker.spy(category2, 'create_document')
    condition = {'in': [1, 2]}
    name = 'TEST'
    value = 'foo'
    model_obj = T1()
    validate_cat2(name, value, condition, model_obj)
    assert spy_create_document.call_count == 0

    condition = {'FOO': {'gt': 0}}
    name = 'FOO'
    value = 'bar'
    model_obj = T1()
    validate_cat2(name, value, condition, model_obj)
    assert spy_create_document.call_count == 1

def test_validate():
    """Test validate."""
    schema = {'FOO': {'gt': 0}}
    document = {'FOO': 0}

    errors = validate(schema, document)
    assert errors['FOO']['constraint'] == 0
    assert errors['FOO']['field'] == 'FOO'
    assert errors['FOO']['value'] == 0

def test_create_document():
    """Test create_document."""
    condition = {'ZIP_CODE': {'gt': 0}}
    model_obj = T1(ZIP_CODE=0)

    assert create_document(condition, model_obj) == {'ZIP_CODE': 0}
