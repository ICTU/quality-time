FROM node:18.16.1-alpine3.17

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time frontend"

WORKDIR /work
COPY . /work
RUN npm install -g npm@9.8.0 && \
    npm install && \
    npm install -g serve@14.2.0 && \
    npm run build

HEALTHCHECK CMD node /work/healthcheck.js

# hadolint ignore=DL3025
CMD serve --listen ${FRONTEND_PORT:-5000} --no-request-logging --single build
