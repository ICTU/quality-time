FROM node:16.13.2-alpine3.14

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time frontend"

RUN apk --no-cache add curl=~7.79

WORKDIR /work
COPY . /work
RUN npm install
RUN npm install -g serve@13.0.2
RUN npm run build

HEALTHCHECK CMD curl -f http://localhost:${FRONTEND_PORT:-5000}/favicon.ico || exit 1

# skipcq: DOK-DL3025
CMD serve --listen ${FRONTEND_PORT:-5000} --single build
