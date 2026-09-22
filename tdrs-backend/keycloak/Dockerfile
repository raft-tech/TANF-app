# Use the following to build: docker buildx build -t ghcr.io/raft-tech/tdp-keycloak:<tag> . --platform linux/amd64,linux/arm64 --push

# Stage 1: nginx binary and non-system shared libraries.
FROM nginx:1.27 AS nginx-source
# Collect libs that aren't part of glibc (those are already in ubi-micro).
# Also exclude libcrypt — Debian's version requires glibc 2.36, but ubi-micro
# only has glibc 2.34. We grab a compatible libcrypt from UBI 9 instead.
RUN mkdir /nginx-libs && \
    ldd /usr/sbin/nginx | awk '/=>/{print $3}' | \
    grep -v -E '(libc\.so|libm\.so|libdl\.so|libpthread|librt\.so|libcrypt\.so|ld-linux)' | \
    while read -r lib; do cp -L "$lib" /nginx-libs/; done

# Stage 2: libcrypt.so.1 compatible with UBI 9's glibc 2.34.
# Debian nginx links against libcrypt.so.1, but UBI 9 only ships libcrypt.so.2.
# The libxcrypt-compat package provides a backwards-compatible libcrypt.so.1.
FROM registry.access.redhat.com/ubi9/ubi-minimal AS ubi-libs
RUN microdnf install -y libxcrypt-compat && \
    mkdir /ubi-libs && cp -L /usr/lib64/libcrypt.so.1* /ubi-libs/ && \
    microdnf clean all

FROM adorsys/keycloak-config-cli:6.5.1-26.5.5 AS keycloak-config-cli

# Download target-architecture CLI tools before copying them into the minimal
# Keycloak runtime image.
FROM alpine:3.21 AS cli-tools
ARG TARGETARCH
ARG JQ_VERSION=1.7.1
ARG CURL_VERSION=8.7.1
SHELL ["/bin/ash", "-eo", "pipefail", "-c"]
# Package versions follow the pinned Alpine release so security updates remain available.
# hadolint ignore=DL3018
RUN apk add --no-cache ca-certificates curl && \
    case "$TARGETARCH" in \
        amd64) \
            jq_sha256="5942c9b0934e510ee61eb3e30273f1b3fe2590df93933a93d7c58b81d19c8ff5"; \
            curl_arch="amd64"; \
            curl_sha256="af5959046be89599c42085d64bfea87a9ecb5021452ba8eeb8ce04f1e0b9e6be" \
            ;; \
        arm64) \
            jq_sha256="4dd2d8a0661df0b22f1bb9a1f9830f06b6f3b8f7d91211a1ef5d7c4f06a8b4a5"; \
            curl_arch="aarch64"; \
            curl_sha256="28b28df6d5a17b4c43af86979bcb2bb1a5d8fe5a170c84d274e9b5ba81056e5e" \
            ;; \
        *) \
            echo "Unsupported target architecture: $TARGETARCH" >&2; \
            exit 1 \
            ;; \
    esac && \
    mkdir /tools && \
    curl --fail --location --silent --show-error \
        "https://github.com/jqlang/jq/releases/download/jq-${JQ_VERSION}/jq-linux-${TARGETARCH}" \
        --output /tools/jq && \
    curl --fail --location --silent --show-error \
        "https://github.com/moparisthebest/static-curl/releases/download/v${CURL_VERSION}/curl-${curl_arch}" \
        --output /tools/curl && \
    echo "${jq_sha256}  /tools/jq" | sha256sum -c - && \
    echo "${curl_sha256}  /tools/curl" | sha256sum -c - && \
    chmod 755 /tools/jq /tools/curl

FROM quay.io/keycloak/keycloak:26.5.5

USER root
# Copy nginx binary, Debian-compatible libs, and UBI-compatible libcrypt.
COPY --from=nginx-source /usr/sbin/nginx /usr/sbin/nginx
COPY --from=nginx-source /nginx-libs/ /usr/lib64/
COPY --from=ubi-libs /ubi-libs/ /usr/lib64/
RUN mkdir -p /var/log/nginx /tmp/nginx_client_body /tmp/nginx_proxy /tmp/nginx_fastcgi /tmp/nginx_uwsgi /tmp/nginx_scgi && \
    chown -R 1000:0 /var/log/nginx /tmp/nginx_*
USER 1000

# Install jq and curl for manifest startup and health checks.
COPY --from=cli-tools --chmod=755 /tools/jq /usr/local/bin/jq
COPY --from=cli-tools --chmod=755 /tools/curl /usr/local/bin/curl

COPY realm-configs/ /opt/keycloak/realm-configs/
COPY --from=keycloak-config-cli /app/keycloak-config-cli.jar /opt/keycloak/keycloak-config-cli.jar
COPY --chmod=755 select-realm-config.sh /opt/keycloak/select-realm-config.sh
COPY --chmod=755 normalize-login-gov-key.sh /opt/keycloak/normalize-login-gov-key.sh
COPY nginx.conf /opt/keycloak/nginx.conf.template
COPY --chmod=755 entrypoint.sh /opt/keycloak/entrypoint.sh

# Health and metrics are served on the management port (9000) by default.
ENV KC_DB=postgres
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true
ENV KC_FEATURES=user-event-metrics
ENV KC_HTTP_METRICS_HISTOGRAMS_ENABLED=true
ENV KC_EVENT_METRICS_USER_ENABLED=true
ENV KC_EVENT_METRICS_USER_EVENTS=client_login,code_to_token,login,logout,refresh_token,token_exchange
ENV KC_EVENT_METRICS_USER_TAGS=realm,idp,clientId
RUN /opt/keycloak/bin/kc.sh build

ENTRYPOINT ["/opt/keycloak/entrypoint.sh"]
