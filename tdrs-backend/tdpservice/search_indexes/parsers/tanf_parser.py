"""Transforms a TANF datafile into an search_index model."""

import logging
from ..models import T1  # , T2, T3, T4, T5, T6, T7, ParserLog
# from django.core.exceptions import ValidationError
from .util import get_record_type
from .schema_defs.tanf import t1_schema
from tdpservice.search_indexes.parsers.validators.category2 import validate_cat2
from tdpservice.search_indexes.parsers.validators.category3 import validate_cat3

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def active_t1_parser(line, line_number):
    """Parse line in datafile as active case data, T1 only."""
    family_case_schema = t1_schema()
    # create search_index model
    t1 = T1()
    content_is_valid = True

    min_line_length = 118  # we will need to adjust for other types
    actual_line_length = len(line)
    if actual_line_length < min_line_length:
        logger.error('Expected minimum line length of %s, got: %s', min_line_length, actual_line_length)
        return

    for field in family_case_schema:
        print(f'Field: {field}')
        if field['description'] == 'blank':
            # We are discarding this data.
            break
        content = line[field['start']-1:field['end']]  # descriptor pdfs were off by one, could also adjust start values

        # check if content is type string or integer
        if field['data_type'] == 'Numeric':
            try:
                content = int(content)
            except ValueError:
                logger.warn('[LineNo:%d, col%d] Expected field "%s" to be numeric, got: "%s"',
                            line_number, field['start']-1, field['description'], content)
                content_is_valid = False
                continue
        elif field['data_type'] == 'Alphanumeric':
            pass  # maybe we can regex check some of these later
        # The below is extremely spammy, turn on selectively.
        # logger.debug('field: %s\t::content: "%s"\t::end: %s', field.name, content, field.end)

        if content_is_valid:
            setattr(t1, field['description'], content)

    if content_is_valid is False:
        logger.warn('Content is not valid, skipping model creation.')
        return

    run_validation(family_case_schema, t1)

    # try:
    # t1.full_clean()
    t1.save()
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
        else:
            logger.warn("Parsing for type %s not yet implemented", record_type)
            continue

def run_validation(family_case_schema, t1):
    """Run validation on the datafile."""
    cat2_errors = validate(family_case_schema, t1, 'cat2_conditions', validate_cat2)

    if len(cat2_errors) > 0:
        logger.warn(f'There are {len(cat2_errors)} cat2 errors:')
        for error in cat2_errors:
            logger.warn(error)

    cat3_errors = validate(family_case_schema, t1, 'cat3_conditions', validate_cat3)
    if len(cat3_errors) > 0:
        logger.warn(f'There are {len(cat3_errors)} cat3 errors:')
        for error in cat3_errors:
            logger.warn(error)


def validate(schema, model_obj, category, validator):
    """Validate the datafile.

    This function takes a parsing schema, which holds the fields and conditions,
    A Django model obj, a catagory string that corresponds to a dictionary on the schema,
    and a validator function.

    For each row on the schema the field, condition, and value are taken and run through the
    validator function, along with the model_obj.

    If there are errors they are returned.
    """
    errors = []
    for field in schema:
        name = field['description']
        if name == 'BLANK':
            continue
        value = getattr(model_obj, name)
        category_conditions = field[category]
        category_errors = None
        if category_conditions != {}:
            if 'custom' in category_conditions:
                for custom_validator in category_conditions['custom']:
                    category_errors = custom_validator(model_obj)
                    if len(category_errors) > 0:
                        errors.append(category_errors)
            else:
                category_errors = validator(name, value, category_conditions, model_obj)

            if len(category_errors) > 0:
                errors.append(category_errors)

    return errors
