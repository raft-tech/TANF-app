# AGENTS.md

## Code Quality

- Write clear, self-documenting code with meaningful names
- Keep functions small and focused on a single responsibility
- Add comments only when explaining _why_, not _what_
- Follow existing patterns and conventions in the codebase
- Remove dead code rather than commenting it out

## Making Changes

- Read and understand existing code before modifying
- Make minimal, targeted changes that solve the specific problem
- Preserve existing formatting and style conventions
- Update tests when changing functionality
- Run linters and tests before considering work complete
- Always use type hinting when applicable
- Use migrations only for database schema changes.
- Do not use Django migrations (`RunPython` or `RunSQL`) to seed feature flags, configuration, reference data, or other application data.
- Seed or update application data through an explicit management command, deployment step, fixture, or documented administrative procedure.
- Ask before adding a migration that modifies existing data.
- Never modify migrations that have already been committed to the `develop` branch

## Testing

- Write tests that verify behavior, not implementation details
- Cover edge cases and error conditions at the lowest, fastest test layer (`pytest` unit/serializer, `go test`, or `Jest` component tests) rather than duplicating permutations in E2E
- Keep tests independent and deterministic; never weaken assertions, increase retries, or skip tests merely to hide failures
- Maintain existing test coverage levels
- In `pytest` (`tdrs-backend`), test endpoint RBAC using 3 boundary cases (1 permitted role, 1 denied role/cross-STT, 1 unauthenticated client) rather than parametrizing all 7+ roles across every view, and reuse `user`/`stt` fixtures when creating `DataFileFactory` batches
- In `Jest` (`tdrs-frontend/src`), mock HTTP calls via `jest.mock('../../fetch-instance')` (`src/__mocks__/fetch-instance.js`), reset mocks in `beforeEach` (`jest.clearAllMocks()`), never use legacy MirageJS, and own all client-side form/file/header validation permutations here
- In `Cypress` (`tdrs-frontend/cypress/e2e`), test only critical cross-stack user journeys; never mock API responses, add client-side validation matrices, use fixed `cy.wait(ms)` network sleeps, or run post-test data teardowns

## Security

- Never hardcode secrets, credentials, or API keys
- Use environment variables for configuration
- Validate and sanitize all inputs
- Follow the principle of least privilege

## Problem Solving

- Identify root causes before implementing fixes
- Prefer simple solutions over clever ones
- Ask clarifying questions when requirements are ambiguous
- Document assumptions and decisions

## Agent skills

### Issue tracker

Issues and PRDs are always created in GitHub Issues for this repo. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the default mattpocock/skills triage label vocabulary. See `docs/agents/triage-labels.md`.

### Domain docs

This is a multi-context monorepo with a root `CONTEXT-MAP.md` pointing to subsystem context files. See `docs/agents/domain.md`.

### Testing

Before authoring, refactoring, or reviewing automated tests in `pytest`, `go test`, `Jest`, or `Cypress`, read `docs/agents/testing.md` for layer ownership definitions, core principles, and canonical mocking boilerplate.

### Scoped `AGENTS.md` files

Put feature- or module-specific agent instructions in a local `AGENTS.md` inside that subdirectory (for example, `tdrs-frontend/cypress/AGENTS.md` or `tdrs-backend/tdpservice/parsers/AGENTS.md`) rather than crowding the root `AGENTS.md`.
