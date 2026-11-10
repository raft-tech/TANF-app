"""Transient execution engine for legacy Python-based file parsing."""

from typing import Optional, Union

from tdpservice.data_files.models import DataFile, ShadowDataFile
from tdpservice.parsers.factory import ParserFactory
from tdpservice.parsers.models import DataFileSummary, ShadowDataFileSummary

from .table_family import _program_code, _section_name


class PythonParserEngine:
    """Transient execution engine for legacy Python-based file parsing."""

    def __init__(
        self,
        data_file: Union[DataFile, ShadowDataFile],
        dfs: Optional[Union[DataFileSummary, ShadowDataFileSummary]] = None,
        parse_token: Optional[str] = None,
    ):
        self.data_file = data_file
        self.dfs = dfs
        self.parse_token = parse_token

    def get_parser(self):
        """Construct and return the appropriate parser instance via ParserFactory."""
        return ParserFactory.get_instance(
            datafile=self.data_file,
            dfs=self.dfs,
            section=_section_name(self.data_file),
            program_type=_program_code(self.data_file),
            is_program_audit=getattr(self.data_file, "is_program_audit", False),
            parse_token=self.parse_token,
        )

    def execute(self):
        """Execute legacy Python parser."""
        parser = self.get_parser()
        if hasattr(parser, "parse_and_validate"):
            parser.parse_and_validate()
        elif hasattr(parser, "parse"):
            parser.parse()
        return parser
