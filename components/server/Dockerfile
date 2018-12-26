FROM python:3.7-alpine

LABEL maintainer="Frank Niessink <frank@niessink.com>"
LABEL description="Quality-time server"

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip install --no-cache-dir psycopg2 \
    && apk del --no-cache .build-deps
RUN apk add libpq

WORKDIR /work
ADD . /work
RUN pip install -r requirements.txt; python setup.py install
EXPOSE 8080

CMD ["quality-time-server"]
