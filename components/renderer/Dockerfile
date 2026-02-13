FROM node:25.6.1-alpine3.23

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time PDF render service"

# Work around https://gitlab.alpinelinux.org/alpine/aports/-/issues/17775:
# hadolint ignore=DL3018
RUN apk upgrade --scripts=no apk-tools && apk add --no-cache chromium

WORKDIR /home/renderer
COPY package*.json /home/renderer/
RUN npm install --ignore-scripts

COPY src/*js /home/renderer/

RUN adduser renderer --disabled-password
USER renderer

HEALTHCHECK CMD ["node", "/home/renderer/healthcheck.cjs"]

ENV NODE_ENV=production

CMD ["node", "/home/renderer/index.js"]
