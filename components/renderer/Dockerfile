FROM node:26.3.1-alpine3.23@sha256:d1f2956a218f864a8667d0c3f30ca52ed64f488e523a43399bc92de325046476

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time PDF render service"

WORKDIR /home/renderer
COPY package*.json /home/renderer/

# Install, then reduce the attack surface: remove npm/corepack (not needed at runtime) and the package manager.
# The shell is kept because Chromium's launcher (/usr/bin/chromium-browser) is a shell script.
# hadolint ignore=DL3018
RUN apk add --no-cache chromium tzdata=2026b-r0 && \
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
