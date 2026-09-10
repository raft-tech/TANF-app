# Feedback access testing checklist

Feedback is available after authentication and account approval. The API also
requires an active account and an assigned role, using the existing approval
permission. The anonymous option controls the feedback object's user association;
it does not bypass these access checks.

## Automated checks

Local verification on September 8, 2026:

- [x] Frontend Jest suite: 83 suites, 1,010 tests passed. Global coverage:
  95.48% statements, 90.41% branches, 94.11% functions, 95.74% lines.
  The CRA Jest configuration was run directly with explicit public test settings
  because this workspace restricts access to environment files.
- [x] Frontend ESLint: passed with existing warnings.
- [x] Backend Flake8 for the changed permissions, views, and feedback API tests:
  passed.
- [x] Git diff whitespace check: passed.
- [ ] Backend feedback API suite: cannot run in this workspace. The configured
  Pipenv environment lacks pytest and Django; Docker socket access is denied.
  Run `task backend-pytest PYTEST_ARGS="tdpservice/users/test/test_api/test_feedback.py"`
  in the configured development environment.
- [ ] Cypress feedback scenarios: launch attempted, but the cached Cypress
  installation is missing a required application file. With Cypress and local
  services working, run from `tdrs-frontend`:
  `yarn test:e2e-ci --spec cypress/e2e/feedback/user-feedback.feature`.

The frontend tests cover login-dependent visibility, hiding open forms and upload
widgets on logout, anonymous payloads, pending POST/PATCH requests, duplicate
clicks and keyboard shortcuts, failures, and retries. The backend tests cover
unauthenticated requests, every unapproved status, inactive accounts, missing
roles, approved users, and creating/updating anonymous feedback.

## Manual checks remaining

- [ ] Visit `/` while signed out. Confirm there is no Give Feedback button,
  feedback modal, or upload feedback widget.
- [ ] Sign in with an approved Login.gov account, then repeat with an approved
  AMS account. Confirm Give Feedback opens the form.
- [ ] Use an account awaiting approval. Confirm feedback controls are hidden.
- [ ] Select a rating and submit a comment. Confirm the thank-you message appears
  and the stored feedback belongs to the signed-in user.
- [ ] Repeat with Send anonymously selected before choosing a rating, and again
  by selecting it after the rating save. Confirm the resulting feedback has
  `anonymous=true` and `user=null`.
- [ ] Throttle requests. Confirm Send Feedback is disabled during both rating
  saves and final submission, and repeated clicks or Cmd/Ctrl+Enter do not send
  overlapping requests. Repeat in an upload feedback widget.
- [ ] Fail a feedback request in the general modal. Confirm the button becomes
  enabled, the entered feedback remains, and retry succeeds.
- [ ] Log out with feedback open. Confirm the form disappears.

The full testing checklist remains incomplete until the unchecked items pass.
