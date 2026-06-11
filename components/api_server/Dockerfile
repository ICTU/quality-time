FROM python:3.15.0b2-alpine3.23@sha256:8d3de8aae4a0549621b4053ca36a849d89300f7f114d5f5a89a037c783743c62

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time API-server"

RUN apk add --no-cache tzdata=2026b-r0

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PYTHON_DOWNLOADS=0 VIRTUAL_ENV=/home/server/venv

WORKDIR /home/server

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=tools/third_party,target=/tools/third_party,rw \
    --mount=type=bind,source=components/shared_code,target=/home/shared_code,rw \
    --mount=type=bind,source=components/api_server/uv.lock,target=/home/server/uv.lock \
    --mount=type=bind,source=components/api_server/pyproject.toml,target=/home/server/pyproject.toml \
    uv sync --active --frozen --no-dev --no-install-project

RUN adduser -S server
USER server

COPY components/api_server/src /home/server

HEALTHCHECK CMD ["python", "/home/server/healthcheck.py"]

ENV PATH="/home/server/venv/bin:$PATH"
CMD ["python", "/home/server/quality_time_server.py"]
