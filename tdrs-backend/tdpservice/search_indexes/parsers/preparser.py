"""Converts data files into a model that can be indexed by Elasticsearch."""


import argparse
from tdpservice.data_files.models import DataFile

def validate_header(datafile):
    """Validate the header line of the datafile."""
    return True

def validate_trailer(datafile):
    """Validate the trailer line of the datafile."""
    return True


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


    
    




