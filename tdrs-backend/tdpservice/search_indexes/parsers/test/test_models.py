"""Module testing for data file model."""
import pytest

from tdpservice.search_indexes.parsers.models import ParserError
from tdpservice.search_indexes.parsers.test.factories import ParserErrorFactory

@pytest.fixture
def parser_error_instance():
    """Create a parser error instance."""
    return ParserErrorFactory.create()


@pytest.mark.django_db
def test_parser_error_instance(parser_error_instance):
    """Test that the parser error instance is created."""
    assert isinstance(parser_error_instance, ParserError)
