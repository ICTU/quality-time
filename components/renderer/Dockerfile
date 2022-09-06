FROM node:16.17.0-alpine3.16

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time PDF render service"

RUN apk --no-cache add curl=~7.83

RUN apk add --no-cache \
    msttcorefonts-installer=3.8-r1 \
    font-noto=0_git20211101-r4 \
    fontconfig=2.14.0-r0 \
    freetype=2.12.1-r0 \
    ttf-dejavu=2.37-r1 \
    ttf-droid=20200215-r2 \
    ttf-freefont=20120503-r2 \
    ttf-liberation=2.1.5-r1 \
    chromium=102.0.5005.173-r0 && \
    rm -rf /var/cache/apk/* /tmp/*

RUN update-ms-fonts \
    && fc-cache -f

RUN npm install -g npm@8.17.0

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

WORKDIR /home/renderer
COPY package*.json /home/renderer/
RUN npm install

COPY src/index.js /home/renderer/index.js

RUN adduser renderer --disabled-password
USER renderer

HEALTHCHECK CMD curl -f http://localhost:${RENDERER_PORT:-9000}/api/health || exit 1

ENV NODE_ENV production

CMD ["node", "/home/renderer/index.js"]
