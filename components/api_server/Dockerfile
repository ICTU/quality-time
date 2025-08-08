FROM python:3.13.6-alpine3.22

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time API-server"

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PYTHON_DOWNLOADS=0 VIRTUAL_ENV=/home/server/venv

WORKDIR /home/server

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=shared_code,target=/home/shared_code,rw \
    --mount=type=bind,source=api_server/uv.lock,target=/home/server/uv.lock \
    --mount=type=bind,source=api_server/pyproject.toml,target=/home/server/pyproject.toml \
    uv sync --active --locked --no-dev --no-install-project

RUN adduser -S server
USER server

COPY api_server/src /home/server

HEALTHCHECK CMD ["python", "/home/server/healthcheck.py"]

ENV PATH="/home/server/venv/bin:$PATH"
CMD ["python", "/home/server/quality_time_server.py"]
