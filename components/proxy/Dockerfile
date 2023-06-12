ARG IMAGE_NAME=nginx
ARG IMAGE_VERSION=1.23.4-alpine-slim
FROM $IMAGE_NAME:$IMAGE_VERSION

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time proxy"

ENV FRONTEND_HOST frontend
ENV FRONTEND_PORT 5000
ENV API_SERVER_HOST api_server
ENV API_SERVER_PORT 5001

COPY *.template /etc/nginx/templates/
