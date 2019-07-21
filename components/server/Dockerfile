FROM python:3.7-alpine

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time server"

RUN apk add libldap
RUN apk add --no-cache --virtual .build-deps build-base openldap-dev python3-dev
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
RUN apk del --no-cache .build-deps
WORKDIR /server
COPY src /server

CMD ["python", "/server/quality_time_server.py"]
