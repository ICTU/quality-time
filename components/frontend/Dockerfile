FROM node:18.16.0-alpine3.17

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time frontend"

RUN apk --no-cache add curl=8.1.1-r1

WORKDIR /work
COPY . /work
RUN npm install -g npm@9.6.7 && \
    npm install && \
    npm install -g serve@14.2.0 && \
    npm run build

HEALTHCHECK CMD curl -f http://localhost:${FRONTEND_PORT:-5000}/favicon.ico || exit 1

# hadolint ignore=DL3025
CMD serve --listen ${FRONTEND_PORT:-5000} --no-request-logging --single build
