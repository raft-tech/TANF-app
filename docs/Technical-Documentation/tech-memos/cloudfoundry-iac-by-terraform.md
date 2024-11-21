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

### CircleCI workflows

### Bash Deploy scripts

### Manifests

### New Terraform architecture

## Affected Systems
provide a list of systems this feature will depend on/change.

## Use and Test cases to consider
provide a list of use cases and test cases to be considered when the feature is being implemented.
