# Technical Memo: Refactoring Parsing and Reparsing in TANF Data Portal Backend

## 1. Purpose

This memo proposes a refactor of the **parsing** and **reparsing** pipelines in the TANF Data Portal backend (`tdrs-backend`). The goal is to:

- Reduce duplicated orchestration logic between initial parsing and reparsing
- Make parsing behavior easier to reason about, test, and extend
- Improve performance and observability for large-scale reparsing operations
- Clearly separate “what to parse” (selection) from “how to parse” (pipeline)
- Establish a stable contract (service + state machine) so new file types and policy changes do not require touching Celery tasks or ad hoc utilities.

### Why this refactor is beneficial
- **Single source of truth for parsing logic:** Today, behavior is split across parser classes, the Celery task, and reparse utilities. Moving to a `ParsingService` collapses side effects (status updates, summaries, error reports) into one place, reducing drift and regression risk.
- **Testability:** A service with clear inputs/outputs can be unit-tested without Celery, making it easier to cover both happy paths and failure modes. Reparsing can reuse the same entry point with explicit context.
- **Extensibility:** A factory-driven, class-based parser plus decoder abstraction makes it straightforward to add file types (e.g., new CSV/XLSX variants) or program types without rewriting orchestration. SchemaManager and decoders become the main extension points.
- **Operational clarity:** With the submission state machine and centralized transitions, operators and users see consistent states (e.g., `parsing`, `parsed_with_errors`, `ingest_failed`) instead of implicit flags scattered across models.
- **Safer reparsing:** Consolidating reparse behavior (backups, deletions, status updates) through the same service and state transitions improves idempotency, makes resume/rollback safer, and keeps `ReparseMeta`/`ReparseFileMeta` in sync.
- **Observability:** Centralized logging and optional metrics around a single service boundary make it easier to trace a file’s journey, correlate errors, and measure performance (parse durations, error counts).

The recommendations are based on the current implementation in:

- `tdpservice/parsers/…`
- `tdpservice/scheduling/parser_task.py`
- `tdpservice/search_indexes/reparse.py`
- `tdpservice/search_indexes/utils.py`
- `tdpservice/search_indexes/models/reparse_meta.py`
- `tdpservice/data_files/models.py` (especially `DataFile` and `ReparseFileMeta`)


## 2. Current Architecture (High-Level)

### 2.1 Initial parsing flow

**Entry point:** a TANF/SSP/TRIBAL/FRA data file is uploaded (`DataFile` instance created).

**Core components:**

- **Celery task:** `tdpservice/scheduling/parser_task.parse_data_file`
  - Looks up the `DataFile`
  - Uses `ParserFactory` to get the correct parser class for the file’s program type
  - Calls parser methods (e.g., `parse_and_validate()`)
  - Updates `DataFileSummary` / status flags
  - Generates error reports via `ErrorReportFactory`
  - Sends notification emails (`send_data_submitted_email`)
  - If the parse is part of a reparse run, it also updates `ReparseFileMeta`

- **Parser infrastructure:**
  - `tdpservice/parsers/factory.ParserFactory`
  - `tdpservice/parsers/parser_classes/base_parser.BaseParser`
  - Concrete parsers:
    - `TanfDataReportParser`
    - `FRAParser`
    - `ProgramAuditParser`
  - `SchemaManager` (`schema_manager.py`) to manage program- and section-specific schema
  - `ErrorGeneratorFactory` and `ParserError` to generate and persist row-level errors
  - `DataFileSummary` to track high-level outcomes (record counts, error counts)

**Characteristics:**
- “Initial parse” logic is **implicitly defined** by the behavior inside `parse_data_file` and the individual parser classes.
- The Celery task contains non-trivial orchestration logic: logging, error handling, and special cases for reparse runs.


### 2.2 Reparsing flow

Reparsing is used to “clean and reprocess” existing data files, usually when schemas or validation logic change.

**Core components:**

- **Reparse orchestration:** `tdpservice/search_indexes/reparse.py`
  - User / admin triggers some “clean and reparse” behavior (fiscal year, quarter, optional filters)
  - Uses helpers from `tdpservice/search_indexes/utils.py` and `tdpservice/search_indexes/util.py`:
    - `backup(...)` → creates a DB backup
    - `delete_associated_models(...)` → deletes records associated with the selected files (ParserError, DataFileSummary, index rows, etc.)
    - `calculate_timeout(...)` / `assert_sequential_execution(...)` → safety checks for long-running reparses
    - `count_total_num_records(...)` / `count_all_records(...)` → record-count snapshots

- **Meta tracking models:**
  - `ReparseMeta` (`tdpservice/search_indexes/models/reparse_meta.py`)
    - Represents a single “reparse run” (with fields like `timeout_at`, `finished`, `success`, `total_num_records_initial`, `total_num_records_after`, etc.)
    - Aggregates related `ReparseFileMeta` records
  - `ReparseFileMeta` (`tdpservice/data_files/models.py`)
    - Represents the parse status of a single `DataFile` within a reparse run (finished, success, record counts, error counts)

- **Scheduling reparses:**
  - Once backup and deletion are done, `reparse.py` calls into `parser_task` for each `DataFile` to schedule Celery tasks for reparsing.
  - The same `parse_data_file` task is used, but with additional `reparse_id` context that ties the parse to a `ReparseMeta` / `ReparseFileMeta` pair.

**Characteristics:**
- Reparsing logic is spread across:
  - `search_indexes/reparse.py`
  - `search_indexes/utils.py`
  - `parser_task.parse_data_file`
  - The parsers and error-reporting logic
- `ReparseMeta` / `ReparseFileMeta` add an extra dimension of lifecycle and state, but much of the behavior to maintain them lives in the Celery task.


## 3. Pain Points & Risks

From a maintainability and performance perspective, several issues stand out:

### 3.1 Duplicated orchestration between “parse” and “reparse”

- The **initial parsing path** and the **reparsing path** both:
  - Determine which files to parse
  - Manage database state (deleting old records, updating summaries)
  - Schedule Celery tasks
  - Generate logs and metrics
- However, the logic to do this is split across multiple modules, and the reparsing path has its own backup / cleanup orchestration.
- When schemas or error-handling rules change, engineers must remember to update both flows, which increases the risk of subtle inconsistencies.

### 3.2 Tight coupling to Celery and logging

- `parse_data_file` is both a Celery task and a “business service”:
  - It contains domain logic (how we parse, validate, update summaries, etc.)
  - It also contains infrastructure concerns (Celery wiring, logging, email notifications, file rotation).
- This makes unit testing harder and encourages direct calls to the Celery task instead of to a clear, reusable parsing service.

### 3.3 Reparsing logic is scattered and not obviously idempotent

- `search_indexes/reparse.py` performs several responsibilities:
  - Safety checks (sequential execution, timeouts)
  - Backup orchestration
  - Bulk deletion of associated records
  - Scheduling reparse tasks for each `DataFile`
- Much of this logic operates directly on the DB and logging functions, which makes it harder to reason about/retry safely.
- While `ReparseMeta` / `ReparseFileMeta` provide state tracking, the actual transitions are implemented in different modules, making it non-obvious how to safely resume or inspect a partially finished reparse run.

### 3.4 Performance & operational concerns on large datasets

- `count_total_num_records(...)`, `count_all_records(...)`, and bulk deletions may become expensive as datasets grow.
- Parsing and reparsing touch several related tables (DataFile, ParserError, DataFileSummary, index tables, etc.), so the order and batching of operations matters for performance and locking behavior.
- Today, these concerns are embedded in the reparse utilities and Celery task without a single place to tune or monitor the pipeline behavior.


## 4. Proposed Refactor: Parsing & Reparsing as a Unified Service

The core idea is to **centralize parsing behavior** in a small, well-defined service layer and let:

- The Celery task (`parse_data_file`)
- The reparse orchestration (`clean_and_reparse` command / function)
- Any future “parse this file now” triggers

…all call the **same service** with different context (e.g., initial parse vs reparse run).


### 4.1 Introduce a `ParsingService`

Create a new module, for example:

- `tdpservice/parsing/service.py` or
- `tdpservice/parsers/service.py`

with a class like:

```python
class ParsingService:
    def __init__(self, *, logger, now_fn=timezone.now):
        self.logger = logger
        self.now_fn = now_fn

    def parse_data_file(self, data_file_id: int, *, reparse_meta: ReparseMeta | None = None) -> None:
        """
        Orchestrate the full lifecycle for parsing a single DataFile.

        - Load DataFile and related metadata
        - Select parser via ParserFactory
        - Invoke parser.parse_and_validate()
        - Update DataFileSummary / DataFile status
        - Generate error report
        - If reparse_meta is provided, update/attach ReparseFileMeta
        - Log outcome
        """
```

This service should encapsulate **what it means** to fully process a `DataFile`, regardless of why it is being parsed (initial submit or reparse).


### 4.2 Make Celery task a thin wrapper around the service

Refactor `tdpservice/scheduling/parser_task.parse_data_file` to:

- Parse out its Celery-specific concerns (arguments, retries, logging context)
- Delegate the core work to `ParsingService.parse_data_file`

Example (conceptually):

```python
@shared_task(bind=True)
def parse_data_file(self, data_file_id: int, reparse_id: int | None = None):
    logger = get_task_logger(__name__)
    service = ParsingService(logger=logger)

    reparse_meta = None
    if reparse_id is not None:
        reparse_meta = ReparseMeta.objects.get(pk=reparse_id)

    service.parse_data_file(data_file_id, reparse_meta=reparse_meta)
```

This keeps Celery wiring and logging but moves domain logic into the service.


### 4.3 Refactor reparsing orchestration to call the same service

Refactor `tdpservice/search_indexes/reparse.py` and `search_indexes/utils.py` so that they:

1. Determine **which DataFiles** should be reparsed (by fiscal year, quarter, program type, STT, etc.)
2. Perform backup operations (if needed)
3. Clean out associated records (ParserError, summaries, index rows) in a coherent, batched way
4. For each file, create/update `ReparseFileMeta`
5. Schedule the Celery task **without duplicating parsing logic**

The Celery task, in turn, always calls `ParsingService`. This ensures:

- All parsing behavior (record counts, error report generation, DataFile status transitions) is implemented in one place.
- Changes to parser behavior automatically apply to both initial parsing and reparsing.


### 4.4 Centralize ReparseMeta / ReparseFileMeta state transitions

Move logic that mutates `ReparseMeta` / `ReparseFileMeta` into:

- Methods on `ParsingService`, or
- Small helper functions that are **only** called by `ParsingService` and the reparse orchestration.

For example:

```python
class ParsingService:
    ...

    def _start_reparse_file(self, data_file: DataFile, reparse_meta: ReparseMeta) -> ReparseFileMeta:
        ...

    def _finish_reparse_file_success(self, file_meta: ReparseFileMeta, dfs: DataFileSummary) -> None:
        ...

    def _finish_reparse_file_failure(self, file_meta: ReparseFileMeta, exc: Exception) -> None:
        ...
```

This makes state transitions explicit and easier to test, and avoids scattering them between the Celery task and reparse utilities.


### 4.5 Improve testability & observability

Once parsing and reparsing are routed through a single service class:
- **Unit tests** can exercise `ParsingService` directly using a small in-memory or test DB dataset.
- **Integration tests** can cover:
  - Initial parse of a sample file
  - Reparse run across a few files
  - Recovery from a mid-run failure
- Logging can be standardized around a single logger/context, making it easier to trace parsing results in logs or APM tooling.


## 5. Suggested Implementation Phases

To de-risk the refactor, implement in small, incremental steps:


### Phase 1 – Document & stabilize current behavior

- Capture current parsing and reparsing flows in sequence diagrams or text:
  - How `parse_data_file` is called
  - Which tables are touched and in what order
  - How ReparseMeta / ReparseFileMeta are created and updated
- Add any missing indexes or small performance improvements that are clearly safe (see separate performance tickets).


### Phase 2 – Introduce `ParsingService` without changing behavior

- Extract the body of `parse_data_file` into `ParsingService.parse_data_file`, keeping behavior identical.
- The Celery task delegates to the service, but inputs/outputs remain unchanged.
- Add tests that assert the service produces the same side effects as the existing Celery task for a small fixture.


### Phase 3 – Wire reparsing through `ParsingService`

- Refactor `search_indexes/reparse.py` and `search_indexes/utils.py` so that they:
  - Only perform backup + selection + deletion + Celey scheduling
  - Never run parsing logic directly
- Ensure that `ReparseMeta` / `ReparseFileMeta` updates are driven by `ParsingService` and not by ad-hoc logic outside the service.


### Phase 4 – Clean up and harden

- Remove now-dead code paths or duplicated logic.
- Add better failure handling and idempotency guarantees for reparse runs:
  - Safe retry behavior if a Celery worker crashes mid-run
  - Clear reporting of which files succeeded/failed in `ReparseMeta`
- Add regression tests for:
  - Incremental reparsing (subset of files, STT-specific)
  - Large batches (e.g., dozens/hundreds of files)


## 6. Expected Benefits

1. **Reduced duplication**  
   Single source of truth for parsing logic, regardless of whether it is an initial parse or a reparse.

2. **Easier reasoning and debugging**  
   Parsing behavior is concentrated in `ParsingService`; reparse orchestration just chooses “what” to parse.

3. **Better testability**  
   Service-oriented design enables targeted unit tests instead of having to go through Celery + management commands for every behavior change.

4. **Improved performance tuning**  
   Backup, deletion, and parsing steps are separated more clearly, making it easier to profile and optimize the heaviest operations.

5. **Lower operational risk**  
   A more explicit lifecycle for ReparseMeta / ReparseFileMeta, with a single place where their states are updated, makes it easier to detect and recover from partial failures.


## 7. Next Steps

1. Create tickets for:
   - Introducing `ParsingService` and refactoring the Celery task to use it
   - Refactoring reparse orchestration to depend on `ParsingService`
   - Adding tests and observability around the unified parsing pipeline
2. Implement Phase 2 first (service extraction) with strict “no behavior change” to build confidence.
3. Once stable in staging, implement the reparse refactor and validate on a controlled subset of files.



# Parsing & Reparsing Refactor – Ticket Breakdown

---

## Ticket 0 – Implement submission state machine before parser refactor

### Title
Add submission state machine with enforced transitions and auditability

### Description
Add a first-class submission lifecycle state machine to `DataFile` (or a companion model) to capture file status across upload, scanning, validation, parsing, ingest, and completion. This should land before the parser refactor to avoid churn and to give downstream changes a consistent contract for status/triage.

### Scope
- Define allowed states/transitions (uploaded → virus_scanning → validated/scan_failed → parsing → parsed_clean/parsed_with_errors → ingesting → completed/ingest_failed; cancel from any active state).
- Add a small transition helper (service or model mixin) that validates transitions and logs/audits them.
- Persist current state on `DataFile` (or a dedicated lifecycle table) and provide a migration with defaults for existing rows.
- Update existing code paths (upload, AV scan callback, header validation, parser entry, ingest completion, cancel) to call the transition helper.
- Wire logs with correlation IDs (data_file_id, reparse_id) and optional audit entries per transition.
- Provide a dry-run/guard-rail mode initially (feature flag) to enforce transitions without breaking current flows.

### Acceptance Criteria
- Illegal transitions are rejected in code (server-side), and the allowed transition map is tested.
- Existing flows update state via the helper; direct state writes are removed.
- Migration sets a sensible initial state for existing `DataFile` rows.
- Logs or audit records show each transition with who/what triggered it.
- Feature flag exists to disable enforcement if rollout needs a fallback.
- See `docs/Technical-Documentation/tech-memos/submission-state-machine.md` for the detailed state/transition map and code sketch.

## Ticket 1 – Document current parsing & reparsing flows

### Title
Document current parsing and reparsing flows for TANF data files

### Description
We need clear documentation of how parsing and reparsing currently work in `tdrs-backend` so we can refactor safely.

### Scope

**Capture the current initial parsing flow:**

- From `DataFile` upload to `parse_data_file` Celery task completion  
- Interactions with:
  - `ParserFactory` and parser classes:
    - `TanfDataReportParser`
    - `FRAParser`
    - `ProgramAuditParser`
  - `SchemaManager`, `ParserError`, `DataFileSummary`
  - `ErrorReportFactory`, emails, logging
  - Where state is stored (`DataFile.status`, summaries, error counts)
  - How retries/rollbacks are handled today (if at all)

**Capture the current reparsing flow:**

- `search_indexes/reparse.py` and `search_indexes/utils.py`
- Use of `ReparseMeta` and `ReparseFileMeta`
- Backup, deletion, re-scheduling of Celery tasks
- How timeouts/sequential execution checks are enforced
- What data is destroyed vs. recreated during a reparse run

**Also:**

- Summarize which tables are touched and in which order (high level).
- Note any implicit contracts (e.g., parser expects certain `DataFile` fields to be set).

### Deliverables

- A short architecture doc (can be added next to the memo), with:
  - Two sequence diagrams or textual step lists:
    - Initial parse of a single `DataFile`
    - A “clean and reparse” run
  - Pointers to key modules/classes involved.
  - An explicit list of current side effects (created/updated/deleted models) for both flows.

### Acceptance Criteria

- Doc is checked into the repo and linked from the new parsing/reparsing memo.
- At least one other engineer has reviewed and confirmed it matches real behavior.
- Known gaps/assumptions (if any) are called out for follow-up.

---

## Ticket 2 – Introduce `ParsingService` and refactor Celery task to use it

### Title
Introduce ParsingService and refactor parse_data_file Celery task to use it

### Description
Create a dedicated service class (`ParsingService`) that encapsulates the full lifecycle of parsing a single `DataFile`. Refactor the existing `parse_data_file` Celery task to become a thin wrapper that delegates to this service. This should be a behavior-preserving change.

### Scope

**Add a new module**, e.g. `tdpservice/parsers/service.py`, with a class:

- `ParsingService.parse_data_file(data_file_id: int, reparse_meta: ReparseMeta | None = None)`
  - Accept optional hooks for logging/metrics injection.
  - Return a simple result DTO (statuses, counts) for testing.

**Move logic from** `tdpservice/scheduling/parser_task.parse_data_file` **into the service:**

- Loading `DataFile`
- Creating `ParserFactory` instance and invoking `parser.parse_and_validate()`
- Updating `DataFileSummary` and `DataFile` status
- Generating error reports via `ErrorReportFactory`
- Handling `ReparseFileMeta` when `reparse_meta` is present
- Logging relevant events
- Preserve retry behavior / error handling semantics (exceptions vs. swallowed errors).
- Keep email/notification behavior intact.

**Refactor `parse_data_file` Celery task to:**

- Resolve `ReparseMeta` from `reparse_id` (if provided)
- Instantiate `ParsingService` and call `parse_data_file(...)`
- Not make intentional behavior changes (same side effects, same status transitions).

### Acceptance Criteria

- All existing tests for parsing pass **without changes**.
- A new unit test (or tests) exists for `ParsingService.parse_data_file` covering:
  - Successful parse of a sample file
  - Failure path (exception inside parser) resulting in the same statuses as before.
- Celery task implementation is significantly smaller and only handles:
  - Argument parsing
  - Logging setup
  - Calling the service.
- Service returns a structured result object used by tests (no reliance on logs).
- No regression in emails/notifications or `DataFileSummary` population.

---

## Ticket 3 – Refactor reparse orchestration to depend on `ParsingService`

### Title
Refactor reparse orchestration to use ParsingService for all reparses

### Description
Update the reparsing pipeline so that all actual parsing work for reparsed files goes through the new `ParsingService`. Reparse orchestration should focus on which files to process and on backup/cleanup, not on parsing internals.

### Scope

In `tdpservice/search_indexes/reparse.py` and `search_indexes/utils.py`:

- **Keep logic that:**
  - Computes which `DataFile` instances to reparse (FY, quarter, STT, program type, etc.).
  - Performs backup (`backup(...)`).
  - Deletes associated records (`delete_associated_models(...)`).
  - Creates or updates `ReparseMeta`.

- **Ensure that for each selected `DataFile`:**
  - A `ReparseFileMeta` is created or updated as appropriate.
  - The Celery `parse_data_file` task is scheduled without any duplicated parsing logic.

- **Remove or consolidate** any parsing-like logic from reparse utilities that overlaps with what `ParsingService` now does.

- Make sure `ReparseFileMeta` transitions (finished/success, counts) are driven from the service or a single helper, not scattered.
- Add guardrails: skip/mark failed if backup or deletion fails; do not silently continue.
- Add optional dry-run flag to reparse orchestration to list candidate files without executing.

### Acceptance Criteria

- Reparsing a small set of files (in a test or local environment) produces the same `ReparseMeta` / `ReparseFileMeta` outcomes as before.
- No module outside of `ParsingService` and the Celery task directly invokes parser classes for reparsing.
- Logs for a reparse run clearly show:
  - backup + deletion steps,
  - scheduling of files,
  - completion status via `ParsingService`.
- Dry-run mode (if added) lists files and planned actions without side effects.
- Failure of backup/deletion prevents scheduling and surfaces an explicit error state.

---

## Ticket 4 – Centralize and harden `ReparseMeta` / `ReparseFileMeta` state transitions

### Title
Centralize state transitions for ReparseMeta and ReparseFileMeta

### Description
Move all logic that mutates `ReparseMeta` and `ReparseFileMeta` into one cohesive place (inside `ParsingService` or dedicated helpers) so their lifecycle is explicit, testable, and easier to reason about.

### Scope

**Identify all locations that update:**

- `ReparseMeta` fields like:
  - `timeout_at`
  - `finished`
  - `success`
  - `total_num_records_initial`
  - `total_num_records_after`
- `ReparseFileMeta` fields like:
  - `finished`
  - `success`
  - `num_records_created`
  - `cat_4_errors_generated`
  - `finished_at`

**Introduce helper methods, e.g.:**

- `ParsingService._start_reparse_file(...)`
- `ParsingService._finish_reparse_file_success(...)`
- `ParsingService._finish_reparse_file_failure(...)`

**Ensure all existing callers** (Celery task, reparse utilities) use these helpers instead of mutating models directly.

Make sure state transitions support “resume” semantics where possible (e.g., if a reparse run is partially complete).
- Add simple transition validation (e.g., prevent finishing twice) and log when transitions are no-ops due to current state.
- Optionally add an audit trail table or log line per transition for observability.

### Acceptance Criteria

- All `ReparseMeta` / `ReparseFileMeta` updates flow through the new helper methods/service methods.
- There are unit tests that:
  - Start a reparse run.
  - Simulate a successful file parse and confirm `ReparseFileMeta` fields are updated correctly.
  - Simulate a failed file parse and confirm failure state.
- Code that directly writes to `ReparseMeta` / `ReparseFileMeta` fields has been removed or replaced by the helpers.
- Transition validation prevents illegal state changes and is covered by tests.
- Optional audit logging demonstrates at least one recorded transition per parse in tests/logs.

---

## Ticket 5 – Add tests & minimal metrics/observability for parsing pipeline

### Title
Add tests and minimal observability for unified parsing & reparsing pipeline

### Description
After consolidating parsing and reparsing into `ParsingService`, we need coverage and basic observability to ensure the refactor doesn’t regress behavior and to make production issues easier to debug.

### Scope

**Tests:**

- Add unit tests for:
  - Initial parsing of a valid file (happy path).
  - Parsing of an invalid file (error generation, statuses).
  - Reparsing a file in the context of a `ReparseMeta` / `ReparseFileMeta`.
  - State machine transitions (if implemented) for submission lifecycle.

- Add at least one integration test (possibly Django test + Celery eager mode) that:
  - Runs a mini “clean and reparse” on a small fixture dataset.
  - Asserts that `ReparseMeta.is_finished` and `ReparseMeta.is_success` behave as expected.
  - Confirms `DataFileSummary` and `ParserError` counts match expectations.

**Observability:**

- Ensure key logs include:
  - `DataFile` IDs being parsed.
  - Whether the run is an initial parse or associated with a specific `ReparseMeta` ID.
  - Summary of record counts and error counts for each file.
- (Optional) Add a simple metric or log line summarizing a full reparse run (total files, successes, failures).
- Add correlation IDs per parse (data_file_id, reparse_id) to all logs.
- Consider a lightweight counter/metric (Django logging or StatsD if available) for parse duration and error count.

### Acceptance Criteria

- New tests pass in CI and are stable (not flaky).
- When running a reparse in a non-prod environment, logs clearly show:
  - Start and end of the run
  - File-level outcomes
- On failure, the system surfaces enough info (via logs and `ReparseMeta`) to debug which file(s) failed and why.
- Metrics/logs include correlation IDs and basic duration/error counts (if metrics implemented).

## Submission State Machine — Implementation Notes and Examples

### States
`uploaded` → `virus_scanning` → (`scan_failed` | `validated`) → `parsing` → (`parsed_with_errors` | `parsed_clean`) → `ingesting` → (`ingest_failed` | `completed`). Any active state can transition to `canceled`.

### Minimal implementation sketch

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable

class SubmissionState(str, Enum):
    UPLOADED = "uploaded"
    VIRUS_SCANNING = "virus_scanning"
    SCAN_FAILED = "scan_failed"
    VALIDATED = "validated"
    PARSING = "parsing"
    PARSED_WITH_ERRORS = "parsed_with_errors"
    PARSED_CLEAN = "parsed_clean"
    INGESTING = "ingesting"
    INGEST_FAILED = "ingest_failed"
    COMPLETED = "completed"
    CANCELED = "canceled"

ALLOWED_TRANSITIONS: Dict[SubmissionState, Iterable[SubmissionState]] = {
    SubmissionState.UPLOADED: {SubmissionState.VIRUS_SCANNING, SubmissionState.CANCELED},
    SubmissionState.VIRUS_SCANNING: {
        SubmissionState.SCAN_FAILED,
        SubmissionState.VALIDATED,
        SubmissionState.CANCELED,
    },
    SubmissionState.SCAN_FAILED: {SubmissionState.CANCELED},
    SubmissionState.VALIDATED: {SubmissionState.PARSING, SubmissionState.CANCELED},
    SubmissionState.PARSING: {
        SubmissionState.PARSED_WITH_ERRORS,
        SubmissionState.PARSED_CLEAN,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSED_WITH_ERRORS: {SubmissionState.INGESTING, SubmissionState.CANCELED},
    SubmissionState.PARSED_CLEAN: {SubmissionState.INGESTING, SubmissionState.CANCELED},
    SubmissionState.INGESTING: {
        SubmissionState.INGEST_FAILED,
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.INGEST_FAILED: {SubmissionState.CANCELED},
    SubmissionState.COMPLETED: set(),
    SubmissionState.CANCELED: set(),
}

class InvalidTransition(Exception):
    ...

@dataclass
class SubmissionLifecycle:
    state: SubmissionState
    history: list[str] = field(default_factory=list)

    def transition(self, next_state: SubmissionState, note: str = "") -> None:
        if next_state not in ALLOWED_TRANSITIONS[self.state]:
            raise InvalidTransition(f"{self.state} → {next_state} not allowed")
        self.history.append(f"{self.state} -> {next_state}: {note}")
        self.state = next_state
```

### Transition helpers (examples for each step)

```python
def on_upload(lifecycle: SubmissionLifecycle):
    lifecycle.transition(SubmissionState.VIRUS_SCANNING, "file accepted; queued for AV")

def on_scan_complete(lifecycle: SubmissionLifecycle, clean: bool):
    lifecycle.transition(
        SubmissionState.VALIDATED if clean else SubmissionState.SCAN_FAILED,
        "scan pass" if clean else "scan flagged",
    )

def on_header_validated(lifecycle: SubmissionLifecycle):
    lifecycle.transition(SubmissionState.PARSING, "header/pre-parse checks passed")

def on_parsing_finished(lifecycle: SubmissionLifecycle, has_errors: bool):
    lifecycle.transition(
        SubmissionState.PARSED_WITH_ERRORS if has_errors else SubmissionState.PARSED_CLEAN,
        "parse finished with errors" if has_errors else "parse finished clean",
    )

def on_ingest_start(lifecycle: SubmissionLifecycle):
    lifecycle.transition(SubmissionState.INGESTING, "begin persisting records/errors")

def on_ingest_finish(lifecycle: SubmissionLifecycle, ok: bool):
    lifecycle.transition(
        SubmissionState.COMPLETED if ok else SubmissionState.INGEST_FAILED,
        "ingest success" if ok else "ingest failure",
    )

def on_cancel(lifecycle: SubmissionLifecycle, reason: str = ""):
    # Allow cancel from any non-terminal state
    if lifecycle.state not in {SubmissionState.COMPLETED, SubmissionState.CANCELED}:
        lifecycle.state = SubmissionState.CANCELED
        lifecycle.history.append(f"canceled from {lifecycle.state}: {reason}")
```

### Integrating with Django models

```python
from django.db import transaction
from tdpservice.data_files.models import DataFile

def transition_datafile(data_file: DataFile, next_state: SubmissionState, note: str = ""):
    with transaction.atomic():
        lifecycle = SubmissionLifecycle(SubmissionState(data_file.state))
        lifecycle.transition(next_state, note)
        data_file.state = lifecycle.state.value
        data_file.save(update_fields=["state"])
        # Optionally persist history to an audit table
```

### Guardrails
- Enforce transitions server-side (do not trust client-side state).
- Use atomic transactions when persisting state changes plus side effects (e.g., enqueue parsing).
- Log state changes with correlation IDs (data file ID, reparse ID) for triage.
- Consider feature-flagging transition enforcement initially to ease rollout.

---

## Appendix: Class-Based Parser Restructure Notes (from original memo)

### Summary and Goals
- Refactor the parsing engine from functional to class-based to improve adherence to SOLID principles and extensibility.
- Decouple parsing from file formats via decoder abstraction and a parser factory.
- Keep the parser-task interface stable while enabling FRA and future file types.
- Out of scope: FRA concrete parsing logic (lives in `RowSchema`/`Field`), multi-row records, FRA-specific schema migrations.

### SchemaManager responsibilities
- Initialize and cache all `RowSchema`s for the file’s program type/section.
- Provide a single `parse_and_validate` entry that routes to schemas by record type.
- Manage encryption flags per file up front.
- Offer setup/teardown hooks to avoid mid-parse mutation.

### Decoder considerations
- Stream rows (don’t load whole files); normalize newlines once.
- Surface decoding failures with row/file context; fail fast on unknown extensions.
- Proposed decoders: UTF-8, CSV, XLSX with `RawRow`/`Position` helpers and `DecoderFactory` detection (e.g., `puremagic`, `chardet`).

### Parser interface templates
- `BaseParser` encapsulates shared parsing utilities and initializes `SchemaManager` and decoder.
- Concrete parsers (TANF/SSP/Tribal, FRA) implement `parse_and_validate`, header/trailer checks, and category validations while reusing base utilities.
- `ParserFactory` selects the correct parser class/instance by program type for use in `parser_task.py`.

### Implementation Plan (class-based parser work)
1. Rewrite `SchemaManager` to be context-aware (program type/section) with cached schemas and encryption updates; add routing tests.
2. Add decoder layer (`RawRow`, decoders, `DecoderFactory`) and gate into current TANF/SSP/Tribal path behind a feature flag; verify streaming on large samples.
3. Introduce `BaseParser` and port shared functions from `parse.py`; keep external task signature unchanged.
4. Move remaining TANF/SSP/Tribal logic into `TanfSspTribalParser`; ensure header/trailer parity; migrate tests to the class API.
5. Adopt `ParserFactory` in `parser_task.py`; add factory tests and end-to-end smoke tests.
6. Enable FRA by stubbing `FRAParser` with decoders and schemas; add fixtures and contract tests.

### Risks and decisions
- Confirm single-row-per-record assumption for FRA; adjust decoder/`RawRow` contract if not.
- Approve dependencies (`puremagic`, `chardet`, `openpyxl`) or choose alternatives.
- Assess XLSX performance (streaming vs in-memory).
- Decide on feature flag/rollback strategy during rollout.

### Validator improvement tickets
1. Fix `isOneOf` mutation/range handling; build immutable option sets and add reuse/range tests.
2. Improve validator logging/telemetry with validator name, value, and field context; test exception paths.
3. Wrap legacy pre-parse validators with decorator plumbing for deprecation/flagging; update call sites and add tests.
4. Normalize composite validators (`Result` usage, SSN helpers) to short-circuit cleanly with predictable messages; add tests and avoid double-logging.
