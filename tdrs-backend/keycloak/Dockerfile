# Local-only build from the repository root (also supports linux/arm64):
# task keycloak:build IMAGE_REF=tdp-keycloak:dhi-candidate-amd64 PLATFORM=linux/amd64

FROM dhi.io/keycloak:26.8.1-debian13@sha256:cf5c35691dc4e48a9cbade9d707a8df0cb35f9cfd5a25735ed9d447b0576e017 AS runtime
FROM dhi.io/nginx:1.30.6-debian13@sha256:98cdc3c682c3c11e6ce1629094e2fb8c88e9fa58393c63ec934d0be787273e21 AS nginx-source
FROM --platform=$BUILDPLATFORM dhi.io/maven:3.10.0-jdk21-debian13-dev@sha256:582eab6325c5112cd73b3649205a9b9c0d0166ec9eaf0449af5d766816cd348e AS config-cli-build

USER 0:0
RUN apt-get update && apt-get install -y --no-install-recommends patch=2.8-2+deb13u0+dhi3 && \
    rm -rf /var/lib/apt/lists/*
ADD https://github.com/adorsys/keycloak-config-cli.git#90c97fc0f8968286400be7bcb27f8165581003f2 /source
WORKDIR /source
COPY config-cli-security.diff /config-cli-security.patch
RUN patch --fuzz=0 -p1 < /config-cli-security.patch
RUN --mount=type=cache,target=/root/.m2 \
    mvn -B -ntp -Dtest=JsonUtilTest,CloneUtilTest,KeycloakProviderJacksonProviderTest \
    -Dgit.commit.time=20260522153036 package && \
    mkdir /artifacts && cp target/keycloak-config-cli.jar /artifacts/keycloak-config-cli.jar && \
    sha256sum /artifacts/keycloak-config-cli.jar | sed 's@/artifacts/@/opt/keycloak/@' > /artifacts/config-cli.sha256 && \
    cp pom.xml /artifacts/config-cli-pom.xml && \
    cp -r target/surefire-reports /artifacts/unit-test-reports

FROM scratch AS config-cli-evidence
COPY --from=config-cli-build /artifacts/config-cli.sha256 /artifacts/config-cli-pom.xml /
COPY --from=config-cli-build /artifacts/unit-test-reports /unit-test-reports/

FROM dhi.io/keycloak:26.8.1-debian13-dev@sha256:21affd709f0a1ad250b37f55880d29e51fccf3c025e97aa09f427189018de26d AS assembly

USER 0:0
COPY runtime-packages.lock /runtime-packages.lock
RUN apt-get update && xargs -r apt-get install -y --no-install-recommends < /runtime-packages.lock && \
    rm -rf /var/lib/apt/lists/*
COPY --from=nginx-source /usr/sbin/nginx /usr/sbin/nginx
COPY --from=nginx-source /var/lib/dpkg/status /nginx-status
# Compare against the actual final runtime, never replacing its existing libraries.
COPY --from=runtime /usr/lib/ /runtime-libs/
COPY --from=runtime /var/lib/dpkg/status /runtime-status
COPY collect-runtime.sh /collect-runtime.sh
RUN bash /collect-runtime.sh

FROM runtime
USER 0:0
COPY --from=assembly /runtime-additions/ /
COPY --from=config-cli-build /artifacts/keycloak-config-cli.jar /opt/keycloak/keycloak-config-cli.jar
COPY --from=config-cli-build /artifacts/config-cli.sha256 /artifacts/config-cli-pom.xml /usr/share/keycloak-image/
RUN mkdir -p /opt/keycloak/data/import /var/log/nginx \
    /tmp/nginx_client_body /tmp/nginx_proxy /tmp/nginx_fastcgi /tmp/nginx_uwsgi /tmp/nginx_scgi && \
    chown -R 65532:65532 /opt/keycloak /var/log/nginx /tmp/nginx_*
USER 65532:65532

COPY realm-configs/ /opt/keycloak/realm-configs/
COPY --chmod=755 select-realm-config.sh /opt/keycloak/select-realm-config.sh
COPY --chmod=755 normalize-login-gov-key.sh /opt/keycloak/normalize-login-gov-key.sh
COPY nginx.conf /opt/keycloak/nginx.conf.template
COPY --chmod=755 entrypoint.sh /opt/keycloak/entrypoint.sh
COPY --chmod=755 check-readiness.sh /opt/keycloak/check-readiness.sh

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
