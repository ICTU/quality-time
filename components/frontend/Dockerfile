FROM node:26.13.1-alpine3.24@sha256:6bd9ab43c0ec0190ca7b2d193906cb8b7edf6e7f4afa43ddeccd6452710bffb5 AS compile-image

RUN apk add --no-cache tzdata=2026f-r0

WORKDIR /home/frontend
COPY public /home/frontend/public
COPY package*.json /home/frontend
COPY index.html /home/frontend
COPY *.ts /home/frontend
COPY src /home/frontend/src
COPY .env /home/frontend
RUN npm ci --ignore-scripts && \
    npm run --ignore-scripts build

FROM nginx/nginx-unprivileged:1.31.9-alpine3.24-slim@sha256:75e85a09b0f25bd46d49a9fd85589ffa70b0459c8ed5ee0dc6596fd642e1f829

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time frontend"

ENV FRONTEND_PORT=5000

# Reduce the attack surface by removing the package manager, which the Nginx runtime does not need. The
# shell is kept because the Nginx entrypoint renders the configuration templates with it at startup.
# # Hadolint says: DL3066 info: Non-numeric user-id may not be resolvable by host system. Fix TBD.
# hadolint ignore=DL3066
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
