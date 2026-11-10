"""Table family and model resolution for production and shadow data files."""

from contextlib import nullcontext
from typing import Optional

from django.apps import apps

from tdpservice.data_files.enums import GoParserMode
from tdpservice.data_files.models import (
    DataFile,
    ReparseFileMeta,
    ShadowDataFile,
)
from tdpservice.data_files.submission_lifecycle import (
    claim_parse,
    parse_write_scope,
)
from tdpservice.parsers.models import (
    DataFileSummary,
    ParserError,
    ShadowDataFileSummary,
    ShadowParserError,
)

from .classes import ParserModelSet


def _program_code(data_file) -> Optional[str]:
    """Project a parser protocol program code from production or shadow data."""
    if data_file is not None and getattr(data_file, "program", None) is not None:
        return data_file.program.code
    return None


def _section_name(data_file) -> Optional[str]:
    """Project a parser protocol section name from production or shadow data."""
    if data_file is not None and getattr(data_file, "section", None) is not None:
        return data_file.section.name
    return None


def _shadow_record_model(production_model):
    """Return the Django model for the Go parser shadow copy of a record table."""
    shadow_table_name = f"shadow_{production_model._meta.db_table}"
    for model in apps.get_app_config("search_indexes").get_models():
        if model._meta.db_table == shadow_table_name:
            return model
    raise LookupError(
        f"No shadow model found for table {production_model._meta.db_table}"
    )


def _production_parser_models() -> ParserModelSet:
    """Return parser models for production parser output."""
    return ParserModelSet(
        data_file_model=DataFile,
        summary_model=DataFileSummary,
        parser_error_model=ParserError,
        record_model_resolver=lambda production_model: production_model,
        label="production",
    )


def _shadow_parser_models() -> ParserModelSet:
    """Return parser models for Go parser shadow output."""
    return ParserModelSet(
        data_file_model=ShadowDataFile,
        summary_model=ShadowDataFileSummary,
        parser_error_model=ShadowParserError,
        record_model_resolver=_shadow_record_model,
        label="shadow",
    )


def _uses_shadow_table(model_or_instance) -> bool:
    """Return whether a model or instance belongs to a shadow table family."""
    if model_or_instance is None:
        return False
    return model_or_instance._meta.db_table.startswith("shadow_")


def _parse_write_scope(data_file, parse_token=None):
    """Return an ownership fence for production parser writes."""
    if parse_token is None or _uses_shadow_table(data_file):
        return nullcontext()
    return parse_write_scope(data_file.id, parse_token)


def _parser_models_for_instance(model_or_instance) -> ParserModelSet:
    """Return the model set matching the table family of a model or instance."""
    if _uses_shadow_table(model_or_instance):
        return _shadow_parser_models()
    return _production_parser_models()


def _parser_models_for_mode(table_mode: str | None) -> ParserModelSet:
    """Return the exact table family selected when the task was dispatched."""
    if table_mode == GoParserMode.GO_SHADOW.value:
        return _shadow_parser_models()
    if table_mode == GoParserMode.GO_ONLY.value:
        return _production_parser_models()
    raise ValueError(f"Unsupported Go parser table mode: {table_mode!r}")


def _resolve_parse_owner(data_file, reparse_id=None, parse_token=None):
    """Resolve one task's reparse metadata and exclusive ownership token."""
    file_meta = None
    if reparse_id:
        file_meta = ReparseFileMeta.objects.get(
            data_file_id=data_file.id,
            reparse_meta_id=reparse_id,
        )
    if parse_token is None:
        parse_token = claim_parse(data_file, reparse_file_meta=file_meta)
    return file_meta, str(parse_token)
