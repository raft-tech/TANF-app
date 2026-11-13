"""Data classes and models for the parsing service."""

from dataclasses import dataclass
from typing import Any, Callable, Optional, Union

from tdpservice.data_files.models import DataFile, ShadowDataFile
from tdpservice.parsers.models import DataFileSummary, ShadowDataFileSummary


@dataclass(frozen=True)
class ParserModelSet:
    """Models and lookup hooks for a parser output table family."""

    data_file_model: type
    summary_model: type
    parser_error_model: type
    record_model_resolver: Callable[[type], type]
    label: str


@dataclass
class ParseResult:
    """Structured result of a single DataFile parsing execution."""

    success: bool
    data_file: Optional[Union[DataFile, ShadowDataFile]] = None
    summary: Optional[Union[DataFileSummary, ShadowDataFileSummary]] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    total_records_processed: int = 0
    total_errors_generated: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Return a lightweight, JSON-serializable dictionary representation."""
        return {
            "success": self.success,
            "data_file_id": getattr(self.data_file, "id", None),
            "summary_id": getattr(self.summary, "id", None),
            "status": self.status,
            "error_message": self.error_message,
            "total_records_processed": self.total_records_processed,
            "total_errors_generated": self.total_errors_generated,
        }
