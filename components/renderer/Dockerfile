FROM node:26.3.0-alpine3.23@sha256:144769ec3f32e8ee36b3cfde91e82bee25d9367b20f31a151f3f7eea3a2a8541

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time PDF render service"

# hadolint ignore=DL3018
RUN apk add --no-cache chromium tzdata=2026b-r0

WORKDIR /home/renderer
COPY package*.json /home/renderer/
RUN npm ci --ignore-scripts

COPY src/*js /home/renderer/

RUN adduser renderer --disabled-password
USER renderer

HEALTHCHECK CMD ["node", "/home/renderer/healthcheck.cjs"]

ENV NODE_ENV=production

CMD ["node", "/home/renderer/index.js"]
