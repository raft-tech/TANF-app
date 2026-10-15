# TDP Parsing Service

## Overview

The `ParsingService` provides a unified, decoupled interface for single-`DataFile` parsing and lifecycle orchestration. It encapsulates the parsing workflow previously embedded in Celery tasks (`parser_task.py`), separating domain logic (parsing, error calculation, summary creation, email notifications, state transitions) from worker and message broker concerns.

The service supports both:
1. **Python Parsing Pipeline (`service.run()`)**: Validates preconditions, selects the parser via `ParserFactory`, executes parsing and validation, calculates error and case aggregates, updates `DataFileSummary`, generates error reports, sends notifications, and transitions submission lifecycle state.
2. **Go Parser Post-Parse Finalization (`service.post_parse()`)**: Finalizes output from the high-throughput Go parser in both production (`go-only`) and shadow (`go-shadow`) modes, updating summaries, generating error reports, and recording state transitions.

```
                  +-----------------------------------+
                  |           DataFile                |
                  +-----------------+-----------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                           ParsingService                              |
+-----------------------------------------------------------------------+
      | (run)                                             | (post_parse)
      v                                                   v
+-------------------------+                     +-----------------------+
| Preconditions Validation|                     | Go Parser Finalization|
| ParserFactory Lookup    |                     | Error Report Gen      |
| Parse & Validate        |                     | Aggregate Refresh     |
| DataFileSummary Update  |                     | Lifecycle Transition  |
| Lifecycle Transition    |                     +-----------------------+
| Notification Email      |
+-------------------------+
      |
      v
+-------------------------+
|      ParseResult        |
|  (success, summary,     |
|   metrics, to_dict())   |
+-------------------------+
```

---

## Core Classes

### `ParsingService`
Defined in [`tdpservice.parsers.service`](file:///Users/hschwarz/Documents/Projects/TDP/dev/TANF-app/tdrs-backend/tdpservice/parsers/service.py).

`ParsingService` is responsible for enforcing precondition invariants (valid initial state, file existence, parse ownership tokens), instantiating the appropriate parser via `ParserFactory`, executing the parse lifecycle, creating/updating `DataFileSummary`, updating the lifecycle state via `DataFileStateTransition` (with execution metrics appended to `metadata`), and returning a structured `ParseResult`.

#### Constructor Arguments
| Parameter | Type | Default | Description |
|---|---|---|---|
| `data_file` | `Union[DataFile, ShadowDataFile]` | *Required* | Pre-fetched `DataFile` or `ShadowDataFile` instance. |
| `reparse_id` | `Optional[int]` | `None` | Optional `ReparseMeta` ID if running as part of a reparse workflow. |
| `parse_token` | `Optional[Union[UUID, str]]` | `None` | Concurrency/ownership lock token (UUID). |
| `event_id` | `Optional[Union[UUID, str]]` | `None` | Correlation ID for lifecycle audit trail (`DataFileStateTransition`). |
| `file_meta` | `Optional[ReparseFileMeta]` | `None` | Optional pre-resolved `ReparseFileMeta` instance. |

#### Primary Methods
- `run() -> ParseResult` (alias: `parse()`): Executes the complete Python parsing flow and returns the structured outcome.
- `post_parse(parse_error=None, table_mode=None, task_name=None) -> None`: Finalizes Go parser output for this DataFile in its selected table family.
- `fetch_data_file() -> Union[DataFile, ShadowDataFile]`: Returns the bound data file instance.
- `validate_preconditions() -> None`: Validates file presence, submission state eligibility, and token ownership without executing parsing.
- `get_parser() -> BaseParser`: Resolves and instantiates the parser for the bound DataFile.

---

### `ParseResult`
Dataclass representing the structured outcome of a parsing operation.

#### Attributes
| Field | Type | Description |
|---|---|---|
| `success` | `bool` | `True` if parsing completed without fatal errors, `False` otherwise. |
| `data_file` | `Optional[Union[DataFile, ShadowDataFile]]` | The file that was parsed. |
| `summary` | `Optional[Union[DataFileSummary, ShadowDataFileSummary]]` | The created or updated summary record. |
| `status` | `Optional[str]` | The final `DataFileSummary.Status` (`ACCEPTED`, `ACCEPTED_WITH_ERRORS`, `PARTIALLY_ACCEPTED`, `REJECTED`). |
| `error_message` | `Optional[str]` | Failure explanation if `success` is `False`. |
| `total_records_processed` | `int` | Total number of data records parsed from the file. |
| `total_errors_generated` | `int` | Total count of parser error records generated during parsing. |

#### Serialization (`to_dict()`)
To ensure memory safety and clean Celery serialization across Redis brokers, `ParseResult.to_dict()` serializes results into primitives:
```python
{
    "success": True,
    "data_file_id": 123,
    "summary_id": 456,
    "status": "Accepted",
    "error_message": None,
    "total_records_processed": 5000,
    "total_errors_generated": 0,
}
```

---

## Execution Metadata & State Transitions

Parse execution metrics are appended directly to the `metadata` JSON field on the terminal [`DataFileStateTransition`](file:///Users/hschwarz/Documents/Projects/TDP/dev/TANF-app/tdrs-backend/tdpservice/data_files/models.py) record (e.g. `COMPLETED`, `PARSED_WITH_ERRORS`, or `PARSE_FAILED`) for both production `DataFile` and `ShadowDataFile` instances.

### Transition Metadata Fields
| Field | Type | Description |
|---|---|---|
| `parser_class` | `str` | Name of parser class executed (e.g., `TanfDataReportParser`, `GoParser`). |
| `execution_duration_ms` | `int` | Parse execution duration in milliseconds. |
| `total_records_processed` | `int` | Total number of data records parsed from the file. |
| `total_errors_generated` | `int` | Total count of parser error records generated during parsing. |
| `section` | `Optional[str]` | DataFile section name. |
| `program_type` | `Optional[str]` | Program type (e.g. TANF, SSP, Tribal, FRA). |
| `parse_summary_status` | `Optional[str]` | Final summary status on completion. |
| `parse_error` | `Optional[str]` | Error message if parsing failed. |

---

## Usage Examples

### 1. Direct / Synchronous Execution
Useful in management commands, synchronous scripts, test fixtures, or debugging:

```python
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.service import ParsingService

data_file = DataFile.objects.get(id=123)
service = ParsingService(data_file=data_file)
result = service.run()

if result.success:
    print(f"Parsed successfully with status: {result.status}")
    print(f"Summary ID: {result.summary.id}, Total Errors: {result.total_errors_generated}")
else:
    print(f"Parsing failed: {result.error_message}")
```

### 2. Celery Asynchronous Task Delegation
In [`tdpservice.scheduling.parser_task`](file:///Users/hschwarz/Documents/Projects/TDP/dev/TANF-app/tdrs-backend/tdpservice/scheduling/parser_task.py), the `@shared_task def parse` delegates directly to `ParsingService`:

```python
@shared_task
def parse(data_file_id, reparse_id=None, parse_token=None, event_id=None):
    """Send data file for processing."""
    data_file = DataFile.objects.get(id=data_file_id)
    service = ParsingService(
        data_file=data_file,
        reparse_id=reparse_id,
        parse_token=parse_token,
        event_id=event_id,
    )
    result = service.run()
    if not result.success and (
        result.data_file is None
        or (service.parse_token is None and not _uses_shadow_table(result.data_file))
    ):
        if result.error_message:
            raise ValueError(result.error_message)
        raise RuntimeError("Parsing failed before ownership establishment")
    return result.to_dict()
```

### 3. Go Parser Post-Parse Finalization
When Go parser worker finishes execution, it sends a task to `post_parse`, which delegates to `ParsingService`:

```python
@shared_task(name=GO_PARSER_POST_PARSE_TASK_NAME)
def post_parse(
    data_file_id: int,
    reparse_id: int = 0,
    parse_error: str | None = None,
    table_mode: str | None = None,
    parse_token="",
    event_id=None,
) -> None:
    parser_models = _parser_models_for_mode(table_mode)
    data_file = parser_models.data_file_model.objects.get(id=data_file_id)
    service = ParsingService(
        data_file=data_file,
        reparse_id=reparse_id or None,
        parse_token=parse_token or None,
        event_id=event_id,
    )
    service.post_parse(
        parse_error=parse_error,
        table_mode=table_mode,
        task_name=GO_PARSER_POST_PARSE_TASK_NAME,
    )
```

---

## Testing

Run unit tests for `ParsingService`:
```bash
task backend-pytest PYTEST_ARGS="tdpservice/parsers/test/test_parsing_service.py -vv"
```

Run Celery task tests:
```bash
task backend-pytest PYTEST_ARGS="tdpservice/scheduling/test/test_parser_task.py -vv"
```

Run all parser tests:
```bash
task backend-pytest PYTEST_ARGS="tdpservice/parsers/test/ -vv"
```
