FROM python:3.11.4-alpine3.17 AS compile-image

WORKDIR /home/server

RUN apk add --no-cache gcc=12.2.1_git20220924-r4 make=4.3-r1 libc-dev=0.7.2-r3 libffi-dev=3.4.4-r0
# hadolint ignore=DL3059
RUN python -m venv venv
ENV PATH="/home/server/venv/bin:$PATH"
COPY api_server/requirements/requirements.txt /requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt
COPY api_server/requirements/requirements-internal.txt /requirements-internal.txt
COPY shared_data_model /home/shared_data_model/
COPY shared_code /home/shared_code/
RUN pip install --no-cache-dir --use-pep517 -r /requirements-internal.txt

FROM python:3.11.4-alpine3.17

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time API-server"

# hadolint ignore=DL3059
RUN adduser -S server
WORKDIR /home/server
USER server

COPY --from=compile-image /home/server/venv /home/server/venv
COPY api_server/src /home/server
COPY shared_data_model /home/shared_data_model
COPY shared_code /home/shared_code

HEALTHCHECK CMD python /home/server/healthcheck.py

ENV PATH="/home/server/venv/bin:$PATH"
CMD ["python", "/home/server/quality_time_server.py"]
