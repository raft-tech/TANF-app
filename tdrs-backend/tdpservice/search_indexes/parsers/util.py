"""Utility file for functions shared between all parsers even preparser."""

import logging

logger = logging.getLogger(__name__)


def get_record_type(line):
    """Get the record type from the line."""
    line = line.decode() if isinstance(line, bytes) else line

    if line.startswith('HEADER'):
        logger.debug('Matched following line as a header: %s' % line)
        return 'HE'
    elif line.startswith('TRAILER'):
        logger.debug('Matched following line as a trailer: %s' % line)
        return 'TR'
    elif line.startswith('T1'):
        logger.debug('Matched following line as data: %s' % line)
        return 'T1'
    elif line.startswith('T2'):
        logger.debug('Matched following line as data: %s' % line)
        return 'T2'
    elif line.startswith('T3'):
        logger.debug('Matched following line as data: %s' % line)
        return 'T3'
    elif line.startswith('T4'):
        logger.debug('Matched following line as data: %s' % line)
        return 'T4'
    elif line.startswith('T5'):
        logger.debug('Matched following line as data: %s' % line)
        return 'T5'
    elif line.startswith('T6'):
        logger.debug('Matched following line as data: %s' % line)
        return 'T6'
    elif line.startswith('T7'):
        logger.debug('Matched following line as data: %s' % line)
        return 'T7'
    else:
        logger.debug('No match for line: %s' % line)
        return None

class Field:
    """Provides a mapping between a field name and its position."""

    def __init__(self, item_num, name, length, start, end, type, validators=[]):
        self.item_num = item_num
        self.name = name
        self.length = length
        self.start = start
        self.end = end
        self.type = type
        self.validators = validators

    def create(self, item_num, name, length, start, end, type, validators):
        """Create a new field."""
        return Field(item_num, name, length, start, end, type, validators)

    def __repr__(self):
        """Return a string representation of the field."""
        return f"{self.name}({self.start}-{self.end})"

class RowSchema:
    """Maps the schema for data lines."""

    def __init__(self):  # , section):
        self.fields = []
        # self.section = section # intended for future use with multiple section objects

    def add_field(self, item_num, name, length, start, end, type, validators):
        """Add a field to the schema."""
        self.fields.append(
            Field(item_num, name, length, start, end, type, validators)
        )

    def add_fields(self, fields: list):
        """Add multiple fields to the schema."""
        for item_num, field, length, start, end, type, validators in fields:
            self.add_field(item_num, field, length, start, end, type, validators)

    def get_field(self, name):
        """Get a field from the schema."""
        return self.fields[name]

    def get_field_names(self):
        """Get all field names from the schema."""
        return self.fields.keys()

    def get_all_fields(self):
        """Get all fields from the schema."""
        return self.fields
