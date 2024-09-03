FROM nginxinc/nginx-unprivileged:1.27.0-alpine3.19-slim AS compile-image

# hadolint ignore=DL3002
USER root
# Add the CAP_NET_BIND_SERVICE to provide backwards compatability, running on privileged port (80)
RUN apk add --no-cache libcap=2.69-r1 && setcap CAP_NET_BIND_SERVICE=+eip /usr/sbin/nginx

FROM nginxinc/nginx-unprivileged:1.27.0-alpine3.19-slim

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time proxy"

ENV PROXY_PORT 80
ENV FRONTEND_HOST frontend
ENV FRONTEND_PORT 5000
ENV API_SERVER_HOST api_server
ENV API_SERVER_PORT 5001

COPY --from=compile-image /usr/sbin/nginx /usr/sbin/nginx
COPY *.template /etc/nginx/templates/
