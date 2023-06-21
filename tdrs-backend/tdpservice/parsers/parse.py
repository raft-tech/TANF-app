"""Convert raw uploaded Datafile into a parsed model, and accumulate/return any errors."""


import itertools
from .models import ParserErrorCategoryChoices, ParserError
from . import schema_defs, validators, util
from tdpservice.parsers.util import begin_transaction, end_transaction, rollback
import time


def parse_datafile(datafile):
    """Parse and validate Datafile header/trailer, then select appropriate schema and parse/validate all lines."""
    rawfile = datafile.file
    errors = {}

    # parse header, trailer
    rawfile.seek(0)
    header_line = rawfile.readline().decode().strip()
    header, header_is_valid, header_errors = schema_defs.header.parse_and_validate(
        header_line,
        util.make_generate_parser_error(datafile, 1)
    )
    if not header_is_valid:
        errors['header'] = header_errors
        ParserError.objects.bulk_create(header_errors)
        return errors

    # ensure file section matches upload section
    program_type = header['program_type']
    section = header['type']

    section_is_valid, section_error = validators.validate_header_section_matches_submission(
        datafile,
        program_type,
        section,
    )

    if not section_is_valid:
        errors['document'] = [section_error]
        unsaved_parser_errors = {1: [section_error]}
        bulk_create_errors(unsaved_parser_errors)
        return errors

    line_errors = parse_datafile_lines(datafile, program_type, section)

    errors = errors | line_errors

    return errors


def bulk_create_records(unsaved_records, line_number, header_count, batch_size=20000, flush=False):
    """Bulk create passed in records."""
    if (line_number % batch_size == 0 and header_count > 0) or flush:
        for model, records in unsaved_records.items():
            model.objects.bulk_create(records)
        return {}
    return unsaved_records

def bulk_create_errors(unsaved_parser_errors):
    """Bulk create all ParserErrors"""
    if unsaved_parser_errors:
        ParserError.objects.bulk_create(list(itertools.chain.from_iterable(unsaved_parser_errors.values())))

def evaluate_trailer(datafile, trailer_count, multiple_trailer_errors, is_last_line, line):
    """Validate datafile trailer and return associated errors if any."""
    if trailer_count > 1 and not multiple_trailer_errors:
        return (True, [util.make_generate_parser_error(datafile, -1)(
                schema=None,
                error_category=ParserErrorCategoryChoices.PRE_CHECK,
                error_message="Multiple trailers found.",
                record=None,
                field=None
            )])
    if trailer_count == 1 or is_last_line:
        record, trailer_is_valid, trailer_errors = schema_defs.trailer.parse_and_validate(
            line,
            util.make_generate_parser_error(datafile, -1)
        )
        return (multiple_trailer_errors, None if not trailer_errors else trailer_errors)
    return (False, None)


def signal_last(iterable):
    """Convenience function to indicate when the end of a generator has been reached."""
    it = iter(iterable)
    for val in it:
        yield val, False
    yield b"", True


def parse_datafile_lines(datafile, program_type, section):
    """Parse lines with appropriate schema and return errors."""
    rawfile = datafile.file
    errors = {}

    line_number = 0
    schema_manager_options = get_schema_manager_options(program_type)

    unsaved_records = {}
    unsaved_parser_errors = {}

    header_count = 0
    trailer_count = 0
    prev_sum = 0
    multiple_trailer_errors = False

    # Note: it is unnecessary to call rawfile.seek(0) again because the generator
    # automatically starts back at the begining of the file.
    begin_transaction()
    file_length = len(rawfile)
    offset = 0
    for rawline in rawfile:
        line_number += 1
        offset += len(rawline)
        line = rawline.decode().strip('\r\n')

        header_count += int(line.startswith('HEADER'))
        trailer_count += int(line.startswith('TRAILER'))

        is_last = offset == file_length
        multiple_trailer_errors, trailer_errors = evaluate_trailer(datafile, trailer_count, multiple_trailer_errors,
                                                                   is_last, line)

        if trailer_errors is not None:
            errors['trailer'] = trailer_errors
            unsaved_parser_errors.update({"trailer": trailer_errors})

        if header_count > 1:
            errors.update({'document': ['Multiple headers found.']})
            err_obj = util.make_generate_parser_error(datafile, line_number)(
                schema=None,
                error_category=ParserErrorCategoryChoices.PRE_CHECK,
                error_message="Multiple headers found.",
                record=None,
                field=None
            )
            unsaved_parser_errors.update({line_number: [err_obj]})
            rollback()
            bulk_create_errors(unsaved_parser_errors)
            return errors

        if prev_sum != header_count + trailer_count:
            prev_sum = header_count + trailer_count
            continue

        schema_manager = get_schema_manager(line, section, schema_manager_options)

        records = manager_parse_line(line, schema_manager, util.make_generate_parser_error(datafile, line_number))

        record_number = 0
        for i in range(len(records)):
            r = records[i]
            record_number += 1
            record, record_is_valid, record_errors = r
            if not record_is_valid:
                line_errors = errors.get(line_number, {})
                line_errors.update({record_number: record_errors})
                errors.update({line_number: record_errors})
                unsaved_parser_errors.update({line_number: record_errors})
            if record:
                s = schema_manager.schemas[i]
                unsaved_records.setdefault(s.model, []).append(record)

        unsaved_records = bulk_create_records(unsaved_records, line_number, header_count,)

    if header_count == 0:
        errors.update({'document': ['No headers found.']})
        err_obj = util.make_generate_parser_error(datafile, line_number)(
            schema=None,
            error_category=ParserErrorCategoryChoices.PRE_CHECK,
            error_message="No headers found.",
            record=None,
            field=None
        )
        rollback()
        unsaved_parser_errors.update({line_number: [err_obj]})
        bulk_create_errors(unsaved_parser_errors)
        return errors

    bulk_create_records(unsaved_records, line_number, header_count, flush=True)
    end_transaction()

    bulk_create_errors(unsaved_parser_errors)

    return errors


def manager_parse_line(line, schema_manager, generate_error):
    """Parse and validate a datafile line using SchemaManager."""
    if schema_manager.schemas:
        records = schema_manager.parse_and_validate(line, generate_error)
        return records

    return [(None, False, [
        generate_error(
            schema=None,
            error_category=ParserErrorCategoryChoices.PRE_CHECK,
            error_message="Record Type is missing from record.",
            record=None,
            field=None
        )
    ])]


def get_schema_manager_options(program_type):
    """Return the allowed schema options."""
    match program_type:
        case 'TAN':
            return {
                'A': {
                    'T1': schema_defs.tanf.t1,
                    'T2': schema_defs.tanf.t2,
                    'T3': schema_defs.tanf.t3,
                },
                'C': {
                    # 'T4': schema_options.t4,
                    # 'T5': schema_options.t5,
                },
                'G': {
                    # 'T6': schema_options.t6,
                },
                'S': {
                    # 'T7': schema_options.t7,
                },
            }
        case 'SSP':
            return {
                'A': {
                    'M1': schema_defs.ssp.m1,
                    'M2': schema_defs.ssp.m2,
                    'M3': schema_defs.ssp.m3,
                },
                'C': {
                    # 'M4': schema_options.m4,
                    # 'M5': schema_options.m5,
                },
                'G': {
                    # 'M6': schema_options.m6,
                },
                'S': {
                    # 'M7': schema_options.m7,
                },
            }
        # case tribal?
    return None


def get_schema_manager(line, section, schema_options):
    """Return the appropriate schema for the line."""
    line_type = line[0:2]
    return schema_options.get(section, {}).get(line_type, util.SchemaManager([]))
