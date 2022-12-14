# TODO: how to write separate tests from `test_model_mapping.py`
# certify that file -> model works
# does the model have the same contents as we expect? we dont care about
# correctness

"""Test preparser functions and tanf_parser."""
import pytest
from functools import reduce
from pathlib import Path

from tdpservice.search_indexes.parsers import tanf_parser, preparser, util
from tdpservice.search_indexes.models import T1

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
    test_row = test_file.readline().decode()
    is_valid, validator = preparser.validate_header(test_row, 'TANF', 'Active Case Data')

    logger.info("is_valid: %s", is_valid)
    logger.info("errors: %s", validator.errors)
    assert is_valid is False
    assert validator.errors == {}
    assert validator.document['state_fips'] == '06'

    # negative case
    bad_row = bad_test_file.readline().decode()
    not_valid, not_validator = preparser.validate_header(bad_row, 'TANF', 'Active Case Data')
    assert not_valid is False
    logger.debug("not_validator.errors: %s", not_validator.errors)
    assert not_validator.errors != {}

    # Inserting a bad section type
    with pytest.raises(ValueError) as e_info:
        preparser.validate_header(test_row, 'TANF', 'Active Casexs')
    assert str(e_info.value) == "Given section does not match header section."

    # Inserting a bad program type
    with pytest.raises(ValueError) as e_info:
        preparser.validate_header(test_row, 'GARBAGE', 'Active Case Data')
    assert str(e_info.value) == "Given data type does not match header program type."


def test_preparser_trailer(test_file):
    """Test trailer preparser."""
    for line in test_file:
        line = line.decode()
        if util.get_record_type(line) == 'TR':
            trailer_row = line
            break
    is_valid, validator = preparser.validate_trailer(trailer_row)
    assert is_valid
    assert validator.errors == {}

    logger.debug("validator: %s", validator)
    logger.debug("validator.document: %s", validator.document)
    assert validator.document['record_count'] == '0000001'

def spy_count_check(spies, expected_counts):
    """Run reduce against two lists, returning True if all functions were called the expected number of times."""
    return reduce(
        lambda bool_retVal, tuple:  bool_retVal and (
            lambda spy_count, expected: spy_count == expected
            ),
        zip(spies, expected_counts),
        True)

@pytest.mark.django_db
def test_preparser_body(test_file, mocker):
    """Test that preparse correctly calls lower parser functions...or doesn't."""
    spy_preparse = mocker.spy(preparser, 'preparse')
    spy_head = mocker.spy(preparser, 'validate_header')
    spy_tail = mocker.spy(preparser, 'validate_trailer')
    spy_parse = mocker.spy(tanf_parser, 'parse')
    spy_t1 = mocker.spy(tanf_parser, 'active_t1')

    spies = [spy_preparse, spy_head, spy_tail, spy_parse, spy_t1]
    assert preparser.preparse(test_file, 'TANF', 'Active Case Data')

    assert spy_count_check(spies, [1, 1, 1, 1, 1])

@pytest.mark.django_db
def test_preparser_big_file(test_big_file, mocker):
    """Test the preparse correctly handles a large, correct file."""
    spy_preparse = mocker.spy(preparser, 'preparse')
    spy_head = mocker.spy(preparser, 'validate_header')
    spy_tail = mocker.spy(preparser, 'validate_trailer')
    spy_parse = mocker.spy(tanf_parser, 'parse')
    spy_t1 = mocker.spy(tanf_parser, 'active_t1')

    spies = [spy_preparse, spy_head, spy_tail, spy_parse, spy_t1]
    assert preparser.preparse(test_big_file, 'TANF', 'Active Case Data')

    assert spy_count_check(spies, [1, 1, 1, 1, 815])

@pytest.mark.django_db
def test_preparser_bad_file(bad_test_file, mocker):
    """Test that preparse correctly catches issues in a bad file."""
    spy_preparse = mocker.spy(preparser, 'preparse')
    spy_head = mocker.spy(preparser, 'validate_header')
    spy_tail = mocker.spy(preparser, 'validate_trailer')
    spy_parse = mocker.spy(tanf_parser, 'parse')
    spy_t1 = mocker.spy(tanf_parser, 'active_t1')

    spies = [spy_preparse, spy_head, spy_tail, spy_parse, spy_t1]
    is_valid, preparser_errors = preparser.preparse(bad_test_file, 'TANF', 'Active Case Data')
    assert not is_valid
    assert preparser_errors != {}

    assert spy_count_check(spies, [1, 1, 0, 0, 0])

@pytest.mark.django_db
def test_preparser_bad_params(test_file, mocker):
    """Test that preparse correctly catches bad parameters."""
    spy_preparse = mocker.spy(preparser, 'preparse')
    spy_head = mocker.spy(preparser, 'validate_header')
    spy_tail = mocker.spy(preparser, 'validate_trailer')
    spy_parse = mocker.spy(tanf_parser, 'parse')
    spy_t1 = mocker.spy(tanf_parser, 'active_t1')

    spies = [spy_preparse, spy_head, spy_tail, spy_parse, spy_t1]

    # feed good/bad data_types, sections and get it to error-handle this
    with pytest.raises(ValueError) as e_info:
        preparser.preparse(test_file, 'TANF', 'Garbage Cases')
    assert str(e_info.value) == 'Given section does not match header section.'
    logger.debug("test_preparser_bad_params::garbage section value:")
    for spy in spies:
        logger.debug("Spy: %s\tCount: %s", spy, spy.call_count)
    assert spy_count_check(spies, [1, 0, 0, 0, 0])

    with pytest.raises(ValueError) as e_info:
        preparser.preparse(test_file, 'GARBAGE', 'Active Case Data')
    assert str(e_info.value) == "Given data type does not match header program type."
    logger.debug("test_preparser_bad_params::wrong program_type value:")
    for spy in spies:
        logger.debug("Spy: %s\tCount: %s", spy, spy.call_count)
    assert spy_count_check(spies, [2, 2, 1, 0, 0])

    with pytest.raises(ValueError) as e_info:
        preparser.preparse(test_file, 1234, 'Active Case Data')
    assert str(e_info.value) == 'Given data type does not match header program type.'
    logger.debug("test_preparser_bad_params::wrong program_type type:")
    for spy in spies:
        logger.debug("Spy: %s\tCount: %s", spy, spy.call_count)
    assert spy_count_check(spies, [3, 3, 2, 0, 0])

@pytest.mark.django_db
def test_parsing_tanf_t1_active(test_file):
    """Test tanf_parser.active_t1."""
    t1_count_before = T1.objects.count()
    assert t1_count_before == 0
    tanf_parser.parse(test_file)
    assert T1.objects.count() == t1_count_before + 1

    # define expected values
    # we get back a parser log object for 1354
    # should we create a FK between parserlog and t1 model?

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
