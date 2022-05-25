FROM python:3.10.4-bullseye AS compile-image

RUN useradd --create-home internal_server
WORKDIR /home/internal_server

RUN python -m venv venv
ENV PATH="/home/internal_server/venv/bin:$PATH"
COPY internal_server/requirements/requirements-base.txt /requirements-base.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements-base.txt
COPY internal_server/requirements/requirements.txt /requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt
COPY internal_server/requirements/requirements-internal.txt /requirements-internal.txt
COPY shared_python /home/shared_python/
RUN pip install --no-cache-dir -r /requirements-internal.txt

FROM python:3.10.4-slim-bullseye

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time internal_server"

RUN apt-get update && \
    apt-get install --yes --no-install-recommends curl=7.74\* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home internal_server
WORKDIR /home/internal_server
USER internal_server

HEALTHCHECK CMD curl -f http://localhost:${SERVER_PORT:-5002}/api/health || exit 1

COPY --from=compile-image /home/internal_server/venv /home/internal_server/venv
COPY internal_server/src /home/internal_server
COPY shared_python /home/shared_python

ENV PATH="/home/internal_server/venv/bin:$PATH"
CMD ["python", "/home/internal_server/quality_time_server.py"]
