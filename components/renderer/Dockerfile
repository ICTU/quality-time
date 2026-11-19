FROM node:26.13.1-alpine3.24@sha256:6bd9ab43c0ec0190ca7b2d193906cb8b7edf6e7f4afa43ddeccd6452710bffb5

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time PDF render service"

WORKDIR /home/renderer
COPY package*.json /home/renderer/

# Install, then reduce the attack surface: remove npm/corepack (not needed at runtime) and the package manager.
# The shell is kept because Chromium's launcher (/usr/bin/chromium-browser) is a shell script.
# hadolint ignore=DL3018
RUN apk add --no-cache chromium tzdata=2026f-r0 && \
    npm ci --omit=dev --ignore-scripts && \
    adduser -S renderer && \
    rm -rf /usr/local/lib/node_modules/npm /usr/local/bin/npm /usr/local/bin/npx \
        /usr/local/lib/node_modules/corepack /usr/local/bin/corepack && \
    apk --purge --quiet del apk-tools alpine-keys scanelf && \
    rm -rf /etc/apk /lib/apk /var/cache/apk

COPY src/*js /home/renderer/

# Hadolint says: DL3066 info: Non-numeric user-id may not be resolvable by host system. Fix TBD.
# hadolint ignore=DL3066
USER renderer

HEALTHCHECK CMD ["node", "/home/renderer/healthcheck.cjs"]

ENV NODE_ENV=production

# Point the configuration and cache folders of Chromium, which include the Crashpad crash handler database and
# the fontconfig cache, to /tmp, the only writable folder when the container runs with a read-only root filesystem
ENV XDG_CONFIG_HOME=/tmp
ENV XDG_CACHE_HOME=/tmp

CMD ["node", "/home/renderer/index.js"]
