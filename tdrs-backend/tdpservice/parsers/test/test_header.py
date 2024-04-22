"""Tests for the header parser module."""

from tdpservice.parsers import schema_defs
from tdpservice.parsers import util
from unittest.mock import patch
import pytest

import logging
logger = logging.getLogger(__name__)


@pytest.fixture
def test_datafile(stt_user, stt):
    """Fixture for small_correct_file."""
    return util.create_test_datafile('small_correct_file.txt', stt_user, stt)

@pytest.mark.django_db
def test_header_cleanup(test_datafile):
    """Test the header parser."""

    def _parse_header():
        header_line = f"HEADER{YEAR}{QUARTER}{TYPE}{STATE_FIPS}{TRIBE_CODE}{PROGRAM_CODE}{EDIT_CODE}{ENCRYPTION_CODE}{UPDATE_INDICATOR}"
        return schema_defs.header.parse_and_validate(header_line, util.make_generate_file_precheck_parser_error(test_datafile, 1))

    YEAR = '2020'
    QUARTER = '4'
    TYPE = 'A'
    STATE_FIPS = '06'
    TRIBE_CODE = '000'
    PROGRAM_CODE = 'TAN'
    EDIT_CODE = '1'
    ENCRYPTION_CODE = ' '
    UPDATE_INDICATOR = 'D'
    header_line = f"HEADER{YEAR}{QUARTER}{TYPE}{STATE_FIPS}{TRIBE_CODE}{PROGRAM_CODE}{EDIT_CODE}{ENCRYPTION_CODE}{UPDATE_INDICATOR}"
    header, header_is_valid, header_errors = schema_defs.header.parse_and_validate(header_line, util.make_generate_file_precheck_parser_error(test_datafile, 1))
    assert header_is_valid

    logger.info('________________header: %s', header)
    logger.info('________________header_is_valid: %s', header_is_valid)
    logger.info('________________header_errors: %s', header_errors)

    STATE_FIPS = '  '
    header_line = f"HEADER{YEAR}{QUARTER}{TYPE}{STATE_FIPS}{TRIBE_CODE}{PROGRAM_CODE}{EDIT_CODE}{ENCRYPTION_CODE}{UPDATE_INDICATOR}"
    header, header_is_valid, header_errors = schema_defs.header.parse_and_validate(header_line, util.make_generate_file_precheck_parser_error(test_datafile, 1))
    assert header_is_valid


    logger.info('________________header: %s', header)
    logger.info('________________header_is_valid: %s', header_is_valid)
    logger.info('________________header_errors: %s', header_errors)

