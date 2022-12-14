# TODO: how to write separate tests from `test_model_mapping.py`
# certify that file -> model works
# does the model have the same contents as we expect? we dont care about
# correctness

"""Test preparser functions and tanf_parser."""
import pytest
from pathlib import Path
import cerberus

import tdpservice
from tdpservice.search_indexes.parsers import tanf_parser, preparser, util
from tdpservice.search_indexes import documents
from tdpservice.search_indexes.models import T1

from django.db.models import FileField
from django.core.files.storage import FileSystemStorage

from tdpservice.data_files.models import DataFile
from tdpservice.data_files.test import factories as datafile_factories

import logging
logger = logging.getLogger(__name__)

# TODO: ORM mock for true data file factories
# https://stackoverflow.com/questions/1533861/testing-django-models-with-filefield

@pytest.fixture
def test_file():
    """Open file pointer to test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/small_correct_file"
    yield open(test_filename, 'rb')

@pytest.fixture
def test_big_file():
    """Open file pointer to test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/ADS.E2J.FTP1.TS06"
    yield open(test_filename, 'rb')

@pytest.fixture
def bad_test_file():
    """Open file pointer to bad test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/bad_TANF_S2.txt"
    yield open(test_filename, 'rb')

@pytest.fixture
def big_bad_test_file():
    """Open file pointer to bad test file."""
    test_filepath = str(Path(__file__).parent.joinpath('data'))
    test_filename = test_filepath + "/bad_TANF_S1.txt"
    yield open(test_filename, 'rb')

@pytest.mark.django_db
def test_preparser_header(test_file, bad_test_file):
    """Test header preparser."""

    logger.info("test_file type: %s", type(test_file))
    is_valid, validator = preparser.validate_header(test_file, 'TANF', 'Active Case Data')

    logger.info("is_valid: %s", is_valid)
    logger.info("errors: %s", validator.errors)
    assert is_valid
    assert validator.errors == {}
    assert validator.document['state_fips'] == '06'

    # negative case
    not_valid, not_validator = preparser.validate_header(bad_test_file, 'TANF', 'Active Case Data')
    assert not_valid == False
    logger.debug("not_validator.errors: %s", not_validator.errors)
    assert not_validator.errors != {}

    # TODO: provide diff program type, section, etc.
    not_valid, not_validator = preparser.validate_header(test_file, 'TANF', 'Active Casexs')
    assert not_valid == False
    # relevant error message

    not_valid, not_validator = preparser.validate_header(test_file, 'GARBAGE', 'Active Case Data')
    assert not_valid == False
    # relevant error message

def test_preparser_trailer(test_file):
    """Test trailer preparser."""
    for line in test_file:
        if util.get_record_type(line) == 'TR':
            trailer_row = line
            break
    is_valid, validator = preparser.validate_trailer(trailer_row)
    assert is_valid
    assert validator.errors == {}

    logger.debug("validator: %s", validator)
    logger.debug("validator dir: %s", dir(validator))
    logger.debug("validator.document: %s", validator.document)
    assert validator.document['record_count'] == 1

@pytest.mark.django_db
def test_preparser_body(test_file, bad_test_file, mocker):
    """Test that preparse correctly calls lower parser functions...or doesn't."""
    '''
    mocker.patch('tdpservice.search_indexes.parsers.preparser', return_value=True)
    mocker.patch('tdpservice.search_indexes.parsers.preparser.validate_header', return_value=(True,cerberus.Validator({})))
    mocker.patch('tdpservice.search_indexes.parsers.preparser.tanf_parser.parse', return_value=None)
    mocker.patch('tdpservice.search_indexes.parsers.preparser.active_t1', return_value=None)
    '''

    # TODO:
    # check it can handle header/trailer
    #retVal = tdpservice.search_indexes.parsers.preparser.preparse(test_file, 'TANF', 'Active Case Data')
    # logger.error(dir(retVal))
    # tdpservice.search_indexes.parsers.test.test_data_parsing:test_data_parsing.py:128 
    #   ['assert_any_call', 'assert_called', 'assert_called_once', 'assert_called_once_with', 'assert_called_with', 
    #   'assert_has_calls', 'assert_not_called', 'attach_mock', 'call_args', 'call_args_list', 'call_count', 'called', 
    #   'configure_mock', 'method_calls', 'mock_add_spec', 'mock_calls', 'reset_mock', 'return_value', 'side_effect']

    '''
    tdpservice.search_indexes.parsers.preparser.preparse.assert_called()
    assert tdpservice.search_indexes.parsers.preparser.validate_header.called_once()
    assert tdpservice.search_indexes.parsers.preparser.tanf_parser.parse.called_once()
    tdpservice.search_indexes.parsers.preparser.tanf_parser.active_t1.assert_called()
    '''

    spy = mocker.spy(preparser, 'preparse')
    preparser.preparse(test_file, 'TANF', 'Active Case Data')
    logger.info("preparse call count: %s", spy.call_count)
    assert False
    
    # feed good/bad data_types, sections and get it to error-handle this
    #assert preparser.preparse(test_file, 'TANF', 'Garbage Cases') == False
    #assert preparser.preparse(test_file, 'SSP_MOE', 'Active Cases') == False
    #assert preparser.preparse(bad_test_file, 'TANF', 'Active Cases') == False
    # TODO: ensure it calls the correct parser
    # TODO: assert that function parse() has (not) been called
    # https://stackoverflow.com/questions/50165477/pytest-mock-assert-called-with-failed-for-class-function
    # find a specific t1 model for the small_correct_file and assert it has the correct values

@pytest.mark.django_db
def test_parsing_tanf_t1_active(test_file):
    """Test tanf_parser.active_t1."""
    t1_count_before = T1.objects.count()
    tanf_parser.parse(test_file)
    assert T1.objects.count() > t1_count_before

    # define expected values
    # we get back a parser log object
    # should we create a FK between parserlog and t1 model?
    # were t1 models created?

@pytest.mark.django_db
def test_parsing_tanf_t1_bad(bad_test_file, big_bad_test_file):
    """Test tanf_parser.active_case_data with bad data."""
    t1_count_before = T1.objects.count()
    logger.info("t1_count_before: %s", t1_count_before)

    tanf_parser.parse(bad_test_file)

    t1_count_after = T1.objects.count()
    logger.info("t1_count_after: %s", t1_count_after)
    assert t1_count_after == t1_count_before

    ##########

    t1_count_before = T1.objects.count()
    logger.info("t1_count_before: %s", t1_count_before)

    tanf_parser.parse(big_bad_test_file)

    t1_count_after = T1.objects.count()
    logger.info("t1_count_after: %s", t1_count_after)
    assert t1_count_after == t1_count_before


    


