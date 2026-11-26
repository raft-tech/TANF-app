# AGENTS.md (Cypress E2E & Accessibility)

Rules specific to end-to-end and accessibility tests under `tdrs-frontend/cypress/`. For repo-wide testing rules and layer ownership, see `docs/agents/testing.md`.

## Journey & Gherkin Guidelines

- Keep `.feature` scenarios short (~5 steps each) and written in business language.
- Reuse shared steps from `cypress/e2e/common-steps/common-steps.js` and `cypress/e2e/common-steps/data_files.js` with generalized step definitions.
- Reserve Cypress for critical cross-stack journeys; client-side form, file extension, and header validation permutations belong in Jest (`tdrs-frontend/src/**/*.test.{js,jsx}`).

## Network, State & Teardown Hygiene

- Run against real backend/worker containers (`web`, `celery`, `go-parser`, `postgres`, `redis-server`, `localstack`, `clamav-rest`). Do not mock or replace API responses.
- Synchronize on network requests with `cy.intercept(...).as('alias')` and `cy.wait('@alias')` using bounded timeouts—never use fixed `cy.wait(ms)` sleeps.
- Create prerequisites through fixtures or setup APIs, then perform the behavior under test through the UI. Never mutate backend state to simulate processing.
- Do not clean up test data with post-run teardowns; stale data (especially from failures) aids manual debugging.
- Do not count tests using the Cypress login helper as identity-provider login coverage; test authentication redirects and callbacks separately.
