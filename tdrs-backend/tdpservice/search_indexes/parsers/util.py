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
        # if len(row) != 156:
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
