FROM node:23.8.0-alpine3.21

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time PDF render service"

RUN apk add --no-cache chromium=133.0.6943.141-r0

WORKDIR /home/renderer
COPY package*.json /home/renderer/
RUN npm install --ignore-scripts

COPY src/*js /home/renderer/

RUN adduser renderer --disabled-password
USER renderer

HEALTHCHECK CMD ["node", "/home/renderer/healthcheck.cjs"]

ENV NODE_ENV production

CMD ["node", "/home/renderer/index.js"]
