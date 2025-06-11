FROM node:24.2.0-bookworm-slim

# Note the base image is bookworm and not alpine as work-around for this issue: https://github.com/ICTU/quality-time/issues/11131

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time PDF render service"

RUN apt-get -y update && apt-get install -y --no-install-recommends chromium=137.0.7151.68-1~deb12u1 && rm -rf /var/lib/apt/lists/*

WORKDIR /home/renderer
COPY package*.json /home/renderer/
RUN npm install --ignore-scripts

COPY src/*js /home/renderer/

RUN adduser renderer --disabled-password
USER renderer

HEALTHCHECK CMD ["node", "/home/renderer/healthcheck.cjs"]

ENV NODE_ENV production

CMD ["node", "/home/renderer/index.js"]
