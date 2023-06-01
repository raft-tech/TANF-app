"""Convert raw uploaded Datafile into a parsed model, and accumulate/return any errors."""


from . import schema_defs, util
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.util import begin_transaction, end_transaction, rollback


def parse_datafile(datafile):
    """Parse and validate Datafile header/trailer, then select appropriate schema and parse/validate all lines."""
    rawfile = datafile.file
    errors = {}

    # parse header, trailer
    rawfile.seek(0)
    header_line = rawfile.readline().decode().strip()
    header, header_is_valid, header_errors = schema_defs.header.parse_and_validate(header_line)
    if not header_is_valid:
        errors['header'] = header_errors
        return errors

    # ensure file section matches upload section
    section_names = {
        'TAN': {
            'A': DataFile.Section.ACTIVE_CASE_DATA,
            'C': DataFile.Section.CLOSED_CASE_DATA,
            'G': DataFile.Section.AGGREGATE_DATA,
            'S': DataFile.Section.STRATUM_DATA,
        },
        'SSP': {
            'A': DataFile.Section.SSP_ACTIVE_CASE_DATA,
            'C': DataFile.Section.SSP_CLOSED_CASE_DATA,
            'G': DataFile.Section.SSP_AGGREGATE_DATA,
            'S': DataFile.Section.SSP_STRATUM_DATA,
        },
    }

    program_type = header['program_type']
    section = header['type']

    if datafile.section != section_names.get(program_type, {}).get(section):
        errors['document'] = ['Section does not match.']
        return errors

    line_errors = parse_datafile_lines(rawfile, program_type, section)

    errors = errors | line_errors

    return errors


def bulk_create_records(unsaved_records):
    """Bulk create passed in records."""
    for model, records in unsaved_records.items():
        model.objects.bulk_create(records)


def store_record(unsaved_records, record, model):
    """Store record in dictionary for later processing."""
    if record:
        unsaved_records.setdefault(model, []).append(record)


def evaluate_trailer(trailer_count, multiple_trailer_errors, line):
    """Validate datafile trailer and return associated errors if any."""
    if trailer_count > 1 and not multiple_trailer_errors:
        return (True, ['Multiple trailers found.'])
    if trailer_count == 1:
        record, trailer_is_valid, trailer_errors = schema_defs.trailer.parse_and_validate(line)
        return (multiple_trailer_errors, None if not trailer_errors else trailer_errors)
    return (False, None)


def parse_datafile_lines(rawfile, program_type, section):
    """Parse lines with appropriate schema and return errors."""
    errors = {}

    line_number = 0
    schema_options = get_schema_options(program_type)

    unsaved_records = {}

    header_count = 0
    trailer_count = 0
    prev_sum = 0
    multiple_trailer_errors = False

    # Note: it is unnecessary to call rawfile.seek(0) again because the generator
    # automatically starts back at the begining of the file.
    begin_transaction()
    for rawline in rawfile:
        line_number += 1
        line = rawline.decode().strip('\r\n')

        header_count += int(line.startswith('HEADER'))
        trailer_count += int(line.startswith('TRAILER'))

        multiple_trailer_errors, trailer_errors = evaluate_trailer(trailer_count, multiple_trailer_errors, line)
        if trailer_errors is not None:
            errors['trailer'] = trailer_errors

        if header_count > 1:
            errors.update({'document': ['Multiple headers found.']})
            rollback()
            return errors

        if prev_sum != header_count + trailer_count:
            prev_sum = header_count + trailer_count
            continue

        schema = get_schema(line, section, schema_options)

        if isinstance(schema, util.MultiRecordRowSchema):
            records = parse_multi_record_line(line, schema)

            record_number = 0
            for r, s in zip(records, schema.schemas):
                record_number += 1
                record, record_is_valid, record_errors = r
                if not record_is_valid:
                    line_errors = errors.get(line_number, {})
                    line_errors.update({record_number: record_errors})
                    errors.update({line_number: record_errors})
                store_record(unsaved_records, record, s.model)
        else:
            record, record_is_valid, record_errors = parse_datafile_line(line, schema)
            if not record_is_valid:
                errors.update({line_number: record_errors})
            store_record(unsaved_records, record, schema.model)

    if line_number % 50000 == 0 and header_count > 0:
        bulk_create_records(unsaved_records)
        unsaved_records.clear()

    if header_count == 0:
        errors.update({'document': ['No headers found.']})
        rollback()
        return errors

    bulk_create_records(unsaved_records)
    end_transaction()

    return errors


def parse_multi_record_line(line, schema):
    """Parse and validate a datafile line using MultiRecordRowSchema."""
    if schema:
        records = schema.parse_and_validate(line)
        return records

    return [(None, False, ['No schema selected.'])]


def parse_datafile_line(line, schema):
    """Parse and validate a datafile line and save any errors to the model."""
    if schema:
        record, record_is_valid, record_errors = schema.parse_and_validate(line)

        return record, record_is_valid, record_errors

    return (None, False, ['No schema selected.'])


def get_schema_options(program_type):
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


def get_schema(line, section, schema_options):
    """Return the appropriate schema for the line."""
    line_type = line[0:2]
    return schema_options.get(section, {}).get(line_type, None)
