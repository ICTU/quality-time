FROM python:3.11.3-alpine3.17 AS compile-image

WORKDIR /home/server

RUN apk add --no-cache gcc=12.2.1_git20220924-r4 make=4.3-r1 libc-dev=0.7.2-r3 libffi-dev=3.4.4-r0
# hadolint ignore=DL3059
RUN python -m venv venv
ENV PATH="/home/server/venv/bin:$PATH"
COPY internal_server/requirements/requirements-base.txt /requirements-base.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements-base.txt
COPY internal_server/requirements/requirements.txt /requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt
COPY internal_server/requirements/requirements-internal.txt /requirements-internal.txt
COPY shared_data_model /home/shared_data_model/
COPY shared_server_code /home/shared_server_code/
RUN pip install --no-cache-dir -r /requirements-internal.txt

FROM python:3.11.3-alpine3.17

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time internal server"

RUN apk add --no-cache curl=7.88.1-r1
# hadolint ignore=DL3059
RUN adduser -S server
WORKDIR /home/server
USER server

HEALTHCHECK CMD curl -f http://localhost:${INTERNAL_SERVER_PORT:-5002}/api/health || exit 1

COPY --from=compile-image /home/server/venv /home/server/venv
COPY internal_server/src /home/server
COPY shared_data_model /home/shared_data_model
COPY shared_server_code /home/shared_server_code

ENV PATH="/home/server/venv/bin:$PATH"
CMD ["python", "/home/server/quality_time_server.py"]
