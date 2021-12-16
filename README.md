# Temporary Assistance for Needy Families (TANF) Data Portal - TDP

Welcome to the project for the New TANF Data Reporting System (i.e. TANF Data Portal)!

Our vision is to build a new, secure, web-based data reporting system to improve the federal reporting experience for TANF grantees and federal staff. The new system will allow grantees to easily submit accurate data and be confident that they have fulfilled their reporting requirements. This will reduce the burden on all users, improve data quality, lead to better policy and program decision-making, and ultimately help low-income families.

## Current Build

|| Raft-Tech(raft-tdp-main) |  HHS(main) |
|---|---|---|
|**Build**| [![CircleCI-Dev](https://circleci.com/gh/raft-tech/TANF-app/tree/raft-tdp-main.svg?style=shield)](https://circleci.com/gh/raft-tech/TANF-app/tree/raft-tdp-main) | [![CircleCI-HHS](https://circleci.com/gh/HHS/TANF-app/tree/main.svg?style=shield)](https://circleci.com/gh/HHS/TANF-app/tree/main)|
|**Security**| [Dependabot-Dev](https://github.com/raft-tech/TANF-app/security/dependabot) | [Advisories-HHS](https://github.com/HHS/TANF-app/security/advisories) |
|**Frontend Coverage**| [![Codecov-Frontend-Dev](https://codecov.io/gh/raft-tech/TANF-app/branch/raft-tdp-main/graph/badge.svg?flag=dev-frontend)](https://codecov.io/gh/raft-tech/TANF-app?flag=dev-frontend) | [![Codeco-Frontend-HHS](https://codecov.io/gh/HHS/TANF-app/branch/main/graph/badge.svg?flag=main-frontend)](https://codecov.io/gh/HHS/TANF-app?flag=main-frontend)   |
|**Backend Coverage**|  [![Codecov-Backend-Dev](https://codecov.io/gh/raft-tech/TANF-app/branch/raft-tdp-main/graph/badge.svg?flag=dev-backend)](https://codecov.io/gh/raft-tech/TANF-app/branch/raft-tdp-main?flag=dev-backend)|   [![Codecov-Backend-HHS]( https://codecov.io/gh/HHS/TANF-app/branch/main/graph/badge.svg?flag=main-backend)](https://codecov.io/gh/HHS/TANF-app/branch/main?flag=main-backend) |

**Due to limitations imposed by Github and occasional slow server response times, some badges may require a page refresh to load.**

# Table of Contents

+ **[Acquisition](./docs/Acquisition)**: Acquisition processes; Contracting Officer's Representative documents
+ **[Background](./docs/Background)**: Project, agency, legacy system, and program background
+ **[Design](./Design)**: Design guide and design principles
+ **[How-We-Work](./docs/How-We-Work)**: Team composition, charter, and workflows
+ **[Product-Strategy](./Product-Strategy)**: Vision, roadmap, planning, and product resources
+ **[Prototype](./docs/Prototype)**: Documentation for the initial prototype
+ **[Security-Compliance](./Security-Compliance)**: Supplementary information in support of the ATO process
+ **[Sprint-Review](./docs/Sprint-Review)**: Summaries of delivered stories per sprint
+ **[Technical-Documentation](./docs/Technical-Documentation)**: System documentation; technical workflows
+ **[User-Research](./docs/User-Research)**: Research-related project background, strategy and planning documents, and research syntheses
+ **[Frontend](./tdrs-frontend)**: Frontend ReactJS codebase
+ **[Backend](./tdrs-backend)**: Django codebase for backend
+ **[Figma](./docs/User-Research#mural-links):** UX Figma links 
+ **[MURAL](https://app.mural.co/t/raft2792):** Raft Mural for planning
+ **[HHS Teams](https://teams.microsoft.com/_#/conversations/General)**: HHS Microsoft Teams chat service with lots of additional resources like OneNote, etc.
+ **[Zenhub](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/board?repos=281707402)**: Direct link to our Zenhub sprint board for those not using the [Zenhub browser extension](https://www.zenhub.com/extension)


## Infrastructure

TDP Uses Infrastructure as Code (IaC) and DevSecOps automation

### Authentication

[Login.gov](https://login.gov/) TDP requires strong multi-factor authentication for the states, tribes, and territories and Personal Identity Verification (PIV) authentication for OFA staff. Login.gov is being used to meet both of these requirements. 

### Cloud Environment

[Cloud.gov](https://cloud.gov/) is being used as the cloud environment. This platform-as-a-service (PaaS) removes almost all of the infrastructure monitoring and maintenance from the system, is already procured for OFA, and has a FedRAMP Joint Authorization Board Provisional Authority to Operate (JAB P-ATO) on file. 

## CI/CD Pipelines with CircleCI

### Continuous Integration (CI)

On each git push and merge, a comprehensive list of automated checks are run: Unit tests ([Jest](https://jestjs.io/),, Linting tests ([ESLint](https://eslint.org/), Accessibility tests ([Pa11y](https://pa11y.org/)), and Security Scanning ([OWASP ZAP](https://owasp.org/www-project-zap/)). The configurations for CI are kept in [`.circleci/config.yml`](https://github.com/HHS/TANF-app/blob/main/.circleci/config.yml). 

### Continuous Deployment

The application is continuously deployed to the dev, vendor staging, gov staging or prod environments based on the git branch the code is merged in. The configuration for different branches is maintained in [`.circleci/config.yml`](https://github.com/HHS/TANF-app/blob/main/.circleci/config.yml#L107).

See [Architecture Decision Record 008 - Deployment Flow](docs/Architecture%20Decision%20Record/008-deployment-flow.md) - for more.