FROM node:24.9.0-alpine3.22 AS compile-image

WORKDIR /home/frontend
COPY public /home/frontend/public
COPY package*.json /home/frontend
COPY index.html /home/frontend
COPY *.ts /home/frontend
COPY src /home/frontend/src
COPY .env /home/frontend
RUN npm install --ignore-scripts && \
    npm run --ignore-scripts build

FROM nginxinc/nginx-unprivileged:1.29.2-alpine3.22-slim

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time frontend"

ENV FRONTEND_PORT 5000

COPY --from=compile-image /home/frontend/dist /usr/share/nginx/html

# Use the Shell form of CMD instead of the Exec form so the environment variable is substituted
# hadolint ignore=DL3025
HEALTHCHECK CMD wget --spider http://0.0.0.0:${FRONTEND_PORT:-5000}/favicon.ico || exit 1

COPY *.template /etc/nginx/templates/
