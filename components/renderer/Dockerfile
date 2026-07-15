FROM node:26.4-alpine3.24@sha256:725aeba2364a9b16beae49e180d83bd597dbd0b15c47f1f28875c290bfd255b9

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time PDF render service"

WORKDIR /home/renderer
COPY package*.json /home/renderer/

# Install, then reduce the attack surface: remove npm/corepack (not needed at runtime) and the package manager.
# The shell is kept because Chromium's launcher (/usr/bin/chromium-browser) is a shell script.
# hadolint ignore=DL3018
RUN apk add --no-cache chromium tzdata=2026c-r0 && \
    npm ci --omit=dev --ignore-scripts && \
    adduser -S renderer && \
    rm -rf /usr/local/lib/node_modules/npm /usr/local/bin/npm /usr/local/bin/npx \
        /usr/local/lib/node_modules/corepack /usr/local/bin/corepack && \
    apk --purge --quiet del apk-tools alpine-keys scanelf && \
    rm -rf /etc/apk /lib/apk /var/cache/apk

COPY src/*js /home/renderer/

USER renderer

HEALTHCHECK CMD ["node", "/home/renderer/healthcheck.cjs"]

ENV NODE_ENV=production

# Point the configuration and cache folders of Chromium, which include the Crashpad crash handler database and
# the fontconfig cache, to /tmp, the only writable folder when the container runs with a read-only root filesystem
ENV XDG_CONFIG_HOME=/tmp
ENV XDG_CACHE_HOME=/tmp

CMD ["node", "/home/renderer/index.js"]
