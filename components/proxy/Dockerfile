FROM nginxinc/nginx-unprivileged:1.31.2-alpine3.23-slim@sha256:8f92ff79b9e9039b1ec2e363a04ce89c95c30e3d0be545bf6263024f5c21a2a8 AS compile-image

# hadolint ignore=DL3002
USER root
# Add the CAP_NET_BIND_SERVICE to provide backwards compatibility, running on privileged port (80)
RUN apk add --no-cache libcap=2.78-r0 tzdata=2026b-r0 && setcap CAP_NET_BIND_SERVICE=+eip /usr/sbin/nginx

FROM nginxinc/nginx-unprivileged:1.31.2-alpine3.23-slim@sha256:8f92ff79b9e9039b1ec2e363a04ce89c95c30e3d0be545bf6263024f5c21a2a8

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time proxy"

ENV PROXY_PORT=80
ENV FRONTEND_HOST=frontend
ENV FRONTEND_PORT=5000
ENV API_SERVER_HOST=api_server
ENV API_SERVER_PORT=5001

# Reduce the attack surface by removing the package manager, which the Nginx runtime does not need. The
# shell is kept because the Nginx entrypoint renders the configuration templates with it at startup.
USER root
RUN apk --purge --quiet del apk-tools alpine-keys scanelf && \
    rm -rf /etc/apk /lib/apk /var/cache/apk
USER 101

COPY --from=compile-image /usr/sbin/nginx /usr/sbin/nginx
COPY --from=compile-image /usr/share/zoneinfo /usr/share/zoneinfo
COPY *.template /etc/nginx/templates/
COPY security_headers.conf /etc/nginx/snippets/security_headers.conf

# Use the Shell form of CMD instead of the Exec form so the environment variable is substituted
# hadolint ignore=DL3025
HEALTHCHECK CMD wget --spider http://0.0.0.0:"${PROXY_PORT:-80}"/favicon.ico || exit 1
