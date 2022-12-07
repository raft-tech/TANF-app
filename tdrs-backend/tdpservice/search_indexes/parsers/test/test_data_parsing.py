# TODO: how to write separate tests from `test_model_mapping.py`
# certify that file -> model works
# does the model have the same contents as we expect? we dont care about
# correctness

"""Test preparser functions and tanf_parser."""
import pytest
import logging
from pathlib import Path
from tdpservice.search_indexes.parsers import tanf_parser, preparser

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

"""pytest fixture that opens file pointer object to our test file data/ADS.E2J.FTP1.TS06 for use in test functions."""
@pytest.fixture
def test_file():
    """Open file pointer to test file."""
    test_filepath = str(Path(__file__).parent.joinpath('.'))
    test_filename = test_filepath + "/ADS.E2J.FTP1.TS06"
    yield test_filename

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

def test_preparser_body():
    """Test body preparser."""
    assert False
