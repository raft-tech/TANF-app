# Hotfix process

ADRs [009-git-workflow](./Architecture-Decision-Record/009-git-workflow.md) and [018-versioning-and-releases](./Architecture-Decision-Record/018-versioning-and-releases.md) outline the git workflow and release process. The purpose of this document is to explain the hotfix workflow in more detail to save time and prevent missteps in the future.

Hotfixes are reserved for release-blocking or high-severity production defects. Non-blocking bugs/defects should follow the normal process for prioritizing tickets.

1. Identify the current release version, e.g., `v4.23.0`.
2. Create a hotfix branch from the affected release branch in the `raft-tech/TANF-app` fork. If the release has already been merged to `HHS/TANF-app:main`, then the release branch may need to be restored (you can do so in the release PR in `HHS/TANF-app:main`).

   ```bash
   git fetch origin
   git switch release/v4.23.0
   git pull --ff-only origin release/v4.23.0
   git switch -c hotfix/v4.23.0-<ISSUE>
   ```

3. Implement the fix, add tests, and push the branch:
   ```bash
   git push -u origin hotfix/v4.22.0-<ISSUE>
   ```
4. Open the hotfix PR in `raft-tech/TANF-app` fork, with the release branch as the base branch:
   - Repository: `raft-tech/TANF-app`
   - Base branch: `release/v4.23.0`
   - Head branch: `hotfix/v4.22.0-<ISSUE>`
5. NOTE: if the hotfix branch was originally branched off `develop`, you **must rebase onto the release branch**.
6. Gain the needed approvals, then merge the hotfix into the release branch.
7. Create a new release branch where the `fix` version is incremented:
   - `release/v4.23.1`
   - Follow the rest of the release process described in [018-versioning-and-releases](./Architecture-Decision-Record/018-versioning-and-releases.md), including tagging, creating a release in the `raft-tech/TANF-app` repo, and opening the PR to `HHS/TANF-app:main`
8. Backport the fix into `raft-tech/TANF-app:develop` by creating a branch from the latest `develop` and cherry-picking the hotfix commit
   ```bash
   git switch develop
   git pull --ff-only origin develop
   git switch -c backport/<ISSUE>-hotfix-to-develop
   git cherry-pick <HOTFIX-COMMIT-SHA>
   git push -u origin backport/<ISSUE>-hotfix-to-develop
   ```
9. Open a second PR in this fork:
   - Repository: `raft-tech/TANF-app`
   - Base branch: `develop`
   - Head branch: `backport/<ISSUE>-hotfix-to-develop`
