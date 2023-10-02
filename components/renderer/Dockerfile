FROM node:20.8.0-alpine3.18

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time PDF render service"

RUN apk add --no-cache \
    msttcorefonts-installer=3.8-r1 \
    fontconfig=2.14.2-r3 \
    font-noto=23.5.1-r0 \
    freetype=2.13.0-r5 \
    ttf-dejavu=2.37-r5 \
    ttf-droid=20200215-r2 \
    ttf-freefont=20120503-r4 \
    ttf-liberation=2.1.5-r2 \
    chromium=117.0.5938.62-r0 && \
    rm -rf /var/cache/apk/* /tmp/*

RUN update-ms-fonts \
    && fc-cache -f

RUN npm install -g npm@10.1.0

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

WORKDIR /home/renderer
COPY package*.json /home/renderer/
RUN npm install

COPY src/*js /home/renderer/

RUN adduser renderer --disabled-password
USER renderer

HEALTHCHECK CMD node /home/renderer/healthcheck.cjs

ENV NODE_ENV production

CMD ["node", "/home/renderer/index.js"]
