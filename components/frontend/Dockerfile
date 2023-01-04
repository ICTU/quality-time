FROM node:16.19.0-alpine3.16

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time frontend"

RUN apk --no-cache add curl=~7.83

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
