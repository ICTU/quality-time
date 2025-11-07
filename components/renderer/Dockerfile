FROM node:25.1.0-trixie-slim

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time PDF render service"

RUN apt-get update && \
    apt-get install --no-install-recommends -y chromium=142.0.7444.134-1~deb13u1 && \
    rm -rf /var/lib/apt/lists/* && \
    adduser renderer --disabled-password

WORKDIR /home/renderer
COPY package*.json /home/renderer/
RUN npm install --ignore-scripts

COPY src/*js /home/renderer/

USER renderer

HEALTHCHECK CMD ["node", "/home/renderer/healthcheck.cjs"]

ENV NODE_ENV production

CMD ["node", "/home/renderer/index.js"]
