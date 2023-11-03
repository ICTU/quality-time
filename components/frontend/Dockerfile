FROM node:20.9.0-alpine3.18

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time frontend"

WORKDIR /home/frontend
COPY package*.json /home/frontend
COPY public /home/frontend/public
COPY src /home/frontend/src
COPY healthcheck.js /home/frontend
RUN npm install --ignore-scripts -g npm@10.2.3 && \
    npm install --ignore-scripts && \
    npm install --ignore-scripts -g serve@14.2.1 && \
    npm run --ignore-scripts build

RUN adduser frontend --disabled-password
USER frontend

HEALTHCHECK CMD node /home/frontend/healthcheck.js

# hadolint ignore=DL3025
CMD serve --listen ${FRONTEND_PORT:-5000} --no-request-logging --single build
