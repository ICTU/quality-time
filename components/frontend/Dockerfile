FROM node:23.1.0-alpine3.20

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time frontend"

WORKDIR /home/frontend
COPY package.json /home/frontend
COPY yarn.lock /home/frontend
COPY public /home/frontend/public
COPY src /home/frontend/src
COPY healthcheck.js /home/frontend
COPY .env /home/frontend
RUN corepack enable yarn && \
    yarn && \
    yarn global add --ignore-scripts serve@14.2.4 && \
    yarn run --ignore-scripts build && \
    yarn cache clean && \
    adduser frontend --disabled-password
USER frontend

HEALTHCHECK CMD ["node", "/home/frontend/healthcheck.js"]

# Use the Shell form of CMD instead of the Exec form so the environment variable is substituted
# hadolint ignore=DL3025
CMD serve --listen ${FRONTEND_PORT:-5000} --no-request-logging --single build
