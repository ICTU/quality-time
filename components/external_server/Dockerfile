FROM python:3.10.4-bullseye AS compile-image

WORKDIR /home/external_server

RUN python -m venv venv
ENV PATH="/home/external_server/venv/bin:$PATH"
COPY external_server/requirements/requirements-base.txt /requirements-base.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements-base.txt
COPY external_server/requirements/requirements.txt /requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt
COPY external_server/requirements/requirements-internal.txt /requirements-internal.txt
COPY shared_python /home/shared_python/
RUN pip install --no-cache-dir -r /requirements-internal.txt

FROM python:3.10.4-slim-bullseye

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time external_server"

RUN apt-get update && \
    apt-get install --yes --no-install-recommends curl=7.74\* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home external_server
WORKDIR /home/external_server
USER external_server

HEALTHCHECK CMD curl -f http://localhost:${EXTERNAL_SERVER_PORT:-5001}/api/health || exit 1

COPY --from=compile-image /home/external_server/venv /home/external_server/venv
COPY external_server/src /home/external_server
COPY shared_python /home/shared_python

ENV PATH="/home/external_server/venv/bin:$PATH"
CMD ["python", "/home/external_server/quality_time_server.py"]
