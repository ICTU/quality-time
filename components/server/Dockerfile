FROM python:3.7-alpine

LABEL maintainer="Frank Niessink <frank@niessink.com>"
LABEL description="Quality-time server"

RUN apk add --no-cache --virtual .build-deps \
    build-base \
    openldap-dev \
    gcc \
    g++ \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip install --no-cache-dir psycopg2 python-ldap

RUN apk add libpq icu-dev

WORKDIR /work
ADD . /work
RUN pip install -r requirements.txt; python setup.py install
RUN apk del --no-cache .build-deps
EXPOSE 8080

CMD ["quality-time-server"]
