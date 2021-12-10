# Secret Key Management Strategy

Moving forward, the dev team will be taking additional precautions to protect the TDP system from unauthorized access. 

The goal of these efforts is to help prevent unintended secret key leakage. Though it isn't possible to completely eliminate the possibility of secret key leakage, the strategies documented herein will help improve incident response in the event where keys are leaked. 

## What are secret keys, and how can these be leaked?

As described [here](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/Architecture%20Decision%20Record/004-configuration-by-environment-variable.md), the TDP system is configured by environment variables. [Environment variables](https://medium.com/chingu/an-introduction-to-environment-variables-and-how-to-use-them-f602f66d15fa) help minimize the risk of running into unexpected issues when changes are made to the system. Some of these environment variables are senstive because these are used to authorize access to TDP. We refer to these as "Secret keys". 

If secret keys are leaked/exposed, this can not only change how the TDP system functions, but this also compromises the security of the data files flowing through the system (and the individuals and families represented in these data). There are two primary avenues that secret key leakage can happen: 
- a security breach in one or more of the project tools (e.g. GitHub, CircleCi, [CodeCov](https://about.codecov.io/security-update/), Cloud.gov, Docker) that use or rely on secret keys  (*relatively speaking, this is challenging to prevent*), or 
- a team member with access to the secret keys leaks them (*this is usually unintentional*)

## Mitigation steps
Below are a list of steps the team is taking to help mitigate the incidence of secret key leakage and stay up-to-date on news that could potentially compromise the security state of our TDP system. This may be updated over time, as additional or alternative solutions are adopted. 

### Current practices
- Use `git status` terminal command before any commits and pushes to github repo. This should help detect any secret key files that have been modified prior to `git commit`. 
- Prioritize updating [gitignore](https://git-scm.com/docs/gitignore) before submitting any follow-on PRs that involve use of files that include secret keys. This will prevent any files that contain secret keys from being committed to the repo. 
- Secret keys are to be retrieved from cloud.gov for local development purposes. Cloud.gov is a platform that requires these keys, and the dev team has access to the keys stored in the dev environment space. Therefore, this is a more secure approach for retrieving keys than relying on team members to share keys across other platforms/tools.  
- No production keys will be stored on local machines, since this is unnecessary for development work.  In the event of unintended secret key leakage, this would have no impact on the production environment. Only people who have access to the production space in Cloud.gov will have access to prod keys.
- At a minimum, ACF and vendor Tech Leads should be subscribed to tech tools we use to stay up-to-date on news that could impact project security. This includes: CircleCi, CodeCov, GitHub, Cloud.gov, Docker
- As part of ACF Tech Lead's review of environment variables, secret key rotation will be coordinated. These reviews will take place quarterly or prior to each release (whichever is sooner).

### Longer-term solutions to be implemented (these are housed under epic [#972](https://github.com/raft-tech/TANF-app/issues/972)):
- Automated tool will be added to detect secret keys before local developers can commit changes to project repo ([#965](https://github.com/raft-tech/TANF-app/issues/965)) 
- Add .dockerconfig file as an extra layer of security against accidentally leaking secrets as part of local development ([#544](https://github.com/raft-tech/TANF-app/issues/544))
- Automated testing step will be added in CircleCI to check for secret keys and stop the CI process if keys are detected ([#966](https://github.com/raft-tech/TANF-app/issues/966))
- `DJANGO_SECRET_KEY` is automatically generated for initial deployments to Cloud.gov. This will ensure that the key is not shared across any environments and never needs to be exposed to developers or stored outside of Cloud.gov ([#967](https://github.com/raft-tech/TANF-app/issues/967))
- Perform validation on Codecov Bash Uploader script during CI steps to ensure that it has not been tampered with before allowing it to execute in CI. ([#968](https://github.com/raft-tech/TANF-app/issues/968))
- The `JWT_KEY (JWT_CERT_TEST)`  that is used for testing will be dynamically generated to allow us to reduce the number of keys stored in CI/CD environment variables. ([#969](https://github.com/raft-tech/TANF-app/issues/969))
- Secret keys will be rotated whenever team members rotate off the project. We will soon be leveraging Terraform to automate provisioning of services (e.g. S3, RDS) and eventually to manage users with access to our cloud.gov environments, so the vision is to automate the process of rotating secret keys whenever our user list changes.  ([#1004](https://github.com/raft-tech/TANF-app/issues/1004))
## Communication protocol if secret keys are leaked
Any member of the TDP who notices secret key leakage should alert the full TDP project team immediately as follows:

- Send alert via Microsoft Teams `General` channel and be sure to cc: Product Owner, ACF Tech Lead, Product Manager, vendor Tech Lead. If Teams isn't available, please send an email and also alert team members via Mattermost. 

- Include details of the leakage, which should include:
    - where the leakage ocurred
    - how the leakage occurred (if known)
    - preliminary assessment of the scope of the leakage (e.g. was PII compromised? exposed?)
    - Next steps (e.g. schedule mtg to discuss incident response plan, rotate keys, etc.)
