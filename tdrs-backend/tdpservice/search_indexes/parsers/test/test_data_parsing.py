# TODO: how to write separate tests from `test_model_mapping.py`
# certify that file -> model works
# does the model have the same contents as we expect? we dont care about 
# correctness

"""Test preparser functions and tanf_parser."""

import pytest
from pathlib import Path
from tdpservice.search_indexes.parsers import tanf_parser, preparser

"""pytest fixture that opens file pointer object to our test file data/ADS.E2J.FTP1.TS06 for use in test functions."""
@pytest.fixture
def test_file():
    """Open file pointer to test file."""
    test_filepath = str(Path(__file__).parent.joinpath('.')) # ADS.E2J.FTP1.TS06'))
    test_filename = test_filepath + "/ADS.E2J.FTP1.TS06"
    yield test_filename
    
    #with open(test_filename,'r') as f:
    #    yield f

def test_get_record_type():
    """Test get_record_type function."""
    assert False

def test_preparser_header(test_file):
    """Test header preparser."""

    is_valid, errors = preparser.validate_header(test_file, 'TANF', 'Active Cases')
    print(errors)
    assert is_valid
    assert errors == {}
    # TODO: test some value(s) in header to assert it was actually parsed correctly
    print("finish")
    #assert False

def test_preparser_trailer(test_file):
    """Test trailer preparser."""
    #is_valid, errors = preparser.validate_trailer(test_file)
    #assert is_valid
    #assert errors is {}
    # TODO: test some value(s) in trailer to assert it was actually parsed correctly
    assert False

def test_preparser_body():
    """Test body preparser."""
    assert False



'''
logic -> same computerish msg
coders -> backend msg
backend msg -> user-facing
'''