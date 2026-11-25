# Automated Testing & Layer Ownership Guide

How coding agents and developers should choose the right test layer, avoid redundant cross-layer coverage, and author tests in `pytest`, `go test`, `Jest`, and `Cypress`.

## 1. Layer Ownership Decision Matrix

Before writing or modifying a test, select the **lowest, fastest test layer** capable of verifying the behavior:

| Test Layer | Runner & Location | What MUST Be Tested Here | What MUST NOT Be Tested Here (Anti-Patterns) | External Dependencies & Mocking Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **1. Backend Unit & API Integration (`pytest`)** | `pytest` under `tdrs-backend/tdpservice/**/test/` (`task backend-pytest`) | • **Model invariants & methods**: Custom `.save()`, constraints, state transitions (`SubmissionLifecycle`), querysets.<br>• **Serializer & Validator logic**: Field validation, header/filename prechecks, error payloads (instantiate serializer directly without HTTP when possible).<br>• **DRF ViewSet contracts & RBAC**: Status codes, response payloads, object-level STT/region filtering, and permission boundaries.<br>• **Celery tasks & service classes**: Task orchestration, retry/error handling, Keycloak sync logic, S3 path generation. | • **Do NOT** test every validation permutation through the full HTTP `APIClient` + multipart file upload stack if a direct serializer/validator unit test covers it.<br>• **Do NOT** parametrize RBAC tests across all 7+ roles when 3 boundary cases suffice (**1 permitted role**, **1 denied authenticated role**, **1 unauthenticated client**), unless testing a permission class's exhaustive role matrix once.<br>• **Do NOT** parse multi-thousand-record files (`big_file`, `ssp_section1_datafile`) in tests that only check task scheduling, backups, or line-1 headers.<br>• **Do NOT** test Django Admin framework built-ins unless testing custom `ModelAdmin` methods (`has_*_permission`, custom actions, `get_queryset`). | • **Database**: Real PostgreSQL test DB (`@pytest.mark.django_db`).<br>• **Storage**: Avoid unnecessary S3 uploads; only test `DataFilesS3Storage` or `S3FileHandler` directly in storage-specific tests.<br>• **External Services**: Always mock ClamAV, Keycloak Admin HTTP API (`requests`), email (`mail.outbox` or mock), and Celery `.delay()` / `.apply_async()` using `mocker.patch` at the module where they are used. |
| **2. Go Parser Unit & Integration (`go test` & `pytest`)** | `go test ./...` (`make test`) in `tdrs-services/parser/` & `tdrs-backend/tdpservice/parsers/test/integration/` (`task backend-pytest-go-integration`) | • **Go Unit (`internal/**`)**: All new TANF/SSP/Tribal/FRA record decoders, field transformers, validators, and batch writers.<br>• **Django-to-Go Integration (`test_go_parse.py`)**: Cross-service Celery dispatch (`go-parser` queue), S3 file fetch, and shared Postgres schema/summary writes. | • **Do NOT** add new schema/validator tests only to the deprecated Python parser without corresponding Go parser coverage. | • **Go Unit**: Pure in-memory structs/slices (`sqlmock` for DB helpers).<br>• **Go Integration**: Live `go-parser`, `postgres`, `redis-server`, and `localstack` containers via `task backend-pytest-go-integration`. |
| **3. Frontend Unit & Component Integration (`Jest` + RTL)** | `yarn test` / `task frontend-test` in `tdrs-frontend/src/**/*.test.{js,jsx}` | • **Component rendering & conditional UI**: Role-based view states, feature-flag toggling, empty/loading/error states.<br>• **Client-side form & file validation**: All file extension checks, client-side header validation rules, required field errors, date picker validation.<br>• **Redux actions, thunks, & selectors**: Action dispatch sequences, state reducers, memoized selectors.<br>• **Custom hooks & utility functions**: URL/header builders (`fetch-instance.js`), file error parsers. | • **Do NOT** use MirageJS (`src/mirage.js` is legacy).<br>• **Do NOT** assert on internal React state or implementation details; query the DOM via accessible queries (`screen.getByRole`, `screen.getByLabelText`, `screen.getByText`).<br>• **Do NOT** leave unawaited state updates (always `await waitFor(...)` or `await screen.findBy*(...)` after triggering async events).<br>• **Do NOT** leak mock state across tests (reset/clear mocks in `beforeEach`). | • **HTTP Calls**: Mock `fetch-instance` (`jest.mock('../../fetch-instance')` -> `get`, `post`, `patch`).<br>• **Redux Store**: Prefer real reducer store via `appConfigureStore(initialState)` for component integration tests; use `redux-mock-store` (`configureStore([thunk])`) only when asserting exact dispatched action objects in action unit tests. |
| **4. End-to-End Browser Journeys (`Cypress`)** | `yarn test:e2e` / `task frontend-e2e-local` in `tdrs-frontend/cypress/e2e/**/*.feature` | • **Critical cross-stack user journeys** (1–2 happy paths + 1 representative failure path per feature):<br>  1. Auth & access request -> Admin approval -> Role-gated navigation<br>  2. Profile view & edit lifecycle<br>  3. Data file upload -> ClamAV/S3 -> Parser execution -> Submission history summary & error report download<br>  4. Admin reparse & stuck-file recovery<br>  5. Admin feedback report `.zip` upload -> STT feedback report download | • **Do NOT** use Cypress `Scenario Outline` tables to test exhaustive client-side validation permutations (file extensions, bad headers, missing form fields)—those belong in **Jest**.<br>• **Do NOT** use fixed `cy.wait(ms)` sleeps for network requests when `cy.intercept(...).as('alias')` + `cy.wait('@alias')` can be used.<br>• **Do NOT** mock or replace API responses in Cypress E2E tests.<br>• **Do NOT** update backend state directly to simulate successful processing, and **do not** run post-test teardowns to clean up data (stale data aids manual failure debugging). | • **No application mocks**: Runs against live `web`, `celery`, `go-parser`, `postgres`, `redis-server`, `localstack`, and `clamav-rest` containers using seeded Cypress users. |
| **5. Accessibility Audits (`pa11y-ci` & `cypress-axe`)** | `yarn test:accessibility` (`.pa11yci.json`) & `cypress/e2e/common-steps/a11y.js` | • Route-level WCAG 2.1 AA automated audits across public and authenticated routes. | • **Do NOT** duplicate identical static route scans in both `pa11y-ci` and `cypress-axe` without distinct state coverage. | • `pa11y-ci` uses `REACT_APP_PA11Y_TEST=true`; `cypress-axe` runs against live authenticated states. |

---

## 2. Core Testing Principles

### General
- **Search and extend first**: Search existing tests and fixtures for the behavior before adding new coverage; extend or parameterize an existing test (`@pytest.mark.parametrize`, `test.each`) when appropriate.
- **Justify new tests**: Be able to state the behavior or regression being protected, the chosen layer (unit/component, integration/contract, or E2E), and the coverage gap a new test fills.
- **Respect test-type boundaries**: A Django API test using the database is an integration test; a browser test with mocked API responses is not full end-to-end coverage.
- **Keep suites independently runnable**: Unit, integration, and end-to-end suites must each run on their own without hidden cross-suite dependencies.
- **Descriptive naming**: Give tests descriptive names that identify the scenario and expected outcome. Keep Cypress feature scenarios in business language using Gherkin.
- **Regression reproduction**: For bug fixes, demonstrate that the regression test fails for the original defect and passes with the fix when reproducible.
- **Observable waits only**: Wait for observable conditions with bounded timeouts (`waitFor`, `cy.wait('@alias')`). Avoid fixed delays (`cy.wait(3000)`, `time.sleep`) that assume processing has finished.
- **Never hide failures**: Do not weaken assertions, lower coverage thresholds, increase retries, or skip/delete tests merely to make a failure disappear.

### Unit Tests
- Verify **one focused behavior** using real local logic and simple data.
- Mock dependencies outside the unit (database access, network requests, storage, task dispatch), **never** the behavior being tested.
- Patch dependencies where the code uses them, and keep mock responses consistent with their real contracts.
- Cover normal inputs, boundary values, missing or malformed inputs, and relevant failures; parameterize validation and parsing cases (`@pytest.mark.parametrize`, `test.each`).
- Assert returned values, errors, state changes, or rendered behavior. Assert mock calls when the interaction itself matters (e.g., dispatching a task exactly once).

### Integration Tests
- Keep components inside the integration boundary real—do not mock the serializer, permission check, database operation, or parser whose integration the test claims to verify.
- When replacing services outside the boundary with controlled substitutes, document those substitutions and what the test cannot prove.
- Use **real workers and queues** (`task backend-pytest-go-integration`) when testing asynchronous delivery, retries, or worker visibility of committed data; eager task execution only proves synchronous behavior.
- Cover successful interactions, invalid requests, role and STT access restrictions, persistence, and relevant dependency failures.
- For submission and processing flows, cover valid transitions, rejected transitions, duplicate processing, retries, and stale-worker protection where applicable.

### End-to-End Tests (`Cypress`)
- Use the real frontend, backend, and processing services involved in the journey. Observe requests with `cy.intercept()` without mocking or replacing their responses.
- Create prerequisites through fixtures or setup APIs, then perform the behavior under test through the UI. Do not update backend state to simulate successful processing.
- **No post-run teardowns**: Do not clean up data after a test run; stale test data—especially from failures—is useful for manual debugging. Prefer setup steps and fixtures that create requisite data.
- Use the existing Cypress login helper for ordinary journeys, but do not count those tests as identity-provider login coverage; test authentication redirects and callbacks separately.
- Cover representative journeys for relevant roles (account access, profile changes, file submission, processing results, submission history, report downloads), including critical unsuccessful journeys.
- Assert meaningful user-visible outcomes, including final processing results and downloaded content where relevant.
- Keep Gherkin scenarios short (~5 steps each) as simple documentation of the feature, with generalized step definitions.

---

## 3. Backend (`pytest`) Boilerplate & Mocking Patterns

### A. Direct Serializer / Validator Unit Test (No HTTP Overhead)
```python
import pytest
from tdpservice.data_files.serializers import DataFileSerializer


@pytest.mark.django_db
@pytest.mark.parametrize(
    "quarter,year,is_valid",
    [
        ("Q1", 2024, True),
        ("Q4", 2020, False),
    ],
)
def test_datafile_serializer_quarter_validation(
    data_analyst, stt, mocker, quarter, year, is_valid
):
    """Validate DataFileSerializer rules directly without HTTP upload overhead."""
    data_analyst.stt = stt
    data_analyst.save(update_fields=["stt"])

    mocker.patch(
        "tdpservice.security.clients.ClamAVClient.scan_file", return_value=True
    )

    serializer = DataFileSerializer(
        data={
            "original_filename": "TANF_T1.txt",
            "quarter": quarter,
            "year": year,
            "section": "Active Case Data",
            "program_type": "TAN",
            "stt": stt.id,
            "user": data_analyst.id,
        },
        context={"user": data_analyst},
    )

    assert serializer.is_valid() is is_valid
```

### B. DRF API Endpoint + 3-Boundary RBAC Test
```python
import io
import pytest
from rest_framework import status
from tdpservice.data_files.test.factories import DataFileFactory


@pytest.mark.django_db
class TestDataFileLogsEndpoint:
    """Verify authentication, STT object permissions, and S3 download delegation."""

    def test_rejects_unauthenticated_request(self, api_client, mocker):
        datafile = DataFileFactory.create()
        download_mock = mocker.patch(
            "tdpservice.data_files.views.S3FileHandler.download_file"
        )

        response = api_client.get(f"/v1/data_files/{datafile.pk}/logs/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        download_mock.assert_not_called()

    def test_denies_cross_stt_data_analyst(
        self, api_client, data_analyst, other_stt, mocker
    ):
        datafile = DataFileFactory.create(stt=other_stt)
        api_client.force_authenticate(user=data_analyst)
        download_mock = mocker.patch(
            "tdpservice.data_files.views.S3FileHandler.download_file"
        )

        response = api_client.get(f"/v1/data_files/{datafile.pk}/logs/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        download_mock.assert_not_called()

    def test_allows_authorized_stt_analyst_and_streams_log(
        self, api_client, data_analyst, stt, mocker
    ):
        datafile = DataFileFactory.create(user=data_analyst, stt=stt)
        api_client.force_authenticate(user=data_analyst)
        download_mock = mocker.patch(
            "tdpservice.data_files.views.S3FileHandler.download_file",
            return_value=io.BytesIO(b"parser log output"),
        )

        response = api_client.get(f"/v1/data_files/{datafile.pk}/logs/")

        assert response.status_code == status.HTTP_200_OK
        assert b"".join(response.streaming_content) == b"parser log output"
        download_mock.assert_called_once()
```

### C. Mocking External Boundaries in `pytest` (`mocker.patch` Reference)
```python
# 1. Celery task dispatch (prevent synchronous/broker task execution in view tests)
parse_task_mock = mocker.patch("tdpservice.data_files.views.parser_task.parse.delay")

# 2. S3 File Handler upload/download
s3_download_mock = mocker.patch(
    "tdpservice.data_files.views.S3FileHandler.download_file",
    return_value=io.BytesIO(b"file bytes"),
)

# 3. ClamAV virus scan (globally mocked in conftest.py, or explicitly per test)
clamav_mock = mocker.patch.object(
    ClamAVClient, "scan_file", return_value=True
)

# 4. Keycloak Admin Sync (prevent signal-triggered HTTP calls when testing Keycloak sync)
kc_sync_mock = mocker.patch(
    "tdpservice.users.keycloak_sync.KeycloakSyncClient"
)
```

### D. Factory Performance Rule: Reuse `user` and `stt` Fixtures
```python
# GOOD: Reuses existing user and stt fixtures (1 user created instead of 10)
files = DataFileFactory.create_batch(10, user=data_analyst, stt=stt)

# BAD: Creates 10 separate users (10 password hashes) and 10 STTs
files = DataFileFactory.create_batch(10)
```

---

## 4. Frontend (`Jest` + React Testing Library) Boilerplate & Patterns

### A. Component Integration Test Using `fetch-instance` Manual Mock & Redux Store
All HTTP calls in `tdrs-frontend/src/` go through `src/fetch-instance.js` (`get`, `post`, `patch`), which returns `{ data, error, status, ok }`. A manual mock exists at `src/__mocks__/fetch-instance.js`.

Always reset mocks in `beforeEach` (`jest.clearAllMocks()`, or `jest.resetAllMocks()` if tests configure distinct `mockImplementation`s) so mock call counts and queued responses do not leak between tests.

```javascript
import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'
import appConfigureStore from '../../configureStore'
import { get, post, patch } from '../../fetch-instance'
import MyComponent from './MyComponent'

// Uses src/__mocks__/fetch-instance.js automatically
jest.mock('../../fetch-instance')

// If the component initializes USWDS widgets (fileInput / datePicker), mock them:
jest.mock('@uswds/uswds/src/js/components', () => ({
  fileInput: { init: jest.fn() },
  datePicker: { init: jest.fn() },
}))

describe('MyComponent', () => {
  const defaultState = {
    auth: {
      authenticated: true,
      user: {
        id: 1,
        email: 'analyst@example.com',
        roles: [{ name: 'Data Analyst' }],
        stt: { id: 6, type: 'state', code: 'CA', name: 'California' },
        account_approval_status: 'Approved',
      },
    },
    featureFlags: {
      flags: {},
      loading: false,
    },
  }

  const renderComponent = (stateOverrides = {}, props = {}) => {
    const store = appConfigureStore({ ...defaultState, ...stateOverrides })
    return {
      store,
      ...render(
        <MemoryRouter initialEntries={['/data-files']}>
          <Provider store={store}>
            <MyComponent {...props} />
          </Provider>
        </MemoryRouter>
      ),
    }
  }

  beforeEach(() => {
    jest.clearAllMocks()

    get.mockResolvedValue({
      data: [],
      error: null,
      status: 200,
      ok: true,
    })
  })

  it('displays validation error on invalid client-side file selection without calling API', async () => {
    renderComponent()

    const fileInput = screen.getByLabelText(/Active Case Data/i)
    const invalidFile = new File(['bad content'], 'report.pdf', {
      type: 'application/pdf',
    })

    fireEvent.change(fileInput, { target: { files: [invalidFile] } })

    expect(
      await screen.findByText(/Invalid extension/i)
    ).toBeInTheDocument()
    expect(post).not.toHaveBeenCalled()
  })

  it('submits valid payload and renders updated result', async () => {
    post.mockResolvedValueOnce({
      data: { id: 42, original_filename: 'TANF_T1.txt' },
      error: null,
      status: 201,
      ok: true,
    })

    renderComponent()

    fireEvent.click(screen.getByRole('button', { name: /Submit/i }))

    await waitFor(() => {
      expect(post).toHaveBeenCalledWith(
        expect.stringContaining('/v1/data_files/'),
        expect.any(FormData)
      )
    })
  })
})
```

### B. Redux Thunk / Action Unit Test Using `redux-mock-store`
```javascript
import configureStore from 'redux-mock-store'
import { thunk } from 'redux-thunk'
import { get } from '../fetch-instance'
import { fetchFeatureFlags, SET_FEATURE_FLAGS } from './featureFlags'

jest.mock('../fetch-instance')

const mockStore = configureStore([thunk])

describe('actions/featureFlags', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('dispatches SET_FEATURE_FLAGS on 200 OK', async () => {
    get.mockResolvedValueOnce({
      data: [{ feature_name: 'fra_reports', enabled: true }],
      error: null,
      status: 200,
      ok: true,
    })
    const store = mockStore({})

    await store.dispatch(fetchFeatureFlags())

    const actions = store.getActions()
    expect(actions[0].type).toBe(SET_FEATURE_FLAGS)
  })
})
```

### C. Common Browser API Mocks for File Upload & Scroll Tests
```javascript
// 1. scrollIntoView (JSDOM does not implement scrollIntoView)
window.HTMLElement.prototype.scrollIntoView = jest.fn()

// 2. Blob download URL creation
window.URL.createObjectURL = jest.fn(() => 'blob:http://localhost/mock')

// 3. FileReader for header-validation / zip-inspection components
global.FileReader = jest.fn().mockImplementation(() => ({
  readAsText: jest.fn(function () {
    this.result = 'HEADER20244A06TANFTANF1     '
    if (this.onload) this.onload({ target: { result: this.result } })
  }),
  readAsArrayBuffer: jest.fn(function () {
    this.result = new ArrayBuffer(8)
    if (this.onload) this.onload({ target: { result: this.result } })
  }),
}))
```

---

## 5. End-to-End (`Cypress` + Cucumber) Boilerplate & Patterns

### A. Gherkin `.feature` Authoring Rules
- Keep scenarios focused on **end-to-end multi-service workflows** (browser -> Django API -> Celery/Go parser/S3 -> UI update) and short (~5 steps each).
- Never add `Scenario Outline` tables for client-side input/header validation—put those in Jest (`src/components/**`).
- Reuse shared steps from `cypress/e2e/common-steps/common-steps.js` and `cypress/e2e/common-steps/data_files.js`.

```gherkin
Feature: Data File Submission Journey
  Scenario: Data Analyst uploads a valid TANF file and views parsed summary
    Given 'Data Analyst' logs in
    When the user selects STT 'Arkansas', Fiscal Year '2023', and Quarter 'Q1'
    And the user uploads 'small_correct_file.txt' to 'Active Case Data'
    Then the submission history table shows status 'Accepted' for 'Active Case Data'
```

### B. Step Implementation & Network Synchronization Pattern (`.js`)
```javascript
/* eslint-disable no-undef */
import { When } from '@badeball/cypress-cucumber-preprocessor'

When(
  'the user selects STT {string}, Fiscal Year {string}, and Quarter {string}',
  (sttName, year, quarter) => {
    cy.intercept('GET', '/v1/stts/alpha*').as('getStts')
    cy.intercept('GET', `/v1/data_files/?*year=${year}*`).as('getDataFiles')

    cy.visit('/data-files')
    cy.wait('@getStts', { timeout: 30000 })

    cy.get('#stt').should('be.visible').clear().type(sttName)
    cy.get('.usa-combo-box [role="option"]')
      .contains(new RegExp(`^${sttName}$`, 'i'))
      .click()

    cy.get('#reportingYears').select(year)
    cy.get('#quarter').select(quarter)
    cy.contains('button', 'Search').click()

    cy.wait('@getDataFiles', { timeout: 30000 })
  }
)
```
