FROM node:23.7.0-alpine3.21 AS compile-image

WORKDIR /home/frontend
COPY public /home/frontend/public
COPY package*.json /home/frontend
COPY index.html /home/frontend
COPY *.ts /home/frontend
COPY src /home/frontend/src
COPY .env /home/frontend
RUN npm install --ignore-scripts && \
    npm run --ignore-scripts build

FROM busybox:1.37.0

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time frontend"

WORKDIR /home/frontend
COPY --from=compile-image /home/frontend/dist /home/frontend/dist
RUN adduser frontend --disabled-password
USER frontend

# Use the Shell form of CMD instead of the Exec form so the environment variable is substituted
# hadolint ignore=DL3025
HEALTHCHECK CMD wget --spider http://localhost:${FRONTEND_PORT:-5000}/favicon.ico || exit 1
# hadolint ignore=DL3025
CMD httpd -f -v -p ${FRONTEND_PORT:-5000} -h dist
