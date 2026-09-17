# Proposed workflow: Set Start date when work begins

Intended path after activation: `.github/workflows/set-start-date-when-work-begins.yml`

## Start date field
Start date is a **repo Issue Field** on `raft-tech/TANF-app`:

- Issue Field id: `IFD_kgDOAO480A`
- Mutation: `updateIssueFieldValue` (not `updateProjectV2ItemFieldValue` / not `PVTF_*`)
- Works for **Issues only**; open PRs are skipped by the workflow

## Why under `scripts/ci/` for now
Creating `.github/workflows/*` requires the classic `workflow` OAuth scope on the automation PAT. Copy this file into `.github/workflows/` via UI, or grant `workflow` and ask the bot to move it.

## Activate
1. Secret `TDP_PROJECT_TOKEN` (read TDP Roadmap + write Issue Fields)
2. Place YAML under `.github/workflows/set-start-date-when-work-begins.yml`
3. Merge / run workflow_dispatch
