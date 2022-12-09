# TODO: how to write separate tests from `test_model_mapping.py`
# certify that file -> model works
# does the model have the same contents as we expect? we dont care about
# correctness

"""Test preparser functions and tanf_parser."""
import pytest
import logging
from pathlib import Path
from tdpservice.search_indexes.parsers import tanf_parser, preparser
from tdpservice.search_indexes import documents
from tdpservice.search_indexes.models import T1
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

"""pytest fixture that opens file pointer object to our test file data/ADS.E2J.FTP1.TS06 for use in test functions."""
@pytest.fixture
def test_file():
    """Open file pointer to test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/ADS.E2J.FTP1.TS06"
    yield open(test_filename, 'r')

@pytest.fixture
def bad_test_file():
    """Open file pointer to bad test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/bad_TANF_S1.txt"
    yield open(test_filename, 'r')

def test_get_record_type():
    """Test get_record_type function."""
    assert False

def test_preparser_header(test_file):
    """Test header preparser."""
    is_valid, validator = preparser.validate_header(test_file, 'TANF', 'Active Cases')

    logger.info("is_valid: %s", is_valid)
    logger.info("errors: %s", validator.errors)
    assert is_valid
    assert validator.errors == {}
    assert validator.document['state_fips'] == '06'

def test_preparser_trailer(test_file):
    """Test trailer preparser."""
    # is_valid, validator = preparser.validate_trailer(test_file)
    # assert is_valid
    # assert errors is {}
    # TODO: test some value(s) in trailer to assert it was actually parsed correctly
    assert False

def test_preparser_body(test_file):
    """Test body preparser."""
    # TODO:
    # check it can handle header/trailer
    # feed good/bad data_types, sections
    # ensure it calls the correct parser
    assert False

@pytest.mark.django_db
def test_parsing_tanf_t1_active(test_file):
    """Test tanf_parser.active_case_data."""
    # open file to specific line, send it to parser
    # maybe just give a test line instead of a whole file??
    # assign line to new var, pass to parse()
    t1_count_before = T1.objects.count()

    tanf_parser.parse(test_file, 'Active Cases')

    assert T1.objects.count() > t1_count_before

    # define expected values
    # we get back a parser log object
    # should we create a FK between parserlog and t1 model?
    # were t1 models created

@pytest.mark.django_db
def test_parsing_tanf_t1_bad(bad_test_file):
    """Test tanf_parser.active_case_data with bad data."""
    search = documents.T1DataSubmissionDocument.search().query()
    response_before = search.execute()
    tally_before = response_before.hits.total.value

    tanf_parser.parse(bad_test_file, 'Active Cases')

    response_after = search.execute()
    tally_after = response_after.hits.total.value
    assert tally_after == tally_before  # no models created
