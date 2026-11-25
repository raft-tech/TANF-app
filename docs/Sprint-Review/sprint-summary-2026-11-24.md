# Sprint Summary: Nov 11, 2026 - Nov 24, 2026

## Overview

- Closed the Keycloak environment variable cleanup, the Knowledge Center move to the new tanfdata.acf.hhs.gov domain, and the API check that backend read requests require FRA access. ([#6163](https://github.com/raft-tech/TANF-app/issues/6163), [#5916](https://github.com/raft-tech/TANF-app/issues/5916), [#6125](https://github.com/raft-tech/TANF-app/issues/6125))
- Closed the no-caseload reporting design, the admin toggle that switches Feedback Reports between STT and admin modes, and the vendor-facing Knowledge Center bulletin on Tribal TANF sanction reporting. ([#6020](https://github.com/raft-tech/TANF-app/issues/6020), [#6003](https://github.com/raft-tech/TANF-app/issues/6003), [#6179](https://github.com/raft-tech/TANF-app/issues/6179))
- Closed the test cleanup spike, the custom database views for the data pipeline, and the spike on too many alerts in the dev alerts channel. ([#6102](https://github.com/raft-tech/TANF-app/issues/6102), [#6217](https://github.com/raft-tech/TANF-app/issues/6217), [#6165](https://github.com/raft-tech/TANF-app/issues/6165)) The statistical weights bug fix was also closed shortly after the sprint ended. ([#6143](https://github.com/raft-tech/TANF-app/issues/6143))
- Keycloak work still has two blocked items: the canary rollout and the container registry robot account setup. The ACF-204 UX research plan is also blocked. ([#5757](https://github.com/raft-tech/TANF-app/issues/5757), [#5980](https://github.com/raft-tech/TANF-app/issues/5980), [#6056](https://github.com/raft-tech/TANF-app/issues/6056))
- The Data Table design and the no-caseload research moved from QASP Review back to In Progress. ([#6137](https://github.com/raft-tech/TANF-app/issues/6137), [#6060](https://github.com/raft-tech/TANF-app/issues/6060))
- 23 open items moved on to the next sprint, including FTANF research, the parsing service refactor, the Go parser checks, and the Okta migration. ([#5683](https://github.com/raft-tech/TANF-app/issues/5683), [#5567](https://github.com/raft-tech/TANF-app/issues/5567), [#6156](https://github.com/raft-tech/TANF-app/issues/6156), [#6218](https://github.com/raft-tech/TANF-app/issues/6218))

---

⚪️ **Total Issues:** 33  
✅ **Closed:** 9  
➡️ **Moved:** 5  
⬛️ **Unchanged:** 16  
🛑 **Blocked:** 3  

---

## [Prioritized User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4624)

- ⬛️ [Design Ideation: Explore Help Content and Naming for Report Pages (#5928)](https://github.com/raft-tech/TANF-app/issues/5928)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Operational Backlog](https://github.com/raft-tech/TANF-app/issues/4627)

- ➡️ [[Bug] Fix statistical weights fiscal-year and source-file selection (#6143)](https://github.com/raft-tech/TANF-app/issues/6143)  
_Moved from **Raft (Dev) Review** to **Closed**_  

- ✅ [[SPIKE] Investigate excessive alerts in TDP Dev Alerts channel (#6165)](https://github.com/raft-tech/TANF-app/issues/6165)  
_**Closed**_  

- ➡️ [Add feedback report download-statistics table to Grafana for DIGIT team (#6181)](https://github.com/raft-tech/TANF-app/issues/6181)  
_Moved from **Raft (Dev) Review** to **In Progress**_ - _Moved on to the next sprint_  

- ⬛️ [Update ETL `PipelineDefinition` to have a `completion_keys` for run finalization (#6183)](https://github.com/raft-tech/TANF-app/issues/6183)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  

- ✅ [Add custom psql views to pipeline (#6217)](https://github.com/raft-tech/TANF-app/issues/6217)  
_**Closed**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  

- ⬛️ [[Spike] Design output for a human readable submission file converter (#6168)](https://github.com/raft-tech/TANF-app/issues/6168)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Bug Report Backlog](https://github.com/raft-tech/TANF-app/issues/4969)

- ⬛️ [[Bug] Redis cache reads can hang requests until Gunicorn aborts workers (#6169)](https://github.com/raft-tech/TANF-app/issues/6169)  
_Remained in **Raft (Dev) Review**_ - _Moved on to the next sprint_  


## [TDP Knowledge Center](https://github.com/raft-tech/TANF-app/issues/5455)

- ✅ [Create Vendor-Facing Knowledge Center Bulletin on Tribal TANF Sanction Reporting (#6179)](https://github.com/raft-tech/TANF-app/issues/6179)  
_**Closed**_  


## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ⬛️ [Refine stuck-file notifications to report the latest actionable submission across fiscal years (#6142)](https://github.com/raft-tech/TANF-app/issues/6142)  
_Remained in **Raft (Dev) Review**_ - _Moved on to the next sprint_  


## [(RE)Parsing refactor](https://github.com/raft-tech/TANF-app/issues/5565)

- ⬛️ [Introduce `ParsingService` and refactor Celery task to use it (#5567)](https://github.com/raft-tech/TANF-app/issues/5567)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ⬛️ [7. Add Admin Console Deployment and Cloud.gov Runtime Configuration (#5846)](https://github.com/raft-tech/TANF-app/issues/5846)  
_Remained in **Raft (Dev) Review**_ - _Moved on to the next sprint_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ⬛️ [Establish parity checks between Go and Python parser outputs (#6156)](https://github.com/raft-tech/TANF-app/issues/6156)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- 🛑 [Execute canary rollout of Keycloak auth (0% to 100%) per environment (#5757)](https://github.com/raft-tech/TANF-app/issues/5757)  
_Remained in **Blocked**_  

- 🛑 [Create GHCR robot accounts and CI/CD deployments for Keycloak (#5980)](https://github.com/raft-tech/TANF-app/issues/5980)  
_Remained in **Blocked**_  

- ✅ [Clean up Keycloak environment variables (#6163)](https://github.com/raft-tech/TANF-app/issues/6163)  
_**Closed**_  

- ⬛️ [Migrate AMS authentication to Okta (#6218)](https://github.com/raft-tech/TANF-app/issues/6218)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [TDP API access](https://github.com/raft-tech/TANF-app/issues/5786)

- ✅ [Enforce `has_fra_access` on backend `GET` requests (#6125)](https://github.com/raft-tech/TANF-app/issues/6125)  
_**Closed**_  

- ⬛️ [Clean up Swagger documentation for API submissions (#6127)](https://github.com/raft-tech/TANF-app/issues/6127)  
_Remained in **In Progress**_ - _Moved on to the next sprint_  


## [Create GHCR robot accounts and CI/CD deployments for Keycloak](https://github.com/raft-tech/TANF-app/issues/5980)

- ⬛️ [Update Docker migration document and SIA for public images (#6176)](https://github.com/raft-tech/TANF-app/issues/6176)  
_Remained in **QASP Review**_ - _Moved on to the next sprint_  


## [Allow admins to toggle Feedback Reports between STT and admin modes](https://github.com/raft-tech/TANF-app/issues/5991)

- ✅ [DEV: Allow admins to toggle Feedback Reports between STT and admin modes (#6003)](https://github.com/raft-tech/TANF-app/issues/6003)  
_**Closed**_  


## [Migrate to tanfdata.acf.hhs.gov](https://github.com/raft-tech/TANF-app/issues/5993)

- ✅ [Migrate Knowledge Center to `.tanfdata.acf.hhs.gov` domain (#5916)](https://github.com/raft-tech/TANF-app/issues/5916)  
_**Closed**_  


## [Support No-Caseload Reporting](https://github.com/raft-tech/TANF-app/issues/6000)

- ✅ [Design No-Caseload Reporting Experience (#6020)](https://github.com/raft-tech/TANF-app/issues/6020)  
_**Closed**_  

- ➡️ [Research: Planning & Facilitation for no caseload reporting (#6060)](https://github.com/raft-tech/TANF-app/issues/6060)  
_Moved from **QASP Review** to **In Progress**_ - _Moved on to the next sprint_  


## [Optional Notes field for uploads](https://github.com/raft-tech/TANF-app/issues/6015)

- ⬛️ [Dev - Optional Notes Field for Feedback Report Uploads (#6017)](https://github.com/raft-tech/TANF-app/issues/6017)  
_Remained in **UX Review**_ - _Moved on to the next sprint_  


## [ACF-204: UX research for STT form and narrative submission, validation, and admin audit](https://github.com/raft-tech/TANF-app/issues/6059)

- 🛑 [ACF-204: Create a minimal UX research plan (feasibility, preliminary research, approaches) (#6056)](https://github.com/raft-tech/TANF-app/issues/6056)  
_Remained in **Blocked**_  


## [Decouple SSP and program participation from the STT model](https://github.com/raft-tech/TANF-app/issues/6062)

- ⬛️ [Render upload and history sections from STT program participation (#5376)](https://github.com/raft-tech/TANF-app/issues/5376)  
_Remained in **Raft (Dev) Review**_ - _Moved on to the next sprint_  

- ⬛️ [Configure fiscal-year submission eligibility per STT Section (#6095)](https://github.com/raft-tech/TANF-app/issues/6095)  
_Remained in **Current Sprint Backlog**_ - _Moved on to the next sprint_  


## [Convert Buildpacks to Docker](https://github.com/raft-tech/TANF-app/issues/6074)

- ⬛️ [Migrate Keycloak to Docker Hardened Images (#6089)](https://github.com/raft-tech/TANF-app/issues/6089)  
_Remained in **Raft (Dev) Review**_ - _Moved on to the next sprint_  


## [Design & Implement: Data Table](https://github.com/raft-tech/TANF-app/issues/6136)

- ➡️ [Design: Data Table (#6137)](https://github.com/raft-tech/TANF-app/issues/6137)  
_Moved from **QASP Review** to **In Progress**_ - _Moved on to the next sprint_  


## [Audit Testing](https://github.com/raft-tech/TANF-app/issues/6199)

- ✅ [[SPIKE] Consolidate overlapping tests and establish test-writing rules for contributors and agents (#6102)](https://github.com/raft-tech/TANF-app/issues/6102)  
_**Closed**_  

- ➡️ [Task: Optimize backend pytest in-process execution speed (password hasher) (#6214)](https://github.com/raft-tech/TANF-app/issues/6214)  
_Moved from **Planned for Next Sprint** to **Current Sprint Backlog**_ - _Moved on to the next sprint_
