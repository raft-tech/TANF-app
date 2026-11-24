# TDP Tech Deep Dive - Automated Tests

For detailed layer ownership rules, core testing principles, and canonical mocking boilerplate across `pytest`, `go test`, `Jest`, and `Cypress`, see **[`docs/agents/testing.md`](../agents/testing.md)**.

## Backend Unit & Integration Tests (`pytest`)
* Uses `pytest`, `pytest-django`, `pytest-mock`, and `pytest-factoryboy`.
* Most tests are located in their relevant Django app under `tdrs-backend/tdpservice/**/test/`.
* Shared fixtures (including role-specific user fixtures and mocked ClamAV clients) are defined in `tdrs-backend/tdpservice/conftest.py`.
* Live Django-to-Go parser integration tests live under `tdrs-backend/tdpservice/parsers/test/integration/` and run against the `go-parser` container.

```bash
# Run standard backend pytest suite
task backend-pytest

# Run live Go parser integration suite
task backend-pytest-go-integration
```

## Go Parser Unit Tests (`go test`)
* Located in `tdrs-services/parser/internal/**`.
* Covers record decoding, field transformations, validation rules, and DB batch writing.

```bash
cd tdrs-services/parser && make test
```

## Frontend Unit & Component Tests (`Jest` + React Testing Library)
* Uses Jest and `@testing-library/react`.
* Tests exist alongside their associated action, component, hook, selector, or reducer under `tdrs-frontend/src/`.
* HTTP requests are mocked via `jest.mock('../../fetch-instance')` (`tdrs-frontend/src/__mocks__/fetch-instance.js`), with mocks reset between tests in `beforeEach` (`jest.clearAllMocks()`).

```bash
# Run in Docker (watch-less)
task frontend-test

# Or locally in tdrs-frontend/
cd tdrs-frontend && yarn test
```

## Admin Console Unit Tests (`Vitest`)
* `tdrs-admin` unit tests use Vitest and run in Docker via Taskfile:

```bash
task admin-test
```

## Frontend Accessibility Tests (`Pa11y` & `cypress-axe`)
* `pa11y-ci` navigates to application routes with `REACT_APP_PA11Y_TEST=true` (configured in `tdrs-frontend/.pa11yci.json`) and runs automated WCAG 2.1 AA accessibility checks, storing screenshots as CircleCI artifacts.
* `cypress-axe` (`tdrs-frontend/cypress/e2e/common-steps/a11y.js`) audits authenticated UI states during E2E runs.

```bash
cd tdrs-frontend && yarn test:accessibility
```

## End-to-End Integration Tests (`Cypress`)
* Uses Cypress with `@badeball/cypress-cucumber-preprocessor` (`tdrs-frontend/cypress/e2e/**/*.feature`).
* Synchronize on network calls using `cy.intercept(...).as('alias')` and `cy.wait('@alias')` rather than fixed `cy.wait(ms)` delays.
* See **[`cypress-integration-tests.md`](./cypress-integration-tests.md)** for setup and execution instructions, and **[`docs/agents/testing.md`](../agents/testing.md)** for what belongs in Cypress vs. Jest.

```bash
# Run locally via Taskfile
task frontend-e2e-local

# Or open Cypress interactively in tdrs-frontend/
cd tdrs-frontend && yarn test:e2e
```
