FROM dhi.io/python:3.14.5-alpine3.23-dev@sha256:35e345d2ca9052ad826f62ea89c3e4e99de9290f356f193e588427868a0044ae AS compile-image

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PYTHON_DOWNLOADS=0 VIRTUAL_ENV=/home/server/venv

WORKDIR /home/server

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=tools/third_party,target=/tools/third_party,rw \
    --mount=type=bind,source=components/shared_code,target=/home/shared_code,rw \
    --mount=type=bind,source=components/api_server/uv.lock,target=/home/server/uv.lock \
    --mount=type=bind,source=components/api_server/pyproject.toml,target=/home/server/pyproject.toml \
    uv sync --active --frozen --no-dev --no-install-project

FROM dhi.io/python:3.14.5-alpine3.23@sha256:658c88b53d0525c13675b3808fbaeebe912eb8fe64ee3b761dfcc12787334981

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time API-server"

WORKDIR /home/server

COPY --from=compile-image /home/server/venv /home/server/venv
COPY components/api_server/src /home/server

HEALTHCHECK CMD ["python", "/home/server/healthcheck.py"]

ENV PATH="/home/server/venv/bin:$PATH"
CMD ["python", "/home/server/quality_time_server.py"]
