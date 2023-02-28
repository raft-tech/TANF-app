"""Unit tests for custom Cerberus validator."""


from tdpservice.search_indexes.parsers.validators.validator import FatalEditWarningsValidator


def test_gt_validation():
    """Test _validate_gt."""
    v = FatalEditWarningsValidator()
    schema = {'amount': {'type': 'float', 'gt': 0}}
    assert v.validate({'amount': 10.0}, schema) is True
    assert v.validate({'amount': 0.0}, schema) is False

def test_lt_validation():
    """Test _validate_lt."""
    v = FatalEditWarningsValidator()
    schema = {'age': {'type': 'integer', 'lt': 18}}
    assert v.validate({'age': 10}, schema) is True
    assert v.validate({'age': 20}, schema) is False

def test_gte_validation():
    """Test _validate_gte."""
    v = FatalEditWarningsValidator()
    schema = {'amount': {'type': 'float', 'gte': 0}}
    assert v.validate({'amount': 10.0}, schema) is True
    assert v.validate({'amount': 0.0}, schema) is True
    assert v.validate({'amount': -10.0}, schema) is False

def test_lte_validation():
    """Test _validate_lte."""
    v = FatalEditWarningsValidator()
    schema = {'age': {'type': 'integer', 'lte': 18}}
    assert v.validate({'age': 10}, schema) is True
    assert v.validate({'age': 18}, schema) is True
    assert v.validate({'age': 20}, schema) is False

def test_in_validation():
    """Test _validate_in."""
    v = FatalEditWarningsValidator()
    schema = {'fruit': {'type': 'string', 'in': ['apple', 'orange', 'banana']}}
    assert v.validate({'fruit': 'apple'}, schema) is True
    assert v.validate({'fruit': 'banana'}, schema) is True
    assert v.validate({'fruit': 'grape'}, schema) is False
