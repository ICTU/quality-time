FROM node:23.6.1-alpine3.20 AS compile-image

WORKDIR /home/frontend
COPY public /home/frontend/public
COPY package*.json /home/frontend
COPY src /home/frontend/src
COPY .env /home/frontend
RUN npm install --ignore-scripts && \
    npm run --ignore-scripts build

FROM node:23.6.1-alpine3.20

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time frontend"

WORKDIR /home/frontend
COPY healthcheck.js /home/frontend
COPY --from=compile-image /home/frontend/build /home/frontend/build
RUN npm install --ignore-scripts -g serve@14.2.4 && \
    adduser frontend --disabled-password
USER frontend

HEALTHCHECK CMD ["node", "/home/frontend/healthcheck.js"]

# Use the Shell form of CMD instead of the Exec form so the environment variable is substituted
# hadolint ignore=DL3025
CMD serve --listen ${FRONTEND_PORT:-5000} --no-request-logging --single build
