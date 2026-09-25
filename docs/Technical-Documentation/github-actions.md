# How We Use GitHub Actions
GitHub Actions provides path, pull-request, and label filtering before triggering deployment jobs in CircleCI. It also publishes container images to GHCR with the repository-scoped `GITHUB_TOKEN`, including release images and the Keycloak image. See this [CircleCI guidance](https://circleci.com/blog/trigger-circleci-pipeline-github-action/) for the trigger model; this repository uses `promiseofcake/circleci-trigger-action` rather than `circleci/trigger_circleci_pipeline`.

## Path Filtering
Actions filters CircleCI workflows by sending pipeline parameters through the CircleCI API trigger. The Keycloak workflow first publishes an immutable multi-platform image, then sends its digest to a deployment-only CircleCI workflow. See the individual files in [.github/workflows](../../.github/workflows/) for each trigger and publishing workflow.
