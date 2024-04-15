ARG IMAGE_NAME=nginx
ARG IMAGE_VERSION=1.25.3-alpine3.18-slim
FROM $IMAGE_NAME:$IMAGE_VERSION

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time proxy"

ENV NGINX_LISTEN 80

ENV FRONTEND_HOST frontend
ENV FRONTEND_PORT 5000

ENV API_SERVER_HOST api_server
ENV API_SERVER_PORT 5001

RUN rm -f /etc/nginx/conf.d/default.conf
RUN rm -f /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
RUN rm -f /docker-entrypoint.d/20-envsubst-on-templates.sh

COPY qualitytime.conf.template /srv/qualitytime.conf.template

COPY 90_fix_listen.sh /docker-entrypoint.d/90_fix_listen.sh
RUN chmod 0755 /docker-entrypoint.d/90_fix_listen.sh

COPY nginx.conf /etc/nginx/nginx.conf
RUN chmod 0644 /etc/nginx/nginx.conf

