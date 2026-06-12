FROM python:3.14.5-alpine3.23@sha256:5a824eb82cc75361f98611f3cfc5091ea33f10a6ccea4d4ebdabbc523b9a1614

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time collector"

RUN apk add --no-cache tzdata=2026b-r0

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PYTHON_DOWNLOADS=0 VIRTUAL_ENV=/home/collector/venv

WORKDIR /home/collector

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=tools/third_party,target=/tools/third_party,rw \
    --mount=type=bind,source=components/shared_code,target=/home/shared_code,rw \
    --mount=type=bind,source=components/collector/uv.lock,target=/home/collector/uv.lock \
    --mount=type=bind,source=components/collector/pyproject.toml,target=/home/collector/pyproject.toml \
    uv sync --active --frozen --no-dev --no-install-project

ENV HEALTH_CHECK_FILE=/home/collector/health_check.txt
RUN adduser -S collector && adduser collector root
USER collector

RUN touch "${HEALTH_CHECK_FILE}" && chmod g+w "${HEALTH_CHECK_FILE}" && chgrp root "${HEALTH_CHECK_FILE}"
HEALTHCHECK CMD ["python", "-c", "from datetime import datetime as dt, timedelta, UTC; import os, sys; sys.exit(dt.now(tz=UTC) - dt.fromisoformat(open(os.environ['HEALTH_CHECK_FILE'], encoding='utf-8').read().strip()) > timedelta(seconds=600))"]

COPY components/collector/src /home/collector

ENV PATH="/home/collector/venv/bin:$PATH"
CMD ["python", "/home/collector/quality_time_collector.py"]
