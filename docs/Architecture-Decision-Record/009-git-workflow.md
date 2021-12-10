# 9. Git Workflow

Date: 2021-02-23 (_updated 2021-11-01_)

## Status

Approved

## Context

In order to maintain the principal of Least Privilege, it was decided at the onset of this project that the vendor (Raft) would work from a fork of the government repo and issue pull requests to the government repo from the fork. The vendor would not have write access to the government repository or the government's CircleCI account.

Throughout the project all vendor development work has been done in the vendor's forked repository, while pull requests from the government and even some documentation pull requests from the vendor were made directly to the government repository.

This has created a situation where the vendor has needed to continuously rebase with the government repository to make sure the vendor's repository was up to date. As a result, problems with the Git history have arisen that make it confusing for both the government and the vendor to track the history of the work.

The proposed workflow below provides a remedy to these issues, as well as many others, as detailed in the Consequences section.

## Decision

A contributor to the TDP project would always use the following steps to propose changes to the repository. No merges directly into `HHS:main`

![](images/TANF-Git-Workflow.png)

1. Check out `raft-tdp-main` in `raft-tech/TANF-app` (or another branch if this work is dependent on a branch that hasn't been merged yet)
2. If working locally, run `git pull`
3. Check out new feature branch `git checkout -b <BRANCH NAME>`
4. Update the repo with code, documentation, etc.
5. If working locally, run `git push origin <BRANCH NAME>`
6. Create [a draft pull request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests#draft-pull-requests) from new branch to `raft-tdp-main`. The PR title should include WIP e.g. `WIP: Adding a feature` (If your work is dependent on another branch that has yet to be merged, issue the pull request against that branch)
8. Implement, Test, Review work independently
    * If content is devops oriented, developer can freely merge to `HHS:hhs-dev-devops` to test their changes. No merges from `HHS:hhs-dev-devops` to `HHS:main` will be accepted.
9. When finished: 
    * Update the Pull Request Template
    * Add in-line comment to the file changes to provide context for the proposed changes
    * Ensure there are no merge conflicts 
    * Ensure CI/CD pipelines are green
    * For frontend PRs, ensure that documentation trail from Raft's a11y review associated with epic is included and indicate if PR completes this epic. 
    * Update the title to remove `WIP`, change the PR to [Ready for Review](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/changing-the-stage-of-a-pull-request), assign label `raft-review`.
    * If your PR is against a branch other than `raft-tdp-main` keep it as a draft PR and add the tag `blocked` until the other branch is merged. 
13. Assign a reviewer: 
    * For development work, assign **at least two** Raft developers with one of them being `abottoms-coder` or `jtwillis92` (**but not both**).
    * For research and design assign `reitermb`
    * For security controls assign `abottoms-coder`
    * For documentation submitted by the Government tag `lfrohlich` and `adpennington` and remove label `raft-review`
    * For documentation submissions and updates by raft assign `lfrohlich` and `adpennington` and add label `QASP review`
14. For PRs with `raft-review` label, the appropriate reviewer(s) perform the review and/or requests changes.
    * For dev tickets, author is expected to schedule a tabletop meeting at a minimum 48 hours after the PR is published. 
    **GOAL** 3 days: 2 days to perform the review and 1 day to implement the requested changes. 
    * When changes are asked for, the changes are made by the contributor
    * When satisfied, the reviewer(s) `approves` the PR

15. For dev tickets, tabletop review meetings are covered in-depth in [this ADR](018-developer-tabletops.md). If the outcome of the tabletop requires no rework, Technical Lead will:
    * `approve` the PR
    * remove `raft-review` label
    * add `qasp-review` label
    * assign the Government as the reviewer:
        * For backend and frontend development work assign `adpennington`
        * For frontend work submitted for review but does not yet complete the epic, `adpennington` will sign off on Raft's a11y documentation (e.g. screen captures with VoiceOver utility, summary of review, etc.) and cc: `ttran-hub`
        * For frontend work submitted for review that completes the epic, `adpennington` will complete code review, tag `ttran-hub` + `iamjolly` via comment, and add `a11y` label to PR. Gov a11y review team will use accessibility insights for manual testing. More information about how and when this process will be carried out is described [here.](https://github.com/HHS/TANF-app/blob/main/docs/Technical-Documentation/how-government-will-test-a11y.md) 
        * For research and design work assign `lfrohlich`
     * posts that PR is ready for QASP review in GitNotify channel in Teams and tags appropriate government reviewer.
18. For PRs with `qasp-review` label, the appropriate government reviewer performs the review and/or requests changes. **GOAL** 5 days: 3 days to perform the review and 2 days to implement the requested changes.
    * When changes are asked for, the changes are made by the contributor. Raft reviewers should internalize the changes asked by the Government such that the same feedback is already incorporated and/or caught in future (continuous improvement)
    * Government reviewer is expected to check off boxes in the PR description relating to the deliverables described.
19. When satisfied, the Government reviewer `approves` the PR and tags with the  `ready-to-merge` label. Government reviewer posts that PR is ready to merge in GitNotify channel on Teams.   
20. `abottoms-coder` clicks Merge into `raft-tdp-main`
21. `abottoms-coder` (or his back-up):
    * opens a PR from `raft-tdp-main` to `HHS:main`
    * Updates the PR template to change `addresses` to `closes` so that issue [can be automatically closed when the Government merges](https://docs.github.com/en/github/managing-your-work-on-github/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword)
    * Ensures the CI/CD pipelines are green
    * Assigns the Government as reviewers and pings them on Teams in GitNotify channel to review/merge
26. PR is approved and merged to `HHS:main` by `adpennington` or `lfrohlich` **GOAL** 1 day from open date (by now the code is already approved by the Government)

## Consequences

**Pros**
- Dependency chains would be much easier to manage
  - We can daisy chain PRs with dependencies allowing GitHub to manage changes for downline PRs much more simply and cleanly
  - ie. `my_branch_1` depends on `my_branch_0` and there is an open PR from `my_branch_0` to `raft-tdp-main`. Can open a PR in raft-tech from `my_branch_1` to `my_branch_0` and only the changes from the latest branch will be shown to reviewers, but the dependent code will still be present and kept up to date by GitHub exposing a button to update with upstream branch
  - Because of this, we can more easily submit smaller PRs since this removes much of the maintenance work currently involved to achieve that goal
- Less complexity for developers, reviewers
- No need to rebase from `HHS:main` back to `raft-tdp-main`
- Much smaller chance of needing to revert commits to `HHS:main`
- Git history will be much cleaner
- Much less time managing git history
- All reviews will be in one place, so the entire history of a branch/PR will be viewable in one place
- Will allow us to keep the current CircleCi setup
  - Once staging is in place, we can deploy to the development server when code is merged in to `raft-tdp-main` and test deployment ahead of opening a PR to `HHS:main`
- We can implement it almost immediately
- We can implement GitHub Hooks to automatically issue PRs to `HHS:main` when one is merged to `raft-tdp-main`
- Maintain "Least Privelege" by restricting vendor from having write access to Gov repo and CircleCI
- Tests automated deployment before merging to `HHS:main`

**Cons**
- Only one pull request at a time will be able to go to `HHS:main`, but this won't be a problem since they will only be issued once approved and therefore can be merged immediately
- All PR comments will be on the vendor repo rather than the government repo

**Recommendations for how to get there**
- Merge/Close all [HHS PRs](https://github.com/HHS/TANF-app/pulls) by **figuring out when all can be merged** so that we can start with the process described above
- Do not merge anything directly to HHS:main. All PRs into HHS:main should come from raft-tech/raft-tdp-main unless absolutely needed.

## Notes
- All Pull Requests with the `QASP Review` label will be approved against the QASP Checklist

## Exceptions
- PRs created by Dependabot for dev-only dependencies, which will not be installed on deployed environments, may be merged in to `raft-tdp-main` as they are created. Further reasoning on this decision can be found in [the Dependabot ADR](016-dependabot-dependency-management.md) under "Development Dependencies".
