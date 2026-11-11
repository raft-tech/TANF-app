# Sprint Summary: Oct 28, 2026 - Nov 10, 2026

## Overview

- Closed the design work for the Feedback Report download statistics panel, the STT mode view of Feedback Reports, and optional upload notes. ([#6012](https://github.com/raft-tech/TANF-app/issues/6012), [#6002](https://github.com/raft-tech/TANF-app/issues/6002), [#6033](https://github.com/raft-tech/TANF-app/issues/6033))
- Closed the design for the User Requests and Authorization page, and closed the work that makes DataFile state transitions atomic and race-safe. ([#5968](https://github.com/raft-tech/TANF-app/issues/5968), [#5972](https://github.com/raft-tech/TANF-app/issues/5972))
- Closed the buildpack upgrade, supporting the move of the platform to Docker. ([#6178](https://github.com/raft-tech/TANF-app/issues/6178))
- Moved the Feedback Report admin and STT mode toggle and the optional upload notes field into UX Review, and moved the no-caseload reporting design and the ACF-204 UX research plan into QASP Review. ([#6003](https://github.com/raft-tech/TANF-app/issues/6003), [#6017](https://github.com/raft-tech/TANF-app/issues/6017), [#6020](https://github.com/raft-tech/TANF-app/issues/6020), [#6056](https://github.com/raft-tech/TANF-app/issues/6056))
- Keycloak work continued: the canary rollout and the GHCR robot account and deployment setup are blocked, while environment variable cleanup and the Docker migration document are in Raft (Dev) Review. ([#5757](https://github.com/raft-tech/TANF-app/issues/5757), [#5980](https://github.com/raft-tech/TANF-app/issues/5980), [#6163](https://github.com/raft-tech/TANF-app/issues/6163), [#6176](https://github.com/raft-tech/TANF-app/issues/6176))
- 24 open items moved on to the next sprint, including API access hardening, FTANF research, the parsing service refactor, and the Knowledge Center domain migration. ([#6125](https://github.com/raft-tech/TANF-app/issues/6125), [#5683](https://github.com/raft-tech/TANF-app/issues/5683), [#5567](https://github.com/raft-tech/TANF-app/issues/5567), [#5916](https://github.com/raft-tech/TANF-app/issues/5916))

---

⚪️ **Total Issues:** 30  
✅ **Closed:** 6  
➡️ **Moved:** 6  
⬛️ **Unchanged:** 16  
🛑 **Blocked:** 2  

---


## [Prioritized User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4624)

- ⬛️ [Design Ideation: Explore Help Content and Naming for Report Pages (#5928)](https://github.com/raft-tech/TANF-app/issues/5928)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Operational Backlog](https://github.com/raft-tech/TANF-app/issues/4627)

- ➡️ [[Bug] Fix statistical weights fiscal-year and source-file selection (#6143)](https://github.com/raft-tech/TANF-app/issues/6143)  
_Moved from **Current Sprint Backlog** to **In Progress**_ - _Moved on to the next sprint_  

- ✅ [Upgrade buildpacks (#6178)](https://github.com/raft-tech/TANF-app/issues/6178)  
_**Closed**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  

- ⬛️ [[Spike] Design output for a human readable submission file converter (#6168)](https://github.com/raft-tech/TANF-app/issues/6168)  
_Remained in **Current Sprint Backlog**_ - _Moved on to the next sprint_  


## [TDP Knowledge Center](https://github.com/raft-tech/TANF-app/issues/5455)

- ⬛️ [Create Vendor-Facing Knowledge Center Bulletin on Tribal TANF Sanction Reporting (#6179)](https://github.com/raft-tech/TANF-app/issues/6179)  
_Remained in **QASP Review**_ - _Moved on to the next sprint_  


## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ✅ [Make DataFile State Transitions Atomic and Race-Safe (#5972)](https://github.com/raft-tech/TANF-app/issues/5972)  
_**Closed**_  


## [(RE)Parsing refactor](https://github.com/raft-tech/TANF-app/issues/5565)

- ⬛️ [Introduce `ParsingService` and refactor Celery task to use it (#5567)](https://github.com/raft-tech/TANF-app/issues/5567)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ⬛️ [7. Add Admin Console Deployment and Cloud.gov Runtime Configuration (#5846)](https://github.com/raft-tech/TANF-app/issues/5846)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- 🛑 [Execute canary rollout of Keycloak auth (0% to 100%) per environment (#5757)](https://github.com/raft-tech/TANF-app/issues/5757)  
_Moved from **In Progress** to **Blocked**_ - _Moved on to the next sprint_  

- 🛑 [Create GHCR robot accounts and CI/CD deployments for Keycloak (#5980)](https://github.com/raft-tech/TANF-app/issues/5980)  
_Moved from **Raft (Dev) Review** to **Blocked**_ - _Moved on to the next sprint_  

- ⬛️ [Clean up Keycloak environment variables (#6163)](https://github.com/raft-tech/TANF-app/issues/6163)  
_Remained in **Raft (Dev) Review**_ - _Moved on to the next sprint_  


## [TDP API access](https://github.com/raft-tech/TANF-app/issues/5786)

- ⬛️ [Enforce `has_fra_access` on backend `GET` requests (#6125)](https://github.com/raft-tech/TANF-app/issues/6125)  
_Remained in **Raft (Dev) Review**_ - _Moved on to the next sprint_  

- ⬛️ [Clean up Swagger documentation for API submissions (#6127)](https://github.com/raft-tech/TANF-app/issues/6127)  
_Remained in **Current Sprint Backlog**_ - _Moved on to the next sprint_  


## [Design & Implement: Users Pages](https://github.com/raft-tech/TANF-app/issues/5952)

- ✅ [Design: User Requests and Authorization Page and Interaction (#5968)](https://github.com/raft-tech/TANF-app/issues/5968)  
_**Closed**_  


## [Create GHCR robot accounts and CI/CD deployments for Keycloak](https://github.com/raft-tech/TANF-app/issues/5980)

- ⬛️ [Update Docker migration document and SIA for public images (#6176)](https://github.com/raft-tech/TANF-app/issues/6176)  
_Remained in **Raft (Dev) Review**_ - _Moved on to the next sprint_  


## [Allow admins to toggle Feedback Reports between STT and admin modes](https://github.com/raft-tech/TANF-app/issues/5991)

- ✅ [Design: Allow Regional Staff and Admin to view STT Mode for Feedback Reports via Statistics Panel (#6002)](https://github.com/raft-tech/TANF-app/issues/6002)  
_**Closed**_  

- ➡️ [DEV: Allow admins to toggle Feedback Reports between STT and admin modes (#6003)](https://github.com/raft-tech/TANF-app/issues/6003)  
_Moved from **Raft (Dev) Review** to **UX Review**_ - _Moved on to the next sprint_  


## [Migrate to tanfdata.acf.hhs.gov](https://github.com/raft-tech/TANF-app/issues/5993)

- ⬛️ [Migrate Knowledge Center to `.tanfdata.acf.hhs.gov` domain (#5916)](https://github.com/raft-tech/TANF-app/issues/5916)  
_Remained in **UX Review**_ - _Moved on to the next sprint_  


## [Support No-Caseload Reporting](https://github.com/raft-tech/TANF-app/issues/6000)

- ➡️ [Design No-Caseload Reporting Experience (#6020)](https://github.com/raft-tech/TANF-app/issues/6020)  
_Moved from **UX Review** to **QASP Review**_ - _Moved on to the next sprint_  

- ⬛️ [Research: Planning & Facilitation for no caseload reporting (#6060)](https://github.com/raft-tech/TANF-app/issues/6060)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Feedback Report Download Statistics](https://github.com/raft-tech/TANF-app/issues/6011)

- ✅ [Design Feedback Report Download Statistics Panel (#6012)](https://github.com/raft-tech/TANF-app/issues/6012)  
_**Closed**_  


## [Optional Notes field for uploads](https://github.com/raft-tech/TANF-app/issues/6015)

- ➡️ [Dev - Optional Notes Field for Feedback Report Uploads (#6017)](https://github.com/raft-tech/TANF-app/issues/6017)  
_Moved from **Raft (Dev) Review** to **UX Review**_ - _Moved on to the next sprint_  

- ✅ [Design Optional Notes Field for Uploads (#6033)](https://github.com/raft-tech/TANF-app/issues/6033)  
_**Closed**_  


## [ACF-204: UX research for STT form and narrative submission, validation, and admin audit](https://github.com/raft-tech/TANF-app/issues/6059)

- ➡️ [ACF-204: Create a minimal UX research plan (feasibility, preliminary research, approaches) (#6056)](https://github.com/raft-tech/TANF-app/issues/6056)  
_Moved from **In Progress** to **QASP Review**_ - _Moved on to the next sprint_  


## [Decouple SSP and program participation from the STT model](https://github.com/raft-tech/TANF-app/issues/6062)

- ⬛️ [Render upload and history sections from STT program participation (#5376)](https://github.com/raft-tech/TANF-app/issues/5376)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  

- ⬛️ [Configure fiscal-year submission eligibility per STT Section (#6095)](https://github.com/raft-tech/TANF-app/issues/6095)  
_Remained in **Current Sprint Backlog**_ - _Moved on to the next sprint_  


## [Convert Buildpacks to Docker](https://github.com/raft-tech/TANF-app/issues/6074)

- ⬛️ [Migrate Keycloak to Docker Hardened Images (#6089)](https://github.com/raft-tech/TANF-app/issues/6089)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Design & Implement: Data Table](https://github.com/raft-tech/TANF-app/issues/6136)

- ⬛️ [Design: Data Table (#6137)](https://github.com/raft-tech/TANF-app/issues/6137)  
_Remained in **QASP Review**_ - _Moved on to the next sprint_  


## [Audit Testing](https://github.com/raft-tech/TANF-app/issues/6199)

- ➡️ [[SPIKE] Consolidate overlapping tests and establish test-writing rules for contributors and agents (#6102)](https://github.com/raft-tech/TANF-app/issues/6102)  
_Moved from **Current Sprint Backlog** to **In Progress**_ - _Moved on to the next sprint_
