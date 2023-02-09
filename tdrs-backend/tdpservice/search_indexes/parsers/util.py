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
