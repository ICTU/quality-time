FROM node:16.16.0-alpine3.15

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time frontend"

RUN apk --no-cache add curl=~7.80

WORKDIR /work
COPY . /work
RUN npm install -g npm@8.11.0
RUN npm install
RUN npm install -g serve@13.0.2
RUN npm run build

HEALTHCHECK CMD curl -f http://localhost:${FRONTEND_PORT:-5000}/favicon.ico || exit 1

# skipcq: DOK-DL3025
CMD serve --listen ${FRONTEND_PORT:-5000} --single build
