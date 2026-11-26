# Frontend Context

This context covers the CRA React frontend under `tdrs-frontend/`.

## Boundaries

- User-facing workflows, React components, frontend routing, client-side state, frontend tests, and frontend build configuration live here.
- Authentication and user access workflows may also require reading the backend and Keycloak contexts.
- Data submission, validation messaging, and reporting screens should align with backend behavior and product terminology.

## Test Strategy

- Frontend unit and component integration tests live alongside source files (`tdrs-frontend/src/**/*.test.{js,jsx}`) and run via `yarn test` (`task frontend-test`).
- Mock HTTP requests using `jest.mock('../../fetch-instance')` (backed by `tdrs-frontend/src/__mocks__/fetch-instance.js`), which returns `{ data, error, status, ok }`, and reset mocks in `beforeEach` (`jest.clearAllMocks()`). Do not use legacy MirageJS (`src/mirage.js`).
- Client-side form, file extension, and header validation permutations belong in Jest component/unit tests, not Cypress.
- End-to-end browser tests use Cypress + Cucumber (`tdrs-frontend/cypress/e2e/**/*.feature` and matching `.js` step files) and run via `yarn test:e2e` (`task frontend-e2e-local`). Reserve Cypress for critical cross-stack journeys, synchronize on `cy.intercept()` aliases rather than fixed `cy.wait(ms)` delays, and do not mock API responses or add post-run teardowns.
- Route-level accessibility checks run via `yarn test:accessibility` (`pa11y-ci` configured in `.pa11yci.json`) and `cypress-axe` (`cypress/e2e/common-steps/a11y.js`).
- Read `docs/agents/testing.md` for full layer ownership rules and `Jest` / `Cypress` mocking boilerplate.

## Read With

- Root `CONTEXT.md`
- `CONTEXT-MAP.md`
- `docs/agents/testing.md`
- Relevant frontend README and source-level docs
- Relevant product, UX, and technical docs under `docs/`
