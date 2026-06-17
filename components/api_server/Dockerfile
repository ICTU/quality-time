FROM python:3.14.6-alpine3.23@sha256:02da11a8d221ca167aa07de20b3cd7104c1f01227f4b02b1fa13cf6517280a81

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time API-server"

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PYTHON_DOWNLOADS=0 VIRTUAL_ENV=/home/api_server/venv

WORKDIR /home/api_server

# After installing the API-server, reduce the attack surface to approximate a hardened base image: remove the package
# manager, the shell, and the Python installer and developer tools, none of which are needed to run the API-server.
# Note that this means the running container has no shell, so `docker exec <container> sh` will not work.
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=tools/third_party,target=/tools/third_party,rw \
    --mount=type=bind,source=components/shared_code,target=/home/shared_code,rw \
    --mount=type=bind,source=components/api_server/uv.lock,target=/home/api_server/uv.lock \
    --mount=type=bind,source=components/api_server/pyproject.toml,target=/home/api_server/pyproject.toml \
    uv sync --active --frozen --no-dev --no-install-project && \
    apk add --no-cache tzdata=2026b-r0 && \
    adduser -S api_server && \
    rm -rf /usr/local/bin/pip* /usr/local/bin/idle* /usr/local/bin/pydoc* /usr/local/bin/2to3* \
        /usr/local/lib/python*/site-packages/pip \
        /usr/local/lib/python*/site-packages/pip-* \
        /usr/local/lib/python*/ensurepip /usr/local/lib/python*/idlelib && \
    apk --purge --quiet del apk-tools alpine-keys musl-utils scanelf ssl_client && \
    rm -rf /etc/apk /lib/apk /var/cache/apk /bin/sh /bin/busybox

USER api_server

HEALTHCHECK CMD ["python", "/home/api_server/healthcheck.py"]

COPY components/api_server/src /home/api_server

ENV PATH="/home/api_server/venv/bin:$PATH"
CMD ["python", "/home/api_server/quality_time_api_server.py"]
