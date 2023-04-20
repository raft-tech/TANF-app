"""Transforms a TANF datafile into an search_index model."""

import logging
from tdpservice.search_indexes.models import T1, T2, T3  # , T4, T5, T6, T7, ParserLog
# from django.core.exceptions import ValidationError
from .util import get_record_type
from .schema_defs.tanf import t1_schema, t2_schema, t3_schema

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def active_parse(actual_line_length, min_line_length, schema, line, line_number, model):
    """Parse line in datafile as active case data."""
    content_is_valid = True

    if actual_line_length < min_line_length:
        logger.error('Expected minimum line length of %s, got: %s', min_line_length, actual_line_length)
        return

    for field in schema.get_all_fields():
        content = line[field.start-1:field.end]  # descriptor pdfs were off by one, could also adjust start values

        # check if content is type string or integer
        if field.type == 'Numeric':
            try:
                content = int(content)
            except ValueError:
                logger.warn('[LineNo:%d, col%d] Expected field "%s" to be numeric, got: "%s"',
                            line_number, field.start-1, field.name, content)
                content_is_valid = False
                continue
        elif field.type == 'Alphanumeric':
            pass  # maybe we can regex check some of these later
        # The below is extremely spammy, turn on selectively.
        # logger.debug('field: %s\t::content: "%s"\t::end: %s', field.name, content, field.end)

        if content_is_valid:
            setattr(model, field.name, content)

    if not content_is_valid:
        logger.warn('Content is not valid, skipping model creation.')
        return

    # try:
    # model.full_clean()
    model.save()

def active_t1_parser(line, line_number):
    """Parse line in datafile as active case data, T1 only."""
    family_case_schema = t1_schema()
    # create search_index model
    t1 = T1()

    min_line_length = 118  # we will need to adjust for other types
    actual_line_length = len(line)
    active_parse(actual_line_length, min_line_length, family_case_schema, line, line_number, t1)
    '''
    # holdovers for 1354
        ParserLog.objects.create(
            data_file=datafile,
            status=ParserLog.Status.ACCEPTED,
        )

    except ValidationError as e:
        return ParserLog.objects.create(
            data_file=datafile,
            status=ParserLog.Status.ACCEPTED_WITH_ERRORS,
            errors=e.message
        )
    '''

def active_t2_parser(line, line_number):
    """Parse line in datafile as active case data, T1 only."""
    adult_data_schema = t2_schema()
    # create search_index model
    t2 = T2()

    min_line_length = 156  # we will need to adjust for other types
    actual_line_length = len(line)
    active_parse(actual_line_length, min_line_length, adult_data_schema, line, line_number, t2)

def active_t3_parser(line, line_number):
    """Parse line in datafile as active case data, T1 only."""
    children_data_schema = t3_schema()
    # create search_index model
    t2 = T3()

    min_line_length = 156  # we will need to adjust for other types
    actual_line_length = len(line)
    active_parse(actual_line_length, min_line_length, children_data_schema, line, line_number, t2)

# TODO: def closed_case_data(datafile):

# TODO: def aggregate_data(datafile):

# TODO: def stratum_data(datafile):

def parse(datafile):
    """Parse the datafile into the search_index model."""
    logger.info('Parsing TANF datafile: %s', datafile)

    datafile.seek(0)  # ensure we are at the beginning of the file
    line_number = 0
    for raw_line in datafile:
        line_number += 1
        if isinstance(raw_line, bytes):
            raw_line = raw_line.decode()
        line = raw_line.strip('\r\n')

        record_type = get_record_type(line)

        if record_type == 'HE' or record_type == 'TR':
            # Header/trailers do not differ between types, this is part of preparsing.
            continue
        elif record_type == 'T1':
            active_t1_parser(line, line_number)
        elif record_type == 'T2':
            active_t2_parser(line, line_number)
        elif record_type == 'T3':
            active_t3_parser(line, line_number)
        else:
            logger.warn("Parsing for type %s not yet implemented", record_type)
            continue
