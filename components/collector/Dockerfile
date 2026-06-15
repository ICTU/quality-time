FROM python:3.15.0b2-alpine3.23@sha256:8d3de8aae4a0549621b4053ca36a849d89300f7f114d5f5a89a037c783743c62

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time collector"

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PYTHON_DOWNLOADS=0 VIRTUAL_ENV=/home/collector/venv HEALTH_CHECK_FILE=/tmp/health_check.txt

WORKDIR /home/collector

# After installing the collector, reduce the attack surface to approximate a hardened base image: remove the package
# manager, the shell, and the Python installer and developer tools, none of which are needed to run the collector.
# Note that this means the running container has no shell, so `docker exec <container> sh` will not work.
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=tools/third_party,target=/tools/third_party,rw \
    --mount=type=bind,source=components/shared_code,target=/home/shared_code,rw \
    --mount=type=bind,source=components/collector/uv.lock,target=/home/collector/uv.lock \
    --mount=type=bind,source=components/collector/pyproject.toml,target=/home/collector/pyproject.toml \
    uv sync --active --frozen --no-dev --no-install-project && \
    apk add --no-cache tzdata=2026b-r0 && \
    adduser -S collector && \
    rm -rf /usr/local/bin/pip* /usr/local/bin/idle* /usr/local/bin/pydoc* /usr/local/bin/2to3* \
        /usr/local/lib/python*/site-packages/pip \
        /usr/local/lib/python*/site-packages/pip-* \
        /usr/local/lib/python*/ensurepip /usr/local/lib/python*/idlelib && \
    apk --purge --quiet del apk-tools alpine-keys musl-utils scanelf ssl_client && \
    rm -rf /etc/apk /lib/apk /var/cache/apk /bin/sh /bin/busybox

USER collector

HEALTHCHECK CMD ["python", "-c", "from datetime import datetime as dt, timedelta, UTC; import os, sys; sys.exit(dt.now(tz=UTC) - dt.fromisoformat(open(os.environ['HEALTH_CHECK_FILE'], encoding='utf-8').read().strip()) > timedelta(seconds=600))"]

COPY components/collector/src /home/collector

ENV PATH="/home/collector/venv/bin:$PATH"
CMD ["python", "/home/collector/quality_time_collector.py"]
