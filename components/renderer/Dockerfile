FROM node:16.17.0-alpine3.15

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time PDF render service"

RUN apk --no-cache add curl=~7.80

RUN apk add --no-cache \
    msttcorefonts-installer=3.6-r2 \
    font-noto=0_git20211101-r0 \
    fontconfig=2.13.1-r4 \
    freetype=2.11.1-r2 \
    ttf-dejavu=2.37-r1 \
    ttf-droid=20200215-r1 \
    ttf-freefont=20120503-r2 \
    ttf-liberation=2.00.5-r0 \
    chromium=99.0.4844.84-r0 && \
    rm -rf /var/cache/apk/* /tmp/*

RUN update-ms-fonts \
    && fc-cache -f

RUN npm install -g npm@8.11.0

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
