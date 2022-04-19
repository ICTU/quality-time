FROM nginx:1.21.6

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time proxy"

ENV FRONTEND_PORT 5000
ENV SERVER_PORT 5001

COPY *.template /etc/nginx/templates/
COPY *.conf /etc/nginx/
