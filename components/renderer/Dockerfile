FROM node:25.8.2-alpine3.22

# The base image is Alpine 3.22 instead of 3.23 as a work-around for https://gitlab.alpinelinux.org/alpine/aports/-/issues/?search=chromium&show=eyJpaWQiOiIxODA1NyIsImZ1bGxfcGF0aCI6ImFscGluZS9hcG9ydHMiLCJpZCI6MzU1OTE1fQ%3D%3D

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time PDF render service"

# hadolint ignore=DL3018
RUN apk add --no-cache chromium

WORKDIR /home/renderer
COPY package*.json /home/renderer/
RUN npm install --ignore-scripts

COPY src/*js /home/renderer/

RUN adduser renderer --disabled-password
USER renderer

HEALTHCHECK CMD ["node", "/home/renderer/healthcheck.cjs"]

ENV NODE_ENV=production

CMD ["node", "/home/renderer/index.js"]
