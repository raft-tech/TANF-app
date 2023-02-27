"""Module testing for data file model."""
import pytest

from tdpservice.stts.models import STT

from tdpservice.search_indexes.parsers.models import ParserError
from tdpservice.search_indexes.parsers.test.factories import ParserErrorFactory

@pytest.fixture
def parser_error_instance():
    return ParserErrorFactory.create()


@pytest.mark.django_db
def test_parser_error_instance(parser_error_instance):
    assert isinstance(parser_error_instance, ParserError)
