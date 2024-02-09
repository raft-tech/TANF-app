# Redis Service and Celery Instance

We use a CloudFoundry Redis service and a separate instance to run celery to run background processes like parsing data-file documents that have been submitted and have passed the [ClamAV scan](./clamav.md).

## Redis Deployment

As part of the move towards each environment being self-contained, one redis service is created per environment, deployed through the [CircleCI pipeline](./circle-ci.md), defined using [terraform](../../terraform/README.md).

## Celery Deployment

Celery is deployed at the same time as the backend through the [CircleCI pipeline](./circle-ci.md), with the details configured in the [celery manifest](../../tdrs-backend/manifest.celery.yml) and the [deploy-backend script](../../scripts/deploy-backend.sh)