FROM nginx:1.23.1

LABEL maintainer="Quality-time team <Quality-time@ictu.nl>"
LABEL description="Quality-time proxy"

ENV FRONTEND_HOST frontend
ENV FRONTEND_PORT 5000
ENV EXTERNAL_SERVER_HOST external_server
ENV EXTERNAL_SERVER_PORT 5001

COPY *.template /etc/nginx/templates/
