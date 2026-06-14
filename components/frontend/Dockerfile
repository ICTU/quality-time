FROM node:26.3.0-alpine3.23@sha256:144769ec3f32e8ee36b3cfde91e82bee25d9367b20f31a151f3f7eea3a2a8541 AS compile-image

RUN apk add --no-cache tzdata=2026b-r0

WORKDIR /home/frontend
COPY public /home/frontend/public
COPY package*.json /home/frontend
COPY index.html /home/frontend
COPY *.ts /home/frontend
COPY src /home/frontend/src
COPY .env /home/frontend
RUN npm ci --ignore-scripts && \
    npm run --ignore-scripts build

FROM nginxinc/nginx-unprivileged:1.31.0-alpine3.23-slim@sha256:01cb6604af2fd0dce17f7aab60759e47ad288bec0425ad4b43e749369d2eecca

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time frontend"

ENV FRONTEND_PORT=5000

# Reduce the attack surface by removing the package manager, which the Nginx runtime does not need. The
# shell is kept because the Nginx entrypoint renders the configuration templates with it at startup.
USER root
RUN apk --purge --quiet del apk-tools alpine-keys scanelf && \
    rm -rf /etc/apk /lib/apk /var/cache/apk
USER 101

COPY --from=compile-image /home/frontend/dist /usr/share/nginx/html
COPY --from=compile-image /usr/share/zoneinfo /usr/share/zoneinfo

# Use the Shell form of CMD instead of the Exec form so the environment variable is substituted
# hadolint ignore=DL3025
HEALTHCHECK CMD wget --spider http://0.0.0.0:"${FRONTEND_PORT:-5000}"/favicon.ico || exit 1

COPY *.template /etc/nginx/templates/
COPY security_headers.conf /etc/nginx/snippets/security_headers.conf
