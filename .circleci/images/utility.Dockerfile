ARG ALPINE_LINUX_VERSION='3.16'

###########################################################################################################

ARG TERRAFORM_VERSION='1.3.1'

FROM hashicorp/terraform:${TERRAFORM_VERSION} as terraform-builder

###########################################################################################################

FROM alpine:${ALPINE_LINUX_VERSION}

# Preserve the entrypoint even when the image is used for a primary container
LABEL com.circleci.preserve-entrypoint=true

ENV SOPS_VERSION='3.7.3'

# Install required tools for custom uitlity CircleCI image
RUN apk add bash git openssh tar gzip ca-certificates

# Install python3 deps, parsers and other tools
RUN apk add jq curl python3 py3-pip

RUN pip3 install --upgrade pip \
    pip3 install awscli botocore boto3

# Install SOPS, other ci/cd tools
RUN export SOPS_VERSION=${SOPS_VERSION} \
  && export SOPS_URL=https://github.com/mozilla/sops/releases/download/v${SOPS_VERSION}/sops-v${SOPS_VERSION}.linux.amd64 \
  && curl -sSL -o /usr/local/bin/sops ${SOPS_URL} \
  && chmod +x /usr/local/bin/sops

# Copy over binaries from other images
COPY --from=terraform-builder /bin/terraform /usr/local/bin/terraform

# Add non-root user && switch context to non-root user
RUN addgroup -g 1001 circleci && adduser -u 1001 -s /bin/bash -h /circleci -D circleci -G circleci

USER circleci
