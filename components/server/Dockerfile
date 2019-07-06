FROM python:3.7-alpine

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time server"

RUN apk add libldap

RUN apk add --no-cache --virtual .build-deps \
    build-base \
    openldap-dev \
    python3-dev

WORKDIR /work
ADD . /work
RUN pip install --no-cache-dir -r requirements.txt; python setup.py install
RUN apk del --no-cache .build-deps

CMD ["quality-time-server"]
