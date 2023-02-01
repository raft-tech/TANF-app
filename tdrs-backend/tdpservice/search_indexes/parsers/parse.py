from tdpservice.data_files.models import DataFile
from schema import construct_header_schema, construct_trailer_schema

def parse(data_file_id, data_type):
    """Kick off parsing of a data file.
    
    Parameters:
        data_file_id: ID of the DataFile to parse.
        data_type: Type of data file to parse.
    """

    data_file = DataFile.objects.get(id=data_file_id)
    section = data_file.section
    file = data_file.file

    match data_type:
        case "TANF":
            pass
        case "SSP":
            pass

def get_header_line(datafile):
    """Alters header line into string."""
    # intentionally only reading first line of file
    datafile.seek(0)
    header = datafile.readline()
    datafile.seek(0)  # reset file pointer to beginning of file

    # datafile when passed via redis/db is a FileField which returns bytes
    if isinstance(header, bytes):
        header = header.decode()

    header = header.strip()

    if get_record_type(header) != 'HE':
        return False, {'preparsing': 'First line in file is not recognized as a valid header.'}
    elif len(header) != 23:
        logger.debug("line: '%s' len: %d", header, len(header))
        return False, {'preparsing': 'Header length incorrect.'}

    return True, header


def parse_header(header_data):
    header_schema = construct_header_schema()

    for row in header_schema:
        