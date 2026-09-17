# Proposed workflow: Set Start date when work begins

This file is the intended GitHub Actions workflow body for:

`.github/workflows/set-start-date-when-work-begins.yml`

## Why it is under `scripts/ci/` for now
Creating or updating files under `.github/workflows/` requires a token with the classic **`workflow`** OAuth scope (or equivalent App permission). The bot PAT currently has `repo` + `project` but not `workflow`, so the API returns 404 for workflow paths.

## To activate
1. Add repo secret `TDP_PROJECT_TOKEN` (fine-grained PAT / App token: org `raft-tech`, **Projects: Read and write**).
2. Copy this file to `.github/workflows/set-start-date-when-work-begins.yml` (GitHub UI, or re-run bot after granting `workflow` scope on the automation PAT).
3. Merge, then Actions → **Set Start date when work begins** → Run workflow.

See the pull request description for full behavior and why this uses a schedule instead of `projects_v2_item`.
