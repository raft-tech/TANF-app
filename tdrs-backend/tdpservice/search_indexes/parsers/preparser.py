"""Converts data files into a model that can be indexed by Elasticsearch."""

import re
import logging
import argparse
from cerberus import Validator
from tdpservice.data_files.models import DataFile

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def get_record_type(row):
    """Get the record type from the row."""
    
    if re.match(r'^HEADER.*', row):
        logger.debug('Matched following row as a header: %s' % row)
        return 'HE'
    elif re.match(r'^TRAILER.*', row):
        logger.debug('Matched following row as a trailer: %s' % row)
        return 'TR'
    elif re.match(r'^T1.*', row):
        logger.debug('Matched following row as data: %s' % row)
        #if len(row) != 156:
        #    raise ValueError('T1 row length is not expected length of 156 characters.')
        return 'T1'
    elif re.match(r'^T2.*', row):
        logger.debug('Matched following row as data: %s' % row)
        return 'T2'
    elif re.match(r'^T3.*', row):
        logger.debug('Matched following row as data: %s' % row)
        return 'T3'
    elif re.match(r'^T4.*', row):
        logger.debug('Matched following row as data: %s' % row)
        return 'T4'
    elif re.match(r'^T5.*', row):
        logger.debug('Matched following row as data: %s' % row)
        return 'T5'
    elif re.match(r'^T6.*', row):
        logger.debug('Matched following row as data: %s' % row)
        return 'T6'
    elif re.match(r'^T7.*', row):
        logger.debug('Matched following row as data: %s' % row)
        return 'T7'
    else:
        logger.debug('No match for row: %s' % row)
        return None
        
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
        'A': 'Active Cases',
        'C': 'Closed Cases',
        'G': 'Aggregate',
        'S': 'Stratum',
    }

    # Validate the header row
    with open(datafile, 'r') as f:
        row = f.readline()

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

            # TODO: Will need to be saved in parserLog
            if given_section != section_map[header['type']]:
                raise ValueError('Given section does not match header section.') 

            # TODO: could import schema from a schemas folder/file, would be reusable for other sections
            
            header_schema = {
                'title':        {'type': 'string', 'required': True, 'allowed': ['HEADER']},
                'year':         {'type': 'integer', 'required': True, 'min': 2016}, # '^[0-9]{4}$'},
                'quarter':      {'type': 'integer', 'required': True, 'min': 1, 'max': 4},
                'type':         {'type': 'string', 'required': True, 'allowed': ['A', 'C', 'G', 'S']},
                'state_fips':   {'type': 'string', 'required': True, 'regex': '^[0-9]{2}$'},
                'tribe_code':   {'type': 'string', 'required': False, 'allow_unknown': True, 'regex': '^([0-9]{3}|[ ]{3})$'}, 
                'program_type': {'type': 'string', 'required': True, 'allowed': ['TAN', 'SSP']},
                'edit':         {'type': 'string', 'required': True, 'allowed': ['1', '2']},
                'encryption':   {'type': 'string', 'required': True, 'allowed': ['E', ' ']},
                'update':       {'type': 'string', 'required': True, 'allowed': ['N', 'D', 'U']},
            }

            validator = Validator(header_schema)
            is_valid = validator.validate(header)

            return is_valid, validator

        except Exception as e:
            logger.error('Exception validating header row, please see error.')
            logger.error(e)
            return False, e
        # should we close f?

def validate_trailer(row):
    """Validate the trailer row."""
    """
    https://www.acf.hhs.gov/sites/default/files/documents/ofa/transmission_file_header_trailer_record.pdf
    length of 24
    DESCRIPTION LENGTH FROM TO COMMENT
    Title 7 1 7 Value = TRAILER
    Number of Records 7 8 14 Right Adjusted
    Blank 9 15 23 Value = spaces
    Example:
    'TRAILER0000001         '
    """
    
    logger.info('Validating trailer row.')
    # Validate the trailer row
    is_valid = True # TODO: Implement validation logic with regex probably
    errors = {}
    return is_valid, errors


def preparse(datafile, data_type, section):
    """Validates metadata then dispatches file to appropriate parser."""

    # check file type and extension #TODO: this should be done by the frontend but let's verify here

    # validate header and trailer lines
    header_is_valid, header_errors = validate_header(datafile, data_type, section)
    trailer_is_valid, trailer_errors = validate_trailer(datafile, data_type, section)

    if header_is_valid and trailer_is_valid:
        logger.info("Preparsing succeeded.")
    else:
        logger.error("Preparse failed: %s", errors)
        return ParserLog.objects.create(
            data_file=args.file,
            errors=header_errors.extend(trailer_errors),
            status=ParserLog.Status.REJECTED,
        )

    # validate datatype and section


    # given dict of data_type to parser function, call the correct one with arguments
    if data_type == 'TANF':
        tanf_parser.parse(datafile, section)
    #elif data_type == 'SSP':
    #    ssp_parser.switch(datafile, section)
    #elif data_type == 'Tribal TANF':
    #    tribal_tanf_parser.switch(datafile, section)
    else:
        raise Exception("Invalid data type.")
        



if __name__ == '__main__':
    """Take in command-line arguments and run the parser."""

    parser = argparse.ArgumentParser(description='Parse TANF active cases data.')
    parser.add_argument('--file', type=argparse.FileType('r'), help='The file to parse.') # Does this give me a file object?
    parser.add_argument('--data_type', type=str, default='TANF', help='The type of data to parse.')
    parser.add_argument('--section', type=str, default='Active Case Data', help='The section of data to parse.')

    args = parser.parse_args()
    logger.debug("Arguments: %s", args)
    preparse(args.file, data_type="TANF", section="Active Case Data")


    
    




