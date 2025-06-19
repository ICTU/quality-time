FROM python:3.13.5-alpine3.22 AS compile-image

WORKDIR /home/server

RUN apk add --no-cache g++=14.2.0-r6 gcc=14.2.0-r6 libffi-dev=3.4.8-r0 make=4.4.1-r3 && \
    python -m venv venv
ENV PATH="/home/server/venv/bin:$PATH"
COPY api_server/requirements/requirements.txt /requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt
COPY api_server/requirements/requirements-internal.txt /requirements-internal.txt
COPY shared_code /home/shared_code/
RUN pip install --no-cache-dir --use-pep517 -r /requirements-internal.txt

FROM python:3.13.5-alpine3.22

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time API-server"

RUN adduser -S server
WORKDIR /home/server
USER server

COPY --from=compile-image /home/server/venv /home/server/venv
COPY api_server/src /home/server
COPY shared_code /home/shared_code

HEALTHCHECK CMD ["python", "/home/server/healthcheck.py"]

ENV PATH="/home/server/venv/bin:$PATH"
CMD ["python", "/home/server/quality_time_server.py"]
