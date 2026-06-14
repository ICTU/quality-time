FROM python:3.14.5-alpine3.23@sha256:5a824eb82cc75361f98611f3cfc5091ea33f10a6ccea4d4ebdabbc523b9a1614

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time notifier"

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PYTHON_DOWNLOADS=0 VIRTUAL_ENV=/home/notifier/venv HEALTH_CHECK_FILE=/tmp/health_check.txt

WORKDIR /home/notifier

# After installing the notifier, reduce the attack surface to approximate a hardened base image: remove the package
# manager, the shell, and the Python installer and developer tools, none of which are needed to run the notifier.
# Note that this means the running container has no shell, so `docker exec <container> sh` will not work.
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=tools/third_party,target=/tools/third_party,rw \
    --mount=type=bind,source=components/shared_code,target=/home/shared_code,rw \
    --mount=type=bind,source=components/notifier/uv.lock,target=/home/notifier/uv.lock \
    --mount=type=bind,source=components/notifier/pyproject.toml,target=/home/notifier/pyproject.toml \
    uv sync --active --frozen --no-dev --no-install-project && \
    apk add --no-cache tzdata=2026b-r0 && \
    adduser -S notifier && \
    rm -rf /usr/local/bin/pip* /usr/local/bin/idle* /usr/local/bin/pydoc* /usr/local/bin/2to3* \
        /usr/local/lib/python*/site-packages/pip \
        /usr/local/lib/python*/site-packages/pip-* \
        /usr/local/lib/python*/ensurepip /usr/local/lib/python*/idlelib && \
    apk --purge --quiet del apk-tools alpine-keys musl-utils scanelf ssl_client && \
    rm -rf /etc/apk /lib/apk /var/cache/apk /bin/sh /bin/busybox

USER notifier

HEALTHCHECK CMD ["python", "-c", "from datetime import datetime as dt, timedelta, UTC; import os, sys; sys.exit(dt.now(tz=UTC) - dt.fromisoformat(open(os.environ['HEALTH_CHECK_FILE'], encoding='utf-8').read().strip()) > timedelta(seconds=600))"]

COPY components/notifier/src /home/notifier

ENV PATH="/home/notifier/venv/bin:$PATH"
CMD ["python", "/home/notifier/quality_time_notifier.py"]
