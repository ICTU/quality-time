FROM nginx:1.23.0

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time proxy"

ENV FRONTEND_HOST frontend
ENV FRONTEND_PORT 5000
ENV EXTERNAL_SERVER_HOST external_server
ENV EXTERNAL_SERVER_PORT 5001

COPY *.template /etc/nginx/templates/
