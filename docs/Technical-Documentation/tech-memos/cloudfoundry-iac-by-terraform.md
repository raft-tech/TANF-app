# CloudFoundry IAC

**Audience**: TDP Software Engineers <br>
**Subject**:  CloudFoundry: Infrastructure as Code <br>
**Date**:     Nov 21st, 2024 <br>

## Summary
At present, our Cloud.gov apps are managed through a combination of bite-size manifests for each, bash shell scripts which deploy, and CircleCI YAML pipelines which orchestrate. The bash scripts nor CircleCI pipelines are not stateful but rather fire-and-forget and fail to be truly idempotent

## Background (Optional)
In calls with Cloud.gov's tailored support team, we were pushed to utilize the [new cloudfoundry-community providers](https://github.com/cloud-gov/deploy-cf/tree/main/terraform) for Terraform to manage our apps and spaces. As we already use Terraform, this is a logical evolution of that IaC. Previously we sought to use the cf provider but the functionality was limited and documentation incorrect leading to an inability to utilize those services; I believe this might be the old version [here](https://registry.terraform.io/providers/cloudfoundry-community/cloudfoundry/latest/docs). We will be exploring these new providers in hope to move off our archiac, if functional, bash scripts.

## Out of Scope
For this first pass, we will seek to simply implement what already exists in the three buckets of manifests, bash, and CircleCI into Terraform configurations and will not attempt improvements or restructuring of our environments or spaces.

## Method/Design

### Manifests
Under `tdrs-backend/`, we have 5 manifests:
- manifest.buildpack.yml: defines the backend python buildpack/OS used in production.
- manifest.clamav.yml: defines docker image `rafttech/clamav` for use by our app's virus scanning service.
- manifest.kibana.yml: defines docker image `oss/kibana` for use for data access. Obsolete.
- manifest.proxy.yml: defines docker image `rafttech/aws-es-proxy` presumably for use with Kibana. Obsolete?
- manifest.yml: references a `{{docker-backend}}` variable. I see references to manifest.yml under PLG but unsure what this is. Created 4 years ago but unsure if used?

Under `tdrs-frontend/`, we have just 2 manifests:
- manifest.buildpack.yml: defines the frontend nginx buildpack/OS used in production.
- manifest.yml: references a `{{docker-frontend}}` variable. Unused?

### Bash Deploy scripts
- `deploy-backend.sh`: Used in CircleCI pipelines to not only push `tdrs-backend/` manifests but also manage environment variables, Cloud.gov services, network policies, our monitoring apps, and connecting corresponding frontend apps.
- `deploy-frontend.sh`: Used in CircleCI pipelines to push `tdrs-frontend/manifest.buildback.yml`
- `deploy-infrastructure-dev.sh` and `deploy-infrastructure-staging.sh`: Used for a developer to kick off circleci deployments from their machine.
- `deploy-tdp-product-update-site.sh`: Responsible for knowledge center with staticfiles buildpack under `product-updates/`.

### CircleCI workflows
Under `.circleci/deployment/workflows.yml`, we have dozens of workflows to target specific branches or spaces in a duplicative manner.
`deploy-infrastructure-{space}`: These similarly call `deploy-infrastructure` with various parameters to invoke our existing Terraform configurations.
- `build-and-tag-{space}`: These have jobs underneath them which call the command `build-and-tag-images` which simply performs setup for a call to `./scripts/build-and-tag-images.sh ` for uploading docker images to Nexus.
-`deploy-{space}`: calls the command `deploy-cloud-dot-gov` which underneath runs scripts underneath in this order:
  - ./scripts/apply-remote-migrations.sh
  - ./scripts/deploy-backend.sh
  - ./scripts/deploy-frontend.sh
- `prod-deploy-clamav`: Redeploys our virus scanner image in tanf-prod space.
- `deploy-project-updates-site`: Runs `deploy-tdp-product-update-site.sh`.
- `enable-versioning`: ensures s3 versioning flags are toggled on for apps/spaces x4 (dev, develop, staging, prod)

### Pre-existing Terraform scope
Luckily, we already have CircleCI invoking Terraform under the command `deploy-infrastructure` utilizes by the aforementioned workflows. It procures four service instances for us per space: two s3 buckets (static and datafiles), relational database service (RDS), and elasticsearch.

## New Terraform architecture
Moving to a more stateful infrastructure-as-code versus a collection of scripts, we will attempt to have Terraform manage [CF apps](https://registry.terraform.io/providers/cloudfoundry-community/cloudfoundry/latest/docs/resources/app), [network policies](https://registry.terraform.io/providers/cloudfoundry-community/cloudfoundry/latest/docs/resources/network_policy), [routes](https://registry.terraform.io/providers/cloudfoundry-community/cloudfoundry/latest/docs/resources/route), and [services](https://registry.terraform.io/providers/cloudfoundry-community/cloudfoundry/latest/docs/resources/service_instance). With regard to routes, domains -- this has been handled manually by administrators to get ACF-branded domain names for our web app URLs (e.g., `https://tanfdata.acf.hhs.gov`).

To obsolesce our `deploy-backend` and `deploy-frontend` scripts, we'll need to accomplish the following:
- First steps will be to manage our apps under Terraform instead of CircleCI orchestration of our scripts running `cf push` on various manifests.
- Next would be to ensure our apps can talk to each other as necessary with network policies and routes as we have a complicated network running proxies between our three spaces.
-As our services are infrequently updated, they would be added last for polish and holistic visibility and ensuring connectivity.

TODO: need to review Eric's PLG deploy script and map that flow out for future work.

## Affected Systems
These proposed changes will affect all Cloud.gov infrastructure as well as CircleCI pipelines both for HHS and raft-tech instances.

## Use and Test cases to consider
provide a list of use cases and test cases to be considered when the feature is being implemented.

### Use Cases
Regular feature work
Merge to develop
Releases
  also hhs:main->hhs:master
Crashed app(s)

### Test Cases
From scratch
  with carve out for RDS as we can't automate creation of named databases
From mixed existing/not existing
From downed/crashed
From stable