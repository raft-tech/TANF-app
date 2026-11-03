# Local-only build from the repository root (also supports linux/arm64):
# task keycloak:build IMAGE_REF=tdp-keycloak:dhi-candidate-amd64 PLATFORM=linux/amd64

FROM dhi.io/keycloak:26.7.3-debian13@sha256:1e1d26bfe8614ce1ee1b3ccb1780f4cbce339a302fe38bdb11fa12f408ea0f2c AS runtime
FROM dhi.io/nginx:1.30.6-debian13@sha256:98cdc3c682c3c11e6ce1629094e2fb8c88e9fa58393c63ec934d0be787273e21 AS nginx-source
FROM dhi.io/keycloak:26.7.3-debian13-dev@sha256:33795d6a5bcf9dcc23e3f9d8a7f9c0f32539b97ca219de89d63d29e9ec841772 AS assembly

USER 0:0
COPY runtime-packages.lock /runtime-packages.lock
RUN apt-get update && xargs -r apt-get install -y --no-install-recommends < /runtime-packages.lock && \
    rm -rf /var/lib/apt/lists/*
ADD --checksum=sha256:df6939a1d9c40d5ab7e1fb690082ea8980dbbf402ca92a9968b90b652cb3ca9a \
    https://github.com/adorsys/keycloak-config-cli/releases/download/v6.5.1/keycloak-config-cli-26.5.5.jar /artifacts/keycloak-config-cli.jar
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
COPY --from=assembly /artifacts/keycloak-config-cli.jar /opt/keycloak/keycloak-config-cli.jar
RUN mkdir -p /opt/keycloak/data/import /var/log/nginx \
    /tmp/nginx_client_body /tmp/nginx_proxy /tmp/nginx_fastcgi /tmp/nginx_uwsgi /tmp/nginx_scgi && \
    chown -R 65532:65532 /opt/keycloak /var/log/nginx /tmp/nginx_*
USER 65532:65532

COPY realm-configs/ /opt/keycloak/realm-configs/
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
