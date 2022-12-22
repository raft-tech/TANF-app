"""Utility file for functions shared between all parsers even preparser."""

import logging
import re

logger = logging.getLogger(__name__)


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

class Field:
    """Provides a mapping between a field name and its position."""

    def __init__(self, name, length, start, end, type):
        self.name = name
        self.length = length
        self.start = start
        self.end = end
        self.type = type

    def create(self, name, length, start, end, type):
        """Create a new field."""
        return Field(name, length, start, end, type)

    def __repr__(self):
        """Return a string representation of the field."""
        return f"{self.name}({self.start}-{self.end})"

class RowSchema:
    """Maps the schema for data rows."""

    def __init__(self):  # , section):
        self.fields = []
        # self.section = section # intended for future use with multiple section objects

    def add_field(self, name, length, start, end, type):
        """Add a field to the schema."""
        self.fields.append(
            Field(name, length, start, end, type)
        )

    def add_fields(self, fields: list):
        """Add multiple fields to the schema."""
        for field, length, start, end, type in fields:
            self.add_field(field, length, start, end, type)

    def get_field(self, name):
        """Get a field from the schema."""
        return self.fields[name]

    def get_field_names(self):
        """Get all field names from the schema."""
        return self.fields.keys()

    def get_all_fields(self):
        """Get all fields from the schema."""
        return self.fields
