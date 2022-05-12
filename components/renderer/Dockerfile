FROM node:16.15.0-alpine3.15

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time PDF render service"

RUN apk --no-cache add curl=~7.80

# skipcq: DOK-DL3008
RUN apk add --no-cache \
    msttcorefonts-installer font-noto fontconfig \
    freetype ttf-dejavu ttf-droid ttf-freefont ttf-liberation \
    chromium=~99.0 \
  && rm -rf /var/cache/apk/* /tmp/*

RUN update-ms-fonts \
    && fc-cache -f

RUN npm install -g npm@8.10.0

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

WORKDIR /home/renderer
COPY package*.json /home/renderer
RUN npm install

COPY src/index.js /home/renderer/index.js

RUN adduser renderer --disabled-password
USER renderer

HEALTHCHECK CMD curl -f http://localhost:${RENDERER_PORT:-9000}/api/health || exit 1

ENV NODE_ENV production

CMD ["node", "/home/renderer/index.js"]
