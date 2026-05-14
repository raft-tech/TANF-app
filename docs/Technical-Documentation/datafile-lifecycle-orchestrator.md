# Technical Memo: DataFile Lifecycle Orchestrator

**Date:** 2026-05-12  
**Status:** Draft — For Review  
**Authors:** Engineering Team  
**Reviewers:** Tech Lead, Backend Lead  
**Related Issues:** #5735, #5756

---

## 1. Executive Summary

### PM/UX/OFA Value

A submitted TANF/Tribal/FRA data file goes through up to nine distinct states — from initial upload through virus scan, parsing, and final acceptance — before OFA analysts see a result. When a transition silently fails, or the same transition logic is applied differently across submission, re-parsing, and scan error paths, the file can end up in a permanently incorrect state with no audit trail and no user-facing signal. This work creates a single, well-tested orchestration layer so that every DataFile state change is validated, logged, and deterministic regardless of which code path triggered it.

For data analysts and OFA staff: fewer unexplained "stuck" or stale-state files, consistent error visibility in the UI, and reliable email notifications on reparse completion.

For the engineering team: one canonical place to add new transitions, one set of regression tests to cover the entire lifecycle, and a clear separation between "what should happen next" (orchestrator) and "how the work is done" (worker tasks).

---

## 2. Background

### 2.1 Current Architecture Overview

The `DataFile` model carries a `state` field governed by `SubmissionState` (`enums.py`). The low-level primitive — `transition_datafile()` in `submission_lifecycle.py` — validates the requested transition against `ALLOWED_TRANSITIONS`, persists the new state, and logs it. This primitive is sound.

The problem is that **nothing above that primitive coordinates the full workflow.** Transition calls are scattered across four separate modules:

| Module | Transitions issued |
|---|---|
| `data_files/views.py` (`DataFileViewSet.create`) | `UPLOADED → VIRUS_SCAN_STARTED`, `VIRUS_SCAN_STARTED → VIRUS_SCAN_FAILED`, `VIRUS_SCAN_STARTED → VIRUS_SCAN_COMPLETED` |
| `scheduling/parser_task.py` (`parse` Celery task) | `→ PARSE_STARTED`, `→ PARSE_FAILED`, `→ PARSED_WITH_ERRORS`, `→ PARSE_COMPLETED` |
| `scheduling/parser_task.py` (`_transition_parse_outcome`) | `→ PARSE_COMPLETED`, `→ PARSED_WITH_ERRORS`, `→ PARSE_FAILED` |
| `search_indexes/reparse.py` (`handle_datafiles`) | queues `parse.delay()` with `reparse_id` but does **not** reset DataFile state first |
| Go parser worker (`celery.go`) | Writes `"Rejected"` to `DataFileSummary.status` on failure/panic; writes nothing on success path (bug #5735) |

No module owns the decision of what happens _between_ steps. `views.py` decides when to call `parse.delay()`. `reparse.py` decides when to call `parse.delay()` again. The Go worker decides when (or whether) to write shadow-state. These decisions are made locally with no shared policy.

### 2.2 Pain Points

1. **No canonical entry point for "start a parse."** Both `views.py` and `reparse.py` call `parse.delay()` directly. Any new call site must re-implement the same pre-conditions.

2. **No production code dispatches the Go parser.** The Go parser worker is registered and listens on the `go-parser` queue for the `go_parse` Celery task, but nothing in `views.py`, `reparse.py`, or `parser_task.py` calls `go_parse.delay()`. Adding dual dispatch to `enqueue_parse()` would be new behavior, not a consolidation of existing logic, and requires an explicit decision about the Go parser's integration mode (OQ-8).

3. **Reparse re-entry is underdocumented.** `handle_datafiles()` calls `parse.delay()` on a file that may be in `PARSE_COMPLETED`, `PARSED_WITH_ERRORS`, or `PARSE_FAILED`. The `ALLOWED_TRANSITIONS` map does allow those states to re-enter `PARSE_STARTED`, but callers must know which states are re-entrant. There is no guard that prevents `handle_datafiles()` from queuing a file that is currently in `PARSE_STARTED` (concurrent re-entry), which would cause the second task's `record_parse_started()` call to raise `InvalidTransition`.

4. **The Go parser has no success-path status write.** `celery.go:processTask()` calls `updateDataFileSummaryStatus(ctx, id, "Rejected")` on failure and on panic, but returns `nil` on success without writing any status to `DataFileSummary`. This is the bug from #5735. There is no retry hook if the status write itself fails.

5. **No single audit log for a complete file lifecycle.** Individual transitions are logged, but there is no structured event stream that shows: upload received → scan started → scan passed → parse queued → parse started → ... → completed.

6. **Testing coverage is fragmented.** Unit tests for `parse()` do not exercise the interaction with `views.create()`; tests for `reparse.py` do not exercise the scan states. No integration test drives a file from upload to terminal state.

---

## 3. Target Architecture

### 3.1 Proposed Module Layout

```
tdpservice/
  data_files/
    orchestration/
      __init__.py
      orchestrator.py       ← DataFileOrchestrator class
      events.py             ← LifecycleEvent dataclass + audit log writer
  scheduling/
    parser_task.py          ← unchanged except: replaces direct transition_datafile
                               calls with orchestrator.record_parse_outcome()
  data_files/
    views.py                ← replaces direct calls with orchestrator.submit()
  search_indexes/
    reparse.py              ← replaces parse.delay() with orchestrator.enqueue_reparse()
```

The `DataFileOrchestrator` is a **stateless service object** — it carries no instance state beyond the `DataFile` it was constructed with. Constructing a new orchestrator for each operation is safe; there is no shared mutable state between calls.

### 3.2 DataFileOrchestrator Interface

```python
class DataFileOrchestrator:
    """Coordinates all lifecycle transitions and task dispatch for a single DataFile."""

    def __init__(self, data_file: DataFile) -> None: ...

    # --- Submission path ---
    def begin_scan(self) -> None:
        """UPLOADED → VIRUS_SCAN_STARTED. Call before dispatching ClamAV."""

    def record_scan_failure(self, reason: str) -> None:
        """VIRUS_SCAN_STARTED → VIRUS_SCAN_FAILED. Do not enqueue parse."""

    def record_scan_success(self) -> None:
        """VIRUS_SCAN_STARTED → VIRUS_SCAN_COMPLETED. Persists file to storage."""

    def enqueue_parse(self) -> None:
        """VIRUS_SCAN_COMPLETED → (no state change). Currently dispatches parse.delay()
        to the Python parser queue only — this matches existing production behavior.
        Optionally dispatches go_parse.delay() to the Go parser queue, but this is
        PROPOSED NEW BEHAVIOR contingent on resolution of OQ-8 (Go integration mode).
        If both are dispatched, both write to the same DataFileSummary row; the
        last write wins and must be governed by an explicit concurrency policy.
        Raises InvalidTransition if current state is not VIRUS_SCAN_COMPLETED."""

    # --- Parse task path ---
    def record_parse_started(self) -> None:
        """→ PARSE_STARTED. Valid from VIRUS_SCAN_COMPLETED, PARSE_FAILED,
        PARSE_COMPLETED, PARSED_WITH_ERRORS (reparse re-entry)."""

    def record_parse_outcome(self, dfs: DataFileSummary) -> None:
        """PARSE_STARTED → PARSE_COMPLETED | PARSED_WITH_ERRORS | PARSE_FAILED.
        Determines target state from dfs.status."""

    def record_parse_failure(self, note: str) -> None:
        """PARSE_STARTED → PARSE_FAILED. Called by exception handlers."""

    def finalize(self) -> None:
        """PARSE_COMPLETED | PARSED_WITH_ERRORS → COMPLETED.
        Called after all artifacts are written."""

    # --- Reparse path ---
    def enqueue_reparse(
        self,
        meta_model: ReparseMeta,
        previous_summary_status: str | None = None,
    ) -> None:
        """Validate re-entry, create ReparseFileMeta (with previous_summary_status),
        dispatch parse.delay(). Valid from PARSE_COMPLETED, PARSED_WITH_ERRORS,
        PARSE_FAILED. Raises InvalidTransition from COMPLETED, CANCELED, PARSE_STARTED.
        Does NOT reset state — PARSE_STARTED transition is applied inside the task."""

    # --- Utility ---
    def mark_stuck(self, reason: str) -> None:
        """→ STUCK. Used by monitoring/timeout tasks."""

    def cancel(self, reason: str) -> None:
        """→ CANCELED. Admin-initiated cancellations only."""
```

All state-transition methods (`begin_scan`, `record_scan_failure`, `record_scan_success`, `record_parse_started`, `record_parse_outcome`, `record_parse_failure`, `finalize`, `mark_stuck`, `cancel`) call `transition_datafile()` internally and do not expose the raw `SubmissionState` enum to callers.

Go parser result handling sits outside `DataFileOrchestrator` because it does not change `DataFile.state` — it only updates `DataFileSummary.status`. It is implemented as a standalone helper:

```python
def record_go_parse_outcome(data_file_id: int, status: str) -> None:
    """Write the Go parser's final DataFileSummary status directly.
    Does not call transition_datafile(); DataFile.state is not changed.
    Fixes the success-path gap in celery.go (processTask returns nil
    without writing any status). Pending resolution of OQ-8."""
```

---

## 4. State Model

### 4.1 States

| State | Meaning | Terminal? |
|---|---|---|
| `UPLOADED` | Model row created, no file in storage | No |
| `VIRUS_SCAN_STARTED` | ClamAV scan dispatched | No |
| `VIRUS_SCAN_FAILED` | File rejected by scanner or scanner unavailable | Soft-terminal (no parse) |
| `VIRUS_SCAN_COMPLETED` | File clean, saved to S3 | No |
| `PARSE_STARTED` | Celery `parse` task is executing | No |
| `PARSE_FAILED` | Parser exited abnormally or raised DatabaseError | Re-entrant |
| `PARSED_WITH_ERRORS` | Parser finished; some records had errors | Re-entrant |
| `PARSE_COMPLETED` | Parser finished; all records accepted | Re-entrant |
| `STUCK` | Exceeded timeout; requires manual intervention | Soft-terminal |
| `COMPLETED` | Lifecycle closed; all artifacts written | Hard-terminal |
| `CANCELED` | Admin-cancelled | Hard-terminal |

### 4.2 Allowed Transitions (complete map)

This is unchanged from the existing `ALLOWED_TRANSITIONS` dict in `submission_lifecycle.py`. The orchestrator enforces it; it does not replace it.

```
UPLOADED              → VIRUS_SCAN_STARTED, CANCELED
VIRUS_SCAN_STARTED    → VIRUS_SCAN_FAILED, VIRUS_SCAN_COMPLETED, CANCELED
VIRUS_SCAN_FAILED     → CANCELED
VIRUS_SCAN_COMPLETED  → PARSE_STARTED, CANCELED
PARSE_STARTED         → PARSE_FAILED, PARSED_WITH_ERRORS, PARSE_COMPLETED, CANCELED
PARSE_FAILED          → PARSE_STARTED, CANCELED
PARSED_WITH_ERRORS    → PARSE_STARTED, COMPLETED, CANCELED
PARSE_COMPLETED       → PARSE_STARTED, COMPLETED, CANCELED
STUCK                 → CANCELED
COMPLETED             → (none)
CANCELED              → (none)
```

### 4.3 Invalid-Transition Behavior

`transition_datafile()` already raises `InvalidTransition` (a `ValueError` subclass) on any disallowed move. The orchestrator does not suppress this exception — `InvalidTransition` always propagates to the caller.

Calling `enqueue_reparse()` on a `COMPLETED` or `CANCELED` file raises `InvalidTransition`; the reparse orchestration layer is responsible for checking terminal states before queuing.

Task-layer policy (§5.2): the Celery `parse` task is the primary caller of `record_parse_started()`. If a task runs against a file that is unexpectedly already in `PARSE_STARTED` (e.g., duplicate dispatch), `record_parse_started()` raises `InvalidTransition`. The task should catch `InvalidTransition` specifically, log it at WARNING level, and return immediately without retrying — retrying will hit the same guard on every attempt.

---

## 5. Orchestration Boundaries

### 5.1 API Layer (`views.py`)

**Responsibility:** Validate request, create the DataFile model row, run virus scan, delegate lifecycle to orchestrator.

**What it does:**
1. Validate PIA feature flag and year range (unchanged).
2. Deserialize and call `serializer.save(file=None)` to get the model row in `UPLOADED`.
3. Construct `DataFileOrchestrator(data_file)`.
4. Call `orchestrator.begin_scan()`.
5. Run `_scan_uploaded_file()`.
6. On scan failure: call `orchestrator.record_scan_failure(reason)`, return 400.
7. On scan success: persist file bytes, call `orchestrator.record_scan_success()`, then `orchestrator.enqueue_parse()`.
8. Return 201.

**What it must not do:** Issue `transition_datafile()` directly, call `parse.delay()` or `go_parse.delay()` directly.

### 5.2 Task Layer (`parser_task.py`)

**Responsibility:** Execute parsing work and report outcomes back to the orchestrator.

**What it does:**
1. Fetch `DataFile` and (if `reparse_id`) `ReparseFileMeta`.
2. Construct `DataFileOrchestrator(data_file)`.
3. Call `orchestrator.record_parse_started()`.
4. Create `DataFileSummary`, call `parser.parse_and_validate()`.
5. Call `orchestrator.record_parse_outcome(dfs)` on success.
6. On `DecoderUnknownException` / `DatabaseError` / generic `Exception`: call `orchestrator.record_parse_failure(note)`.
7. In `finally`: call `_finalize_parse()`, `_finalize_reparse()`.

**What it must not do:** Call `transition_datafile()` directly, decide which `SubmissionState` to apply, know about `ALLOWED_TRANSITIONS`.

### 5.3 Reparse Layer (`reparse.py`)

**Responsibility:** Coordinate batch reparse: backup, clean associated models, re-queue files.

**What it does:**
1. `handle_datafiles()` constructs `DataFileOrchestrator(file)` per file.
2. Calls `orchestrator.enqueue_reparse(meta_model, previous_summary_status=previous_summary_statuses.get(file.pk))`.
3. `enqueue_reparse()` internally: validates the current state is re-entrant (`PARSE_FAILED`, `PARSED_WITH_ERRORS`, `PARSE_COMPLETED`), creates `ReparseFileMeta(data_file=file, reparse_meta=meta_model, previous_summary_status=previous_summary_status)`, calls `parse.delay(file.pk, reparse_id=meta_model.pk)`.

**What it must not do:** Call `parse.delay()` directly, assume which states are re-entrant.

### 5.4 Transition Engine (`submission_lifecycle.py`)

**Responsibility:** Low-level guard: validate, persist, log a single state transition.

This module is **not changed**. `ALLOWED_TRANSITIONS`, `validate_transition()`, and `transition_datafile()` remain the authoritative source of truth for valid transitions. The orchestrator calls them; no other module should.

### 5.5 Go Parser Task Worker

**Responsibility:** Run the Go parser against the same `DataFile` as the Python parser and write a final `DataFileSummary.status` directly to the database on failure or panic.

The Go worker (`tdrs-services/parser/internal/server/celery/celery.go`) is a separate process consuming the `go-parser` Celery queue. It receives `go_parse` tasks containing a `data_file_id`. It connects to the same PostgreSQL database as Django and calls `db.UpdateDataFileSummaryStatus()` directly — there are no shadow tables; it writes to the same `DataFileSummary` row as the Python parser.

Current behavior:
- **Failure / panic:** calls `updateDataFileSummaryStatus(ctx, id, "Rejected")`.
- **Success:** returns `nil` from `processTask()` without writing any status — this is the bug from #5735.

**Blocking bug from #5735:** `processTask()` (`celery.go` approximately lines 223–229, the success branch after `RunPipeline` returns nil) exits without calling `updateDataFileSummaryStatus`. A thin Python Celery result task (or a direct Go DB call) should invoke `record_go_parse_outcome(data_file_id, status)` on success, providing the canonical fix without touching the primary Python parse path.

**Race condition:** Both the Python parser (`parser_task.py`) and the Go worker write to the same `DataFileSummary` row. If both tasks run concurrently, the last write wins on `status`, `case_aggregates`, and `error_report`. The correct concurrency policy — whether Go writes are authoritative, advisory, or scoped to non-overlapping file types — must be defined in OQ-8 before dual dispatch is enabled.

**What it must not do:** issue Django `transition_datafile()` calls or update `DataFile.state` — DataFile state is owned by the Python orchestrator.

---

## 6. Error Handling Semantics

### 6.1 Virus Scan Failures

| Scenario | Current behavior | Orchestrator behavior |
|---|---|---|
| Scanner unavailable (`ServiceUnavailable`) | Transitions to `VIRUS_SCAN_FAILED`, returns 400 | Same. `record_scan_failure("scanner unavailable")` |
| File infected | Transitions to `VIRUS_SCAN_FAILED`, returns 400 | Same. `record_scan_failure("file failed security inspection")` |

Both cases produce a `VIRUS_SCAN_FAILED` DataFile. This is correct — the DataFile row persists for audit visibility even though no file was stored.

### 6.2 Parse Failures

| Exception | Note passed | Next state |
|---|---|---|
| `DecoderUnknownException` | `"decoder unknown exception"` | `PARSE_FAILED` |
| `DatabaseError` | `"database error during parsing"` | `PARSE_FAILED` |
| Any other `Exception` (dfs exists) | `"unexpected error during parsing"` | `PARSE_FAILED` |
| Any other `Exception` (dfs is None) | Re-raised, Celery marks task FAILED | State not changed (file remains in `PARSE_STARTED`) |

The last case (dfs is None) is a gap. If the `DataFileSummary.objects.create()` call raises before `dfs` is assigned, the task re-raises and Celery retries it. On retry, the file is still in `PARSE_STARTED`, which is not in `ALLOWED_TRANSITIONS[PARSE_STARTED]` — so the retry's `record_parse_started()` call will raise `InvalidTransition`. 

**Recommended fix (Phase 2):** Move `DataFileSummary.objects.create()` before the `PARSE_STARTED` transition, or catch `DatabaseError` in the create path and call `record_parse_failure()` before re-raising. This ensures the file never strands in `PARSE_STARTED` across a retry.

### 6.3 Database Errors During Transition

`transition_datafile()` calls `data_file.save(update_fields=["state"])`. If this `save()` raises `DatabaseError`, the in-memory `data_file.state` has already been updated but the DB has not. The orchestrator should wrap the call in a try/except that reverts `data_file.state` to its previous value (captured before the call) and re-raises. This can be implemented as a context manager:

```python
@contextmanager
def _safe_transition(data_file, next_state, note):
    prev = data_file.state
    try:
        yield transition_datafile(data_file, next_state, note)
    except DatabaseError:
        data_file.state = prev  # revert in-memory state
        raise
```

### 6.4 Unexpected Exceptions in Orchestrator Methods

Orchestrator methods should not swallow exceptions. Any exception from `transition_datafile()` propagates to the caller. The caller (task or view) is responsible for logging and for deciding whether to retry. The orchestrator logs the intent (before the call) at DEBUG level; the exception itself is logged by the caller.

---

## 7. Logging, Observability, and Audit

### 7.1 Structured Transition Log (existing)

`transition_datafile()` already emits a structured log entry:
```json
{
  "data_file_id": 42,
  "previous_state": "parse_started",
  "next_state": "parse_failed",
  "note": "database error during parsing"
}
```
This is the per-transition audit record. It is sufficient for individual transitions.

### 7.2 Lifecycle Event Stream (new)

Add a `LifecycleEvent` dataclass written to a new `DataFileLifecycleEvent` model (or, if a new table is undesirable in Phase 1, to a structured log key `datafile.lifecycle_event`):

```python
@dataclass
class LifecycleEvent:
    data_file_id: int
    reparse_id: int | None
    event_type: str          # "submit", "scan_start", "scan_pass", "scan_fail",
                             # "parse_queue", "parse_start", "parse_outcome",
                             # "parse_fail", "finalize", "reparse_queue"
    previous_state: str
    next_state: str
    actor: str               # "api", "celery_parse", "celery_go", "admin"
    note: str
    occurred_at: datetime
```

This gives a per-file, time-ordered event log that can be used to:
- Diagnose "stuck" files without reading raw celery logs.
- Feed a future admin UI timeline view.
- Serve as the audit trail required for compliance.

### 7.3 Metrics

Each orchestrator method should emit a counter metric:
- `datafile.transition.total{from_state, to_state, actor}` — count of successful transitions.
- `datafile.transition.invalid{from_state, attempted_to_state}` — count of `InvalidTransition` raises.
- `datafile.parse.duration{program_type, section}` — histogram from `PARSE_STARTED` to outcome.

### 7.4 Alerting

- Alert on `datafile.transition.invalid` spike — indicates a code path calling transitions out of order.
- Alert on files in `PARSE_STARTED` for > 30 minutes (timeout threshold) — drives the `mark_stuck()` workflow.
- Alert on files in `VIRUS_SCAN_STARTED` for > 5 minutes without resolution — scanner may be down.

---

## 8. Migration Approach

Migration is split into four phases to allow incremental rollout with no flag-day cutover.

### Phase 1 — Introduce the orchestrator module (no behavior change)

**Effort:** 2–3 engineer-days  
**Dependencies:** None  
**Risk:** Low

1. Create `tdpservice/data_files/orchestration/orchestrator.py`.
2. Implement all methods as thin wrappers over the existing `transition_datafile()` and `parse.delay()` calls — exactly what the scattered call sites do today, consolidated in one class.
3. Add unit tests for the orchestrator using mocks. No integration paths changed yet.
4. No existing call sites are modified.

**Validation:** Unit tests pass. No runtime behavior changes.

### Phase 2 — Migrate `views.py` to use orchestrator

**Effort:** 1 engineer-day  
**Dependencies:** Phase 1  
**Risk:** Low (covered by existing view tests + manual QA)

1. Replace the five direct `transition_datafile()` / `parse.delay()` calls in `DataFileViewSet.create()` with orchestrator calls.
2. Do **not** add `go_parse.delay()` dispatch yet — no such call exists in production and adding it is gated on OQ-8 resolution. `enqueue_parse()` dispatches only `parse.delay()` in this phase.
3. Update view tests to assert on orchestrator mock calls rather than `transition_datafile` mock calls.

**Validation:** All existing view tests pass. Manual end-to-end upload in staging environment.

### Phase 3 — Migrate `parser_task.py` to use orchestrator

**Effort:** 2 engineer-days  
**Dependencies:** Phase 2  
**Risk:** Medium (core parse path; requires careful regression)

1. Replace direct `transition_datafile()` calls in `parse()`, `_transition_parse_outcome()`, `_handle_parse_failure()` with orchestrator calls.
2. Address the dfs-is-None gap described in §6.2.
3. Update `parser_task` tests to assert on orchestrator mock calls.

**Validation:** Full parser test suite passes. End-to-end parse of a sample TANF file in staging.

### Phase 4 — Migrate `reparse.py` and fix Go parser success path

**Effort:** 3 engineer-days  
**Dependencies:** Phase 3  
**Risk:** Medium (reparse is admin-triggered; lower traffic but higher blast radius)

1. Replace `parse.delay()` in `handle_datafiles()` with `orchestrator.enqueue_reparse(meta_model, previous_summary_status)`.
2. Add re-entry guard inside `enqueue_reparse()`: raise `InvalidTransition` if the file is in `COMPLETED`, `CANCELED`, or `PARSE_STARTED`; proceed for `PARSE_FAILED`, `PARSED_WITH_ERRORS`, `PARSE_COMPLETED`.
3. Add `record_go_parse_outcome()` call in the Go worker success path (thin Python Celery result task or direct Go DB call) to fix #5735 success-path gap.
4. Add `LifecycleEvent` model and wire up event writes throughout the orchestrator (can be deferred to a 4b sub-phase).

**Validation:** End-to-end reparse of a single file in staging. Go parser queue enabled in staging; verify `DataFileSummary.status` is written on both success and failure paths.

---

## 9. Testing Strategy

### 9.1 Unit Tests — Orchestrator

- **Happy-path:** Each method transitions from the correct pre-condition state to the correct target state.
- **Guard:** Each method raises `InvalidTransition` when called from an invalid pre-condition state. (E.g., `record_scan_success()` called when already `VIRUS_SCAN_COMPLETED`.)
- **DatabaseError in save:** `_safe_transition` context manager reverts in-memory state and re-raises.
- **Go dispatch:** `enqueue_parse()` calls both `parse.delay()` and `go_parse.delay()`; verify both are enqueued and each targets the correct queue name.
- **Re-entrant reparse:** `enqueue_reparse()` succeeds from `PARSE_COMPLETED`, `PARSED_WITH_ERRORS`, `PARSE_FAILED`; raises `InvalidTransition` from `COMPLETED` and `CANCELED`.

### 9.2 Integration Tests — Upload Path

Using `pytest` + Django test client + mocked ClamAV and Celery:

1. Upload a clean file → expect `DataFile.state == VIRUS_SCAN_COMPLETED` (before parse task runs) and `parse.delay()` called once.
2. Upload an infected file → expect `DataFile.state == VIRUS_SCAN_FAILED`, no `parse.delay()`.
3. Upload with scanner unavailable → expect `VIRUS_SCAN_FAILED`, 400 response.

### 9.3 Integration Tests — Parse Task Path

Using `pytest` + real parser with minimal fixture files:

1. Parse a valid file → `DataFile.state` transitions `UPLOADED → ... → PARSE_COMPLETED` or `PARSED_WITH_ERRORS`.
2. Parse a completely invalid file → `DataFile.state == PARSE_FAILED`.
3. Parse raises `DatabaseError` → `PARSE_FAILED`, `ReparseFileMeta.success == False` (if reparse).
4. Parse task called with file in wrong state → `InvalidTransition` raised, task returns without retry.

### 9.4 Integration Tests — Reparse Path

1. `enqueue_reparse()` on a `PARSE_COMPLETED` file → `ReparseFileMeta` created, `parse.delay()` queued.
2. `enqueue_reparse()` on a `COMPLETED` file → `InvalidTransition` raised, nothing queued.
3. Full reparse cycle: clean → queue → start → outcome → finalize.

### 9.5 Regression Coverage

Before each phase ships to production:

- [ ] Full backend test suite (`pytest tdpservice/`) passes with no new failures.
- [ ] Existing test for `test_submit_data_file_valid` passes.
- [ ] Existing test for `test_reparse_files` passes.
- [ ] Staging smoke: upload one TANF Active Case file, verify it reaches `PARSE_COMPLETED` or `PARSED_WITH_ERRORS` in Django admin.
- [ ] Staging smoke (after Phase 4): trigger single-file reparse via management command, verify file cycles to `COMPLETED`.

---

## 10. Open Questions and Owner Assignments

| # | Question | Owner | Target Resolution |
|---|---|---|---|
| OQ-1 | Should `LifecycleEvent` be a DB model or a structured log key? A DB model supports future admin UI timelines but adds a migration and a write on every transition. | Backend Lead + PM | Phase 1 planning |
| OQ-2 | Should `COMPLETED` be reachable from `PARSED_WITH_ERRORS` directly (current), or only via an explicit analyst review action? | PM + OFA | Before Phase 3 |
| OQ-3 | What is the correct `finalize()` trigger? Currently there is no explicit `→ COMPLETED` call in the codebase. `PARSE_COMPLETED` and `PARSED_WITH_ERRORS` are both treated as terminal in the UI. The orchestrator's `finalize()` method needs a caller. | Engineering + PM | Phase 3 design |
| OQ-4 | Go parser success-path result delivery: should `record_go_parse_outcome()` be invoked by a thin Python Celery result-callback task, or should `celery.go` call `updateDataFileSummaryStatus` directly before returning? The choice affects whether Go ever needs to know Django's status string vocabulary. | Backend + Go team | Phase 4 planning |
| OQ-5 | Timeout / `STUCK` automation: what process monitors `PARSE_STARTED` age and calls `mark_stuck()`? Celery beat task? Health check? | Engineering | Phase 4 |
| OQ-6 | Status string mismatch between Go worker (`"Partially Accepted"`) and Django (`"Partially Accepted with Errors"`) (#5735). Which is canonical? Fix must be coordinated across both repos before `record_go_parse_outcome()` is wired up. | Backend + Go team | Before Phase 4 |
| OQ-7 | Should `VIRUS_SCAN_FAILED` be re-entrant? Currently there is no path from `VIRUS_SCAN_FAILED → VIRUS_SCAN_STARTED`. If OFA wants to allow a re-upload without creating a new DataFile, the transition map needs to change. | PM + OFA | Phase 1 planning |
| OQ-8 | What is the Go parser's integration mode? Options: (a) **canary** — both parsers run concurrently, Python result is authoritative; (b) **replacement** — Go replaces Python for supported file types, Python does not run; (c) **comparison** — both run, results are diffed, neither is authoritative. This decision determines whether `go_parse.delay()` is dispatched from `enqueue_parse()`, which queue owns `DataFileSummary` writes, and how the race condition between the two workers is resolved. Currently no production code dispatches `go_parse.delay()`. | Backend + Go team + PM | Before Phase 2 |

---

## 11. Acceptance Criteria

- [ ] Memo covers the parse orchestration path end-to-end (upload → scan → enqueue → parse → outcome → finalize).
- [ ] Memo covers the reparse orchestration path end-to-end (admin trigger → clean → enqueue_reparse → parse → outcome → finalize).
- [ ] Memo defines all valid transitions and specifies that `InvalidTransition` is raised on any invalid move, with no suppression in the orchestrator.
- [ ] Memo includes four implementation phases with effort estimates and inter-phase dependencies.
- [ ] Memo captures seven open questions with assigned owners and target resolution points.
- [ ] Testing checklist in §9.5 is complete before each phase ships.

---

*End of memo.*
