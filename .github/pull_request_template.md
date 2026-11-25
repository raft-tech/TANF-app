## Summary of Changes
_Provide a brief summary of changes_
Pull request closes #_

## How to Test
_List the steps and `Taskfile.yml` commands to test the PR (e.g., `task backend-pytest`, `task frontend-test`, `task admin-test`, `cd tdrs-services/parser && make test`)._
These steps are generic, please adjust as necessary.
```
task backend-up
task frontend-up
```

1. Open http://localhost:3000/ and sign in.
1. Proceed with functional tests as described herein.
1. Test steps should be captured in the demo GIF(s) and/or screenshots below.
> *Demo GIF(s) and screenshots for testing procedure*

## Deliverables
_More details on how deliverables herein are assessed included [here](https://github.com/raft-tech/TANF-app/blob/develop/docs/How-We-Work/our-priorities-values-expectations.md#Deliverables)._

### [Deliverable 1: Accepted Features](https://github.com/raft-tech/TANF-app/blob/develop/docs/How-We-Work/our-priorities-values-expectations.md#Deliverable-1-Accepted-Features)

Checklist of ACs:
+ [ ] [**_insert ACs here_**]
+ [ ] **`lfrohlich`** and/or **`adpennington`**  confirmed that ACs are met.

### [Deliverable 2: Tested Code](https://github.com/raft-tech/TANF-app/blob/develop/docs/How-We-Work/our-priorities-values-expectations.md#Deliverable-2-Tested-Code)

+ Test-Scope Review (see [`docs/agents/testing.md`](docs/agents/testing.md)):
  + [ ] Existing tests and fixtures were reviewed before adding new coverage (extending or parameterizing where appropriate).
  + [ ] New tests specify the behavior/regression protected, chosen layer, and unique coverage gap filled.
  + [ ] Any consolidation performed or justification for multi-layer overlap is noted.
+ Are all areas of code introduced in this PR meaningfully tested?
  + [ ] If this PR introduces backend (`tdrs-backend`) code changes, are they meaningfully tested (`task backend-pytest`)?
  + [ ] If this PR introduces frontend (`tdrs-frontend`) code changes, are they meaningfully tested (`task frontend-test`)?
  + [ ] If this PR introduces Go parser (`tdrs-services/parser`) code changes, are they meaningfully tested (`make test` / `task backend-pytest-go-integration`)?
  + [ ] If this PR introduces admin console (`tdrs-admin`) code changes, are they meaningfully tested (`task admin-test`)?
+ Are code coverage minimums met?
  + [ ] Frontend coverage: [_insert coverage %_] (see `CodeCov Report` comment in PR)
  + [ ] Backend coverage: [_insert coverage %_] (see `CodeCov Report` comment in PR)
  + [ ] Go parser / Admin coverage (if applicable): [_insert coverage %_]

### [Deliverable 3: Properly Styled Code](https://github.com/raft-tech/TANF-app/blob/develop/docs/How-We-Work/our-priorities-values-expectations.md#Deliverable-3-Properly-Styled-Code)

+ [ ] Are backend code style checks passing on CircleCI (`task backend-lint`)?
+ [ ] Are frontend code style checks passing on CircleCI (`task frontend-lint`)?
+ [ ] Are Go parser / Admin style checks passing (if applicable: `task parser:lint`)?
+ [ ] Are code maintainability principles being followed?

### [Deliverable 4: Accessible](https://github.com/raft-tech/TANF-app/blob/develop/docs/How-We-Work/our-priorities-values-expectations.md#Deliverable-4-Accessibility)

+ [ ] Does this PR complete the epic? 
+ [ ] Are links included to any other gov-approved PRs associated with epic?
+ [ ] Does PR include documentation for Raft's a11y review? 
+ [ ] Did automated and manual testing with `iamjolly` and `ttran-hub` using Accessibility Insights reveal any errors introduced in this PR?


### [Deliverable 5: Deployed](https://github.com/raft-tech/TANF-app/blob/develop/docs/How-We-Work/our-priorities-values-expectations.md#Deliverable-5-Deployed)

+ [ ] Was the code successfully deployed via automated CircleCI process to development on Cloud.gov?

### [Deliverable 6: Documented](https://github.com/raft-tech/TANF-app/blob/develop/docs/How-We-Work/our-priorities-values-expectations.md#Deliverable-6-Code-documentation)

+ [ ] Does this PR provide background for why coding decisions were made?
+ [ ] If this PR introduces backend code, is that code easy to understand and sufficiently documented, both inline and overall?
+ [ ] If this PR introduces frontend code, is that code easy to understand and sufficiently documented, both inline and overall?
+ [ ] If this PR introduces dependencies, are their licenses documented?
+ [ ] Can reviewer explain and take ownership of these elements presented in this code review?

### [Deliverable 7: Secure](https://github.com/raft-tech/TANF-app/blob/develop/docs/How-We-Work/our-priorities-values-expectations.md#Deliverable-7-Secure)

+ [ ] Does the OWASP Scan pass on CircleCI?
+ [ ] Do manual code review and manual testing detect any new security issues?
+ [ ] If new issues detected, is investigation and/or remediation plan documented? 

### [Deliverable 8: User Research](https://github.com/raft-tech/TANF-app/blob/develop/docs/How-We-Work/our-priorities-values-expectations.md#Deliverable-8-User-Research)

Research product(s) clearly articulate(s):
+ [ ] the purpose of the research
+ [ ] methods used to conduct the research 
+ [ ] who participated in the research
+ [ ] what was tested and how
+ [ ] impact of research on TDP
+ [ ] (_if applicable_) final design mockups produced for TDP development 


