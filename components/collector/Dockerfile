FROM python:3.15.0b2-alpine3.23@sha256:8d3de8aae4a0549621b4053ca36a849d89300f7f114d5f5a89a037c783743c62

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

ENV HEALTH_CHECK_FILE=/tmp/health_check.txt
RUN adduser -S collector
USER collector

HEALTHCHECK CMD ["python", "-c", "from datetime import datetime as dt, timedelta, UTC; import os, sys; sys.exit(dt.now(tz=UTC) - dt.fromisoformat(open(os.environ['HEALTH_CHECK_FILE'], encoding='utf-8').read().strip()) > timedelta(seconds=600))"]

COPY components/collector/src /home/collector

ENV PATH="/home/collector/venv/bin:$PATH"
CMD ["python", "/home/collector/quality_time_collector.py"]
