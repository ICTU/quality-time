FROM python:3.10.5-bullseye AS compile-image

WORKDIR /home/server

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

FROM python:3.10.5-bullseye

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time internal server"

RUN apt-get update && \
    apt-get install --yes --no-install-recommends curl=7.74\* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home server
WORKDIR /home/server
USER server

HEALTHCHECK CMD curl -f http://localhost:${INTERNAL_SERVER_PORT:-5002}/api/health || exit 1

COPY --from=compile-image /home/server/venv /home/server/venv
COPY internal_server/src /home/server
COPY shared_data_model /home/shared_data_model
COPY shared_server_code /home/shared_server_code

ENV PATH="/home/server/venv/bin:$PATH"
CMD ["python", "/home/server/quality_time_server.py"]
