FROM python:3.10.4-bullseye AS compile-image

RUN useradd --create-home server
WORKDIR /home/server

RUN python -m venv venv
ENV PATH="/home/server/venv/bin:$PATH"
RUN python -m pip install --upgrade pip
RUN python -m pip install wheel
COPY server/requirements.txt /requirements.txt
COPY server/requirements-internal.txt /requirements-internal.txt
COPY shared_python /home/shared_python/
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt
RUN pip install --no-cache-dir -r /requirements-internal.txt

FROM python:3.10.4-slim-bullseye

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time server"

RUN apt-get update && \
    apt-get install --yes --no-install-recommends curl=7.74\* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd --create-home server
WORKDIR /home/server
USER server

HEALTHCHECK CMD curl -f http://localhost:${SERVER_PORT:-5001}/api/health || exit 1

COPY --from=compile-image /home/server/venv /home/server/venv
COPY server/src /home/server
COPY shared_python /home/shared_python

ENV PATH="/home/server/venv/bin:$PATH"
CMD ["python", "/home/server/quality_time_server.py"]
