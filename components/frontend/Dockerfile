FROM node:20.7.0-alpine3.18

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time frontend"

WORKDIR /work
COPY . /work
RUN npm install -g npm@10.1.0 && \
    npm install && \
    npm install -g serve@14.2.1 && \
    npm run build

HEALTHCHECK CMD node /work/healthcheck.js

# hadolint ignore=DL3025
CMD serve --listen ${FRONTEND_PORT:-5000} --no-request-logging --single build
