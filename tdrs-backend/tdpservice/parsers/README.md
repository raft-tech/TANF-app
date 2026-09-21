# Parsing Service & Parsers Architecture

This directory contains the core parsing infrastructure for processing TANF, SSP, Tribal, and FRA data files submitted to TDP.

### Table of Contents
- [Overview](#overview)
- [Core Classes](#core-classes)
  - [ParsingService](#parsingservice)
  - [ParseResult](#parseresult)
- [Execution Metadata & State Transitions](#execution-metadata--state-transitions)
- [Example Usage](#example-usage)
  - [1. Direct / Synchronous Execution](#1-direct--synchronous-execution)
  - [2. Celery Single Task Execution](#2-celery-single-task-execution)
  - [3. Batch Execution Patterns](#3-batch-execution-patterns)
- [Parsing Lifecycle & Preconditions](#parsing-lifecycle--preconditions)
- [Testing](#testing)

---

## Overview

The parsing architecture follows a single-responsibility model centered around `ParsingService`. Each `ParsingService` instance is scoped to exactly **one** `DataFile`. Higher-level orchestration (such as Celery tasks, reparse campaigns, or batch imports) orchestrates individual `ParsingService` executions without leaking batch-processing logic into the core parser.

```
+-------------------------------------------------------------+
|                      Caller / Trigger                       |
|   (Celery Task / Reparse Orchestrator / Management Command) |
+-------------------------------------------------------------+
                              |
                              v
                   +--------------------+
                   |   ParsingService   |
                   +--------------------+
                              |
         +--------------------+--------------------+
         |                                         |
         v                                         v
+-----------------+                      +-------------------+
|  Preconditions  |                      |   ParserFactory   |
|   Validation    |                      |  (TANF/SSP/FRA)   |
+-----------------+                      +-------------------+
```

---

## Core Classes

### `ParsingService`
Defined in [`tdpservice.parsers.service`](file:///tdrs-backend/tdpservice/parsers/service.py).

`ParsingService` is responsible for fetching the `DataFile`, enforcing precondition invariants (valid initial status, file existence, parse ownership tokens), selecting and instantiating the appropriate parser via `ParserFactory`, executing the parse lifecycle, creating/updating `DataFileSummary`, updating the lifecycle state via `DataFileStateTransition` (with execution metrics appended to `metadata`), and returning a structured `ParseResult`.

#### Constructor Arguments
| Parameter | Type | Default | Description |
|---|---|---|---|
| `data_file_id` | `Optional[int]` | `None` | Primary key of target `DataFile`. |
| `data_file` | `Optional[DataFile]` | `None` | Pre-fetched `DataFile` instance. |
| `reparse_id` | `Optional[int]` | `None` | Optional `ReparseMeta` ID if running as part of a reparse workflow. |
| `parse_token` | `Optional[Union[UUID, str]]` | `None` | Concurrency/ownership lock token (UUID). |
| `event_id` | `Optional[Union[UUID, str]]` | `None` | Correlation ID for lifecycle audit trail (`DataFileStateTransition`). |

#### Primary Methods
- `run() -> ParseResult` (alias: `parse()`): Executes the complete parsing flow and returns the structured outcome.
- `fetch_data_file() -> DataFile`: Resolves and caches the `DataFile` instance.
- `validate_preconditions() -> None`: Validates file presence, submission state eligibility, and token ownership without executing parsing.
- `get_parser() -> BaseParser`: Resolves the parser class for the `DataFile`'s section and program type.

---

### `ParseResult`
Dataclass representing the structured outcome of a parsing operation.

#### Attributes
| Field | Type | Description |
|---|---|---|
| `success` | `bool` | `True` if parsing completed without fatal errors, `False` otherwise. |
| `data_file` | `Optional[DataFile]` | The `DataFile` that was parsed. |
| `summary` | `Optional[DataFileSummary]` | The created or updated summary record. |
| `status` | `Optional[str]` | The final `DataFileSummary.Status` (e.g. `ACCEPTED`, `ACCEPTED_WITH_ERRORS`, `REJECTED`). |
| `errors` | `list[ParserError]` | List of generated `ParserError` records associated with the file. |
| `error_message` | `Optional[str]` | Failure explanation if `success` is `False`. |

---

## Execution Metadata & State Transitions

Parse execution metrics are appended directly to the `metadata` JSON field on the terminal [`DataFileStateTransition`](file:///tdrs-backend/tdpservice/data_files/models.py) record (e.g. `COMPLETED` or `PARSE_FAILED`) for both production `DataFile` and `ShadowDataFile` instances.

### Transition Metadata Fields
| Field | Type | Description |
|---|---|---|
| `parser_class` | `str` | Name of parser class executed (e.g., `ActiveSection1Parser`, `GoParser`). |
| `execution_duration_ms` | `int` | Parse execution duration in milliseconds. |
| `total_records_processed` | `int` | Total number of data records parsed from the file. |
| `total_errors_generated` | `int` | Total count of parser error records generated during parsing. |
| `section` | `Optional[str]` | DataFile section name. |
| `program_type` | `Optional[str]` | Program type (e.g. TANF, SSP, Tribal, FRA). |
| `parse_summary_status` | `Optional[str]` | Final summary status on completion. |
| `parse_error` / `error` | `Optional[str]` | Error message / traceback snippet if parsing failed. |


---

## Example Usage

### 1. Direct / Synchronous Execution
Useful in management commands, scripts, synchronous debugging, or test fixtures:

```python
from tdpservice.parsers.service import ParsingService

# By DataFile ID
service = ParsingService(data_file_id=123)
result = service.run()

if result.success:
    print(f"Parsed successfully with status: {result.status}")
    print(f"Summary ID: {result.summary.id}, Total Errors: {len(result.errors)}")
else:
    print(f"Parsing failed: {result.error_message}")
```

Or with an existing `DataFile` instance:

```python
data_file = DataFile.objects.get(id=123)
service = ParsingService(data_file=data_file)
result = service.run()
```

---

### 2. Celery Single Task Execution
Standard asynchronous single-file submission queueing:

```python
import uuid
from tdpservice.scheduling.parser_task import parse, queue_parse

# High-level dispatch (claims parse ownership token, dispatches Python parse & Go shadow parse)
event_id = uuid.uuid4()
parse_token = queue_parse(data_file_id=123, event_id=event_id)

# Direct Celery task dispatch (when token is already claimed)
parse.delay(
    data_file_id=123,
    parse_token=str(parse_token),
    event_id=str(event_id),
)
```

Inside [`tdpservice.scheduling.parser_task.parse`](file:///tdrs-backend/tdpservice/scheduling/parser_task.py), the Celery task delegates directly to `ParsingService`:

```python
@shared_task
def parse(data_file_id, reparse_id=None, parse_token=None, event_id=None):
    service = ParsingService(
        data_file_id=data_file_id,
        reparse_id=reparse_id,
        parse_token=parse_token,
        event_id=event_id,
    )
    service.fetch_data_file()
    service.validate_preconditions()
    return service.run()
```

---

### 3. Batch Execution Patterns
Because `ParsingService` is strictly scoped to a single `DataFile`, batch operations (such as processing all files in a quarter or re-running multiple STTs) are orchestrated by grouping single-file tasks.

#### Option A: Celery Group / Chord (Concurrent Asynchronous Batch)
```python
from celery import group
from tdpservice.scheduling.parser_task import queue_parse

def process_batch_files(data_file_ids):
    """Queue parsing for a batch of DataFiles concurrently."""
    tokens = {}
    for df_id in data_file_ids:
        # queue_parse handles token ownership and triggers parse.delay
        token = queue_parse(data_file_id=df_id)
        tokens[df_id] = token
    return tokens
```

#### Option B: Sequential Batch Execution (Management Command / Reparse Script)
```python
import logging
from tdpservice.parsers.service import ParsingService

logger = logging.getLogger(__name__)

def parse_batch_sequentially(data_files):
    """Process a batch of DataFile instances sequentially."""
    results = []
    for data_file in data_files:
        service = ParsingService(data_file=data_file)
        try:
            result = service.run()
            results.append(result)
            logger.info(f"File {data_file.id} finished with success={result.success}")
        except Exception as exc:
            logger.error(f"File {data_file.id} failed unexpectedly: {exc}")
    return results
```

---

## Parsing Lifecycle & Preconditions

`ParsingService.validate_preconditions()` enforces the following checks before parse execution starts:
1. **File Attached**: Verifies that `DataFile.file` is present and non-empty.
2. **State Validity**: Ensures the `DataFile.state` is in `VIRUS_SCAN_COMPLETED`, `REPARSE_REQUESTED`, `PARSE_STARTED`, or `PARSE_FAILED`. Rejects files in `UPLOADED`, `VIRUS_SCAN_STARTED`, `VIRUS_SCAN_FAILED`, etc.
3. **Token Ownership Guard**: Validates that if a `parse_token` is active on the `DataFile`, it matches the current worker's token (preventing split-brain / stale task executions).

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

Run the full parser test suite:
```bash
task backend-pytest PYTEST_ARGS="tdpservice/parsers/test/ -vv"
```

