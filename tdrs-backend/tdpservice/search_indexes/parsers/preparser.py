"""Converts data files into a model that can be indexed by Elasticsearch."""

import os
import logging
import argparse
from cerberus import Validator
from .util import get_record_type
from . import tanf_parser
from django.db.models import FileField
from io import BufferedReader
# from .models import ParserLog
from tdpservice.data_files.models import DataFile

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def validate_header(datafile, data_type, given_section):
    """Validate the header line of the datafile."""
    """
    https://www.acf.hhs.gov/sites/default/files/documents/ofa/transmission_file_header_trailer_record.pdf

    DESCRIPTION		LENGTH	FROM	TO	COMMENT
    Title		    6	1	6	Value	=	HEADER
    YYYYQ	        5	7	11	Value	=	YYYYQ

    Type 	        1	12	12	A=Active;	C=Closed;	G=Aggregate,	S=Stratum
    State Fips	    2	13	14	"2	digit	state	code	000	a	tribe"
    Tribe Code	    3	15	17	"3	digit	tribe	code	000	a	state"
    Program	Type	3	18	20	Value	=	TAN	(TANF)	or	Value	=	SSP	(SSP-MOE)
    Edit Indicator	1	21	21	1=Return	Fatal	&	Warning	Edits	2=Return	Fatal	Edits	only
    Encryption      1	22	22	E=SSN	is	encrypted	Blank	=	SSN	is	not	encrypted
    Update      	1	23	23	N	=	New	data	D	=	Delete	existing	data	U
    QUARTERS:
        Q=1	(Jan-Mar)
        Q=2	(Apr-Jun)
        Q=3	(Jul-Sep)
        Q=4	(Oct-Dec)
    Example:
    HEADERYYYYQTFIPSSP1EN
    """
    logger.debug('Validating header row.')


    section_map = {
        'A': 'Active Case Data',
        'C': 'Closed Case Data',
        'G': 'Aggregate Data',
        'S': 'Stratum Data',
    }

    # intentionally only reading first line of file
    row = datafile.readline()

    # datafile when passed via redis/db is a FileField which returns bytes
    if isinstance(row, bytes):
        logger.info("Row is bytes, decoding to string...")
        row = row.decode()

    logger.debug("Header: %s", row)
    if get_record_type(row) != 'HE':
        raise ValueError('First line in file not recognized as valid header.')

    try:
        header = {
            'title':        row[0:6],
            'year':         int(row[6:10]),
            'quarter':      int(row[10:11]),
            'type':         row[11:12],
            'state_fips':   row[12:14],
            'tribe_code':   row[14:17],
            'program_type': row[17:20],
            'edit':         row[20:21],
            'encryption':   row[21:22],
            'update':       row[22:23],
        }

        for key, value in header.items():
            logger.debug('Header key %s: "%s"' % (key, value))

        # TODO: Will need to be saved in parserLog, #1354
        
        try:
            logger.debug("Given section: '%s'\t Header section: '%s'", given_section, section_map[header['type']])
            logger.debug("Given program type: '%s'\t Header program type: '%s'", data_type, header['program_type'])

            if given_section != section_map[header['type']]:
                raise ValueError('Given section does not match header section.')
            elif data_type == 'TANF' and header['program_type'] != 'TAN':
                logger.debug('Given data type ("%s") does not match header program type ("%s")', data_type, header['program_type'])
                raise ValueError('Given data type ("%s") does not match header program type ("%s")', data_type, header['program_type'])
        except KeyError as e:
            logger.error('Ran into issue with header type: %s', e)

        # TODO: could import schema from a schemas folder/file, would be reusable for other sections

        header_schema = {
            'title':        {'type': 'string', 'required': True, 'allowed': ['HEADER']},
            'year':         {'type': 'integer', 'required': True, 'min': 2016},  # '^[0-9]{4}$'},
            'quarter':      {'type': 'integer', 'required': True, 'min': 1, 'max': 4},
            'type':         {'type': 'string', 'required': True, 'allowed': ['A', 'C', 'G', 'S']},
            'state_fips':   {'type': 'string', 'required': True, 'regex': '^[0-9]{2}$'},
            'tribe_code':   {'type': 'string', 'required': False, 'regex': '^([0-9]{3}|[ ]{3})$'},
            'program_type': {'type': 'string', 'required': True, 'allowed': ['TAN', 'SSP']},
            'edit':         {'type': 'string', 'required': True, 'allowed': ['1', '2']},
            'encryption':   {'type': 'string', 'required': True, 'allowed': ['E', ' ']},
            'update':       {'type': 'string', 'required': True, 'allowed': ['N', 'D', 'U']},
        }

        validator = Validator(header_schema)
        is_valid = validator.validate(header)
        logger.debug(validator.errors)

        return is_valid, validator

    except KeyError as e:
       logger.error('Exception validating header row, please see row and error.')
       logger.error(row)
       logger.error(e)
       return False, e
    except ValueError as f:
        logger.error("Found value mismatch in header row.")
        logger.error(f)
        return False, f

def validate_trailer(datafile):
    """Validate the trailer row."""
    """
    https://www.acf.hhs.gov/sites/default/files/documents/ofa/transmission_file_header_trailer_record.pdf
    length of 24
    DESCRIPTION LENGTH  FROM    TO  COMMENT
    Title       7       1       7   Value = TRAILER
    Record Count7       8       14  Right Adjusted
    Blank       9       15      23  Value = spaces
    Example:
    'TRAILER0000001         '
    """

    logger.info('Validating trailer row.')

    # certify/transform input row to be correct form/type
    
    logger.info("Type of datafile '%s'", type(datafile))
    row = None
    '''for row in datafile:
        if get_record_type(row) == 'TR':
            break
        else:
            continue
    '''

    # Don't want to read whole file, just last line, only possible with binary
    # Credit: https://openwritings.net/pg/python/python-read-last-line-file
    # https://stackoverflow.com/questions/46258499/
    try:
        datafile.seek(-2, os.SEEK_END) # Jump to the second last byte.
        while datafile.read(1) != b'\n': # Check if new line.
            datafile.seek(-2, os.SEEK_CUR)  # Jump two bytes back
    except OSError: # Either file is empty or contains one line.
        datafile.seek(0)
        raise ValueError('File too short or missing trailer.')
    
    # Having set the file pointer to the last line, read it.
    row = datafile.readline().decode()
    logger.info("Trailer row: '%s'", row)
    
    if get_record_type(row) != 'TR':
        raise ValueError('Last row is not a trailer row.')
    if len(row) != 24:
        raise ValueError("Trailer row is not 23 characters long.")
    row = row.strip('\n')

    trailer_schema = {
        'title':        {'type': 'string', 'required': True, 'allowed': ['TRAILER']},
        'record_count': {'type': 'integer', 'required': True, 'min': 1, 'max': 9999999},
        'blank':        {'type': 'string', 'required': True, 'regex': '^[ ]{9}$'},
    }

    validator = Validator(trailer_schema)

    trailer = {
        'title':        row[0:7],
        'record_count': int(row[7:14]),
        'blank':        row[14:23],
    }

    is_valid = validator.validate(trailer)

    logger.debug("Trailer title: '%s'", trailer['title'])
    logger.debug("Trailer record count: '%s'", trailer['record_count'])
    logger.debug("Trailer blank: '%s'", trailer['blank'])
    logger.debug("Trailer errors: '%s'", validator.errors)

    return is_valid, validator


def preparse(data_file, data_type, section):
    """Validate metadata then dispatches file to appropriate parser."""
    if isinstance(data_file, DataFile):
        datafile = data_file.file # do I need to open() this?
    elif isinstance(data_file, BufferedReader):
        datafile = data_file
    else:
        logger.error("Unexpected datafile type %s", type(data_file))
        raise TypeError("datafile type %s", type(data_file))

    # TODO: check file type and extension

    # validates header and trailer lines and the input data_type and section
    header_is_valid, header_validator = validate_header(datafile, data_type, section)
    trailer_is_valid, trailer_validator = validate_trailer(datafile)
    errors = header_validator  # + trailer_errors (how to combine Exception and dict? or logic around it)
    if header_is_valid and trailer_is_valid:
        logger.info("Preparsing succeeded.")
    else:
        logger.error("Preparse failed: %s", errors)
        return False
        # return ParserLog.objects.create(
        #    data_file=args.file,
        #    errors=errors,
        #    status=ParserLog.Status.REJECTED,
        # )

    if data_type == 'TANF':
        tanf_parser.parse(datafile)
    # elif data_type == 'SSP':
    #    ssp_parser.parse(datafile)
    # elif data_type == 'Tribal TANF':
    #    tribal_tanf_parser.parse(datafile)
    else:
        raise Exception("Invalid data type.")

    return True

if __name__ == '__main__':
    """Take in command-line arguments and run the parser."""
    parser = argparse.ArgumentParser(description='Parse TANF active cases data.')
    parser.add_argument('--file', type=argparse.FileType('r'), help='The file to parse.')
    parser.add_argument('--data_type', type=str, default='TANF', help='The type of data to parse.')
    parser.add_argument('--section', type=str, default='Active Case Data', help='The section submitted.')

    args = parser.parse_args()
    logger.debug("Arguments: %s", args)
    preparse(args.file, data_type="TANF", section="Active Case Data")
