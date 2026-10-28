# Sprint Summary: Oct 14, 2026 - Oct 27, 2026

## Overview

- Closed DataFile and parsing cleanup: state changes now route through lifecycle controls, legacy program and section fields were removed, and admins gained a console trigger for ETL pipelines. ([#5971](https://github.com/raft-tech/TANF-app/issues/5971), [#5984](https://github.com/raft-tech/TANF-app/issues/5984), [#6035](https://github.com/raft-tech/TANF-app/issues/6035))
- Security and API hardening closed: log file access now requires authentication, DataFile submissions take the user from the session, and file extension checks are stricter. ([#6126](https://github.com/raft-tech/TANF-app/issues/6126), [#6123](https://github.com/raft-tech/TANF-app/issues/6123), [#6131](https://github.com/raft-tech/TANF-app/issues/6131))
- FRA FY25 submissions were disabled, the FRA "Most recent" filter bug was fixed, and flaky Go Parser tests were resolved. ([#6096](https://github.com/raft-tech/TANF-app/issues/6096), [#6148](https://github.com/raft-tech/TANF-app/issues/6148), [#6049](https://github.com/raft-tech/TANF-app/issues/6049))
- SSP/STT frontend decoupling moved into Raft (Dev) Review, while User Requests and Data Table design returned from QASP Review to In Progress. ([#5376](https://github.com/raft-tech/TANF-app/issues/5376), [#5968](https://github.com/raft-tech/TANF-app/issues/5968), [#6137](https://github.com/raft-tech/TANF-app/issues/6137))
- Design work held in QASP Review: feedback STT-mode panel, download statistics panel, and optional upload notes. ([#6002](https://github.com/raft-tech/TANF-app/issues/6002), [#6012](https://github.com/raft-tech/TANF-app/issues/6012), [#6033](https://github.com/raft-tech/TANF-app/issues/6033))
- The Request Param Mismatch item stayed blocked. 22 open items moved on to the next sprint, including Keycloak canary rollout, FTANF research, the parsing service refactor, no-caseload design and research, and the Knowledge Center domain migration. ([#6051](https://github.com/raft-tech/TANF-app/issues/6051), [#5757](https://github.com/raft-tech/TANF-app/issues/5757), [#5683](https://github.com/raft-tech/TANF-app/issues/5683), [#5567](https://github.com/raft-tech/TANF-app/issues/5567), [#6020](https://github.com/raft-tech/TANF-app/issues/6020), [#6060](https://github.com/raft-tech/TANF-app/issues/6060), [#5916](https://github.com/raft-tech/TANF-app/issues/5916))

---

⚪️ **Total Issues:** 31  
✅ **Closed:** 9  
➡️ **Moved:** 3  
⬛️ **Unchanged:** 18  
🛑 **Blocked:** 1  

---

## [Prioritized User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4624)

- ⬛️ [Design Ideation: Explore Help Content and Naming for Report Pages (#5928)](https://github.com/raft-tech/TANF-app/issues/5928)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Operational Backlog](https://github.com/raft-tech/TANF-app/issues/4627)

- ✅ [Add Django Admin Console trigger for ETL pipelines (#6035)](https://github.com/raft-tech/TANF-app/issues/6035)  
_**Closed**_ - _Moved from **Closed**_  

- ⬛️ [[Bug] Fix statistical weights fiscal-year and source-file selection (#6143)](https://github.com/raft-tech/TANF-app/issues/6143)  
_Remained in **Current Sprint Backlog**_ - _Moved on to the next sprint_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Bug Report Backlog](https://github.com/raft-tech/TANF-app/issues/4969)

- ✅ [[BUG] “Most recent” filter includes older rejected FRA files (#6148)](https://github.com/raft-tech/TANF-app/issues/6148)  
_**Closed**_ - _Moved from **Closed**_  


## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ✅ [Route DataFile State Changes Through Lifecycle Controls (#5971)](https://github.com/raft-tech/TANF-app/issues/5971)  
_**Closed**_ - _Moved from **Closed**_  

- ⬛️ [Make DataFile State Transitions Atomic and Race-Safe (#5972)](https://github.com/raft-tech/TANF-app/issues/5972)  
_Remained in **Raft (Dev) Review**_ - _Moved on to the next sprint_  


## [(RE)Parsing refactor](https://github.com/raft-tech/TANF-app/issues/5565)

- ⬛️ [Introduce `ParsingService` and refactor Celery task to use it (#5567)](https://github.com/raft-tech/TANF-app/issues/5567)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ✅ [[Bug] Investigate flaky go-parser tests (#6049)](https://github.com/raft-tech/TANF-app/issues/6049)  
_**Closed**_ - _Moved from **Closed**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ⬛️ [Execute canary rollout of Keycloak auth (0% to 100%) per environment (#5757)](https://github.com/raft-tech/TANF-app/issues/5757)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  

- ⬛️ [Create GHCR robot accounts and CI/CD deployments for Keycloak (#5980)](https://github.com/raft-tech/TANF-app/issues/5980)  
_Remained in **Raft (Dev) Review**_ - _Moved on to the next sprint_  


## [TDP API access](https://github.com/raft-tech/TANF-app/issues/5786)

- ✅ [Infer `user` from session in DataFile submissions (#6123)](https://github.com/raft-tech/TANF-app/issues/6123)  
_**Closed**_ - _Moved from **Closed**_  

- ✅ [Require auth for `get_log_file` (#6126)](https://github.com/raft-tech/TANF-app/issues/6126)  
_**Closed**_ - _Moved from **Closed**_  


## [Design & Implement: Users Pages](https://github.com/raft-tech/TANF-app/issues/5952)

- ➡️ [Design: User Requests and Authorization Page and Interaction (#5968)](https://github.com/raft-tech/TANF-app/issues/5968)  
_Moved from **QASP Review** to **In Progress**_ - _Moved on to the next sprint_  


## [Allow admins to toggle Feedback Reports between STT and admin modes](https://github.com/raft-tech/TANF-app/issues/5991)

- ⬛️ [Design: Allow Regional Staff and Admin to view STT Mode for Feedback Reports via Statistics Panel (#6002)](https://github.com/raft-tech/TANF-app/issues/6002)  
_Remained in **QASP Review**_ - _Moved on to the next sprint_  

- ⬛️ [DEV: Allow admins to toggle Feedback Reports between STT and admin modes (#6003)](https://github.com/raft-tech/TANF-app/issues/6003)  
_Remained in **Raft (Dev) Review**_ - _Moved on to the next sprint_  


## [Migrate to tanfdata.acf.hhs.gov](https://github.com/raft-tech/TANF-app/issues/5993)

- ⬛️ [Migrate Knowledge Center to `.tanfdata.acf.hhs.gov` domain (#5916)](https://github.com/raft-tech/TANF-app/issues/5916)  
_Remained in **UX Review**_ - _Moved on to the next sprint_  


## [Support No-Caseload Reporting](https://github.com/raft-tech/TANF-app/issues/6000)

- ⬛️ [Design No-Caseload Reporting Experience (#6020)](https://github.com/raft-tech/TANF-app/issues/6020)  
_Remained in **UX Review**_ - _Moved on to the next sprint_  

- ⬛️ [Research: Planning & Facilitation for no caseload reporting (#6060)](https://github.com/raft-tech/TANF-app/issues/6060)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Feedback Report Download Statistics](https://github.com/raft-tech/TANF-app/issues/6011)

- ⬛️ [Design Feedback Report Download Statistics Panel (#6012)](https://github.com/raft-tech/TANF-app/issues/6012)  
_Remained in **QASP Review**_ - _Moved on to the next sprint_  


## [Optional Notes field for uploads](https://github.com/raft-tech/TANF-app/issues/6015)

- ⬛️ [Dev - Optional Notes Field for Feedback Report Uploads (#6017)](https://github.com/raft-tech/TANF-app/issues/6017)  
_Remained in **Raft (Dev) Review**_ - _Moved on to the next sprint_  

- ⬛️ [Design Optional Notes Field for Uploads (#6033)](https://github.com/raft-tech/TANF-app/issues/6033)  
_Remained in **QASP Review**_ - _Moved on to the next sprint_  


## [ACF-204: UX research for STT form and narrative submission, validation, and admin audit](https://github.com/raft-tech/TANF-app/issues/6059)

- ⬛️ [ACF-204: Create a minimal UX research plan (feasibility, preliminary research, approaches) (#6056)](https://github.com/raft-tech/TANF-app/issues/6056)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Decouple SSP and program participation from the STT model](https://github.com/raft-tech/TANF-app/issues/6062)

- ➡️ [Render upload and history sections from STT program participation (#5376)](https://github.com/raft-tech/TANF-app/issues/5376)  
_Moved from **In Progress** to **Raft (Dev) Review**_ - _Moved on to the next sprint_  

- ✅ [Disable FRA submissions for FY25 (#6096)](https://github.com/raft-tech/TANF-app/issues/6096)  
_**Closed**_ - _Moved from **Closed**_  


## [Developer Experience and Tooling](https://github.com/raft-tech/TANF-app/issues/6064)

- ⬛️ [[SPIKE] Consolidate overlapping tests and establish test-writing rules for contributors and agents (#6102)](https://github.com/raft-tech/TANF-app/issues/6102)  
_Remained in **Current Sprint Backlog**_ - _Moved on to the next sprint_  


## [Security Improvements](https://github.com/raft-tech/TANF-app/issues/6065)

- 🛑 [Request Param Mismatch (#6051)](https://github.com/raft-tech/TANF-app/issues/6051)  
_Remained in **Blocked**_ - _Moved on to the next sprint_  

- ✅ [Use `fullmatch` for DataFile extension check (#6131)](https://github.com/raft-tech/TANF-app/issues/6131)  
_**Closed**_ - _Moved from **Closed**_  


## [Complete canonical Program and Section on DataFile](https://github.com/raft-tech/TANF-app/issues/6066)

- ✅ [Remove legacy DataFile program and section enum fields. (#5984)](https://github.com/raft-tech/TANF-app/issues/5984)  
_**Closed**_ - _Moved from **Closed**_  


## [Convert Buildpacks to Docker](https://github.com/raft-tech/TANF-app/issues/6074)

- ⬛️ [Migrate Keycloak to Docker Hardened Images (#6089)](https://github.com/raft-tech/TANF-app/issues/6089)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Design & Implement: Data Table](https://github.com/raft-tech/TANF-app/issues/6136)

- ➡️ [Design: Data Table (#6137)](https://github.com/raft-tech/TANF-app/issues/6137)  
_Moved from **QASP Review** to **In Progress**_ - _Moved on to the next sprint_
