# AGENTS.md

## Core Commands

- task up
- task down
- task frontend-logs
- task frontend-test
- task frontend-test-cov
- task frontend-e2e-cmd


## Tech Stack

- Framework: React 18
<!-- - Language: TypeScript (Strict mode) -->
- Styling: USWDS
- REST endpoints
- Backend Language: Django
- Backend Database: PostgreSQL

## Architecture & Preferences


## Behavioral Rules

- **Always do**: Use industry standards and best practices when possible
- **Always do**: Before starting work on a feature, ask 3-5 clarifying questions so that you are 99% sure of what the execution plan will be
- **Always do**: Before starting work on a feature, unless you suggested it and I say "yes please", display the execution plan and wait for confirmation to proceed
- **Always do**: Run Prettier, Tests and verify TypeScript types before marking a feature as finished
- **Ask first**: Installing new third-party npm packages
- **Never do**: Do not delete or rename files without confirmation

## Code Quality

- Write clear, self-documenting code with meaningful names
- Keep functions small and focused on a single responsibility
- Add comments only when explaining *why*, not *what*
- Follow existing patterns and conventions in the codebase
- Remove dead code rather than commenting it out

## Making Changes

- Read and understand existing code before modifying
- Make minimal, targeted changes that solve the specific problem
- Preserve existing formatting and style conventions
- Update tests when changing functionality
- Run linters and tests before considering work complete
- Always use type hinting when applicable

## Testing

- Write tests that verify behavior, not implementation details
- Cover edge cases and error conditions
- Keep tests independent and deterministic
- Maintain existing test coverage levels

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
