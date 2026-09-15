---
name: update-pr-body
description: Update GitHub PR body from a provided PR URL. Use when the user asks to fill in, refresh, or update a pull request description/body.
---

# Update PR Body

Use this skill when the user provides a GitHub PR URL and asks to update the PR body.

The current session is expected to contain the implementation context for the PR, but do not rely on session memory alone. Always inspect the PR, its changed files, and its corresponding issue before editing the body.

## Workflow

1. Read the provided PR URL.
2. Fetch the PR details with `gh pr view <PR_URL> --json title,body,files,closingIssuesReferences,headRefName,baseRefName,url`.
3. Review the PR's changed files with `gh pr diff <PR_URL>` or by checking the local branch diff if the workspace is already on the PR branch.
4. Review the corresponding issue from `closingIssuesReferences`.
5. If no issue is linked, inspect the PR title/body for an issue number and review that issue with `gh issue view <number>`.
6. Preserve the existing PR body template structure. Fill in missing sections rather than replacing the template wholesale unless the user explicitly asks for a rewrite.
7. Update the PR body with `gh pr edit <PR_URL> --body-file <temp-file>`.
8. Report that the PR body was updated and include the PR URL.

## Body Guidance

- Base the summary on the implementation context, changed files, PR diff, and linked issue.
- Be specific about user-visible behavior, system behavior, migrations, configuration, and risk where relevant.
- Keep the description concise and reviewer-oriented.
- Do not invent scope that is not supported by the diff or issue.
- If a template checkbox clearly applies, mark it. Leave uncertain checkboxes unchanged unless there is enough evidence.
- Preserve any existing useful author notes, screenshots, links, or release notes.

## How To Test Guidance

The `How to test` section must be manual reviewer instructions only.

- Do not mention unit tests, automated tests, CI, linting, Jest, pytest, Cypress, or similar automated verification.
- Write step-by-step instructions a reviewer can follow locally or in the deployed review environment.
- Include setup steps only when necessary for manual verification.
- Include the expected result for each important step.
- Cover the primary changed behavior and at least one relevant edge case when the diff or issue indicates one.

Example style:

```markdown
## How to test

1. Open the affected page as a user with permission to perform the workflow.
2. Complete the updated form using valid inputs.
3. Confirm the success message appears and the saved record shows the new value.
4. Repeat the flow with the required field left blank.
5. Confirm the validation message appears and the record is not saved.
```
