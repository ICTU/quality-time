FROM node:22.9.0-alpine3.20

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time frontend"

WORKDIR /home/frontend
COPY package*.json /home/frontend
COPY public /home/frontend/public
COPY src /home/frontend/src
COPY healthcheck.js /home/frontend
COPY .env /home/frontend
RUN npm install --ignore-scripts -g npm@10.9.0 && \
    npm install --ignore-scripts && \
    npm install --ignore-scripts -g serve@14.2.3 && \
    npm run --ignore-scripts build && \
    adduser frontend --disabled-password
USER frontend

HEALTHCHECK CMD ["node", "/home/frontend/healthcheck.js"]

# Use the Shell form of CMD instead of the Exec form so the environment variable is substituted
# hadolint ignore=DL3025
CMD serve --listen ${FRONTEND_PORT:-5000} --no-request-logging --single build
