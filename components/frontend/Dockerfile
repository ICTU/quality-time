FROM node:18.14.2-alpine3.17

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time frontend"

RUN apk --no-cache add curl=7.88.1-r0

WORKDIR /work
COPY . /work
RUN npm install -g npm@9.2.0 && \
    npm install && \
    npm install -g serve@14.1.2 && \
    npm run build

HEALTHCHECK CMD curl -f http://localhost:${FRONTEND_PORT:-5000}/favicon.ico || exit 1

# skipcq: DOK-DL3025
# hadolint ignore=DL3025
CMD serve --listen ${FRONTEND_PORT:-5000} --single build
