"""Shared helpers for parser tests."""

from tdpservice.data_files.util import get_datafile_classification
from tdpservice.parsers.factory import ParserFactory


def parse_datafile(dfs, datafile, **factory_kwargs):
    """Parse a datafile using the parser factory with consistent defaults."""
    dfs.datafile = datafile
    program_type, section = get_datafile_classification(datafile)
    parser = ParserFactory.get_instance(
        datafile=datafile,
        dfs=dfs,
        section=factory_kwargs.pop("section", section),
        program_type=factory_kwargs.pop("program_type", program_type),
        **factory_kwargs,
    )
    parser.parse_and_validate()
    return parser
