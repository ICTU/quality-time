FROM python:3.14.6-alpine3.24@sha256:26730869004e2b9c4b9ad09cab8625e81d256d1ce97e72df5520e806b1709f92

ARG COMPONENT
LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time ${COMPONENT}"

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PYTHON_DOWNLOADS=0 VIRTUAL_ENV=/home/${COMPONENT}/venv

WORKDIR /home/${COMPONENT}

# After installing the component, reduce the attack surface to approximate a hardened base image: remove the package
# manager, the shell, and the Python installer and developer tools, none of which are needed to run the component.
# Note that this means the running container has no shell, so `docker exec <container> sh` will not work.
RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=tools/third_party,target=/tools/third_party,rw \
    --mount=type=bind,source=components/shared_code,target=/home/shared_code,rw \
    --mount=type=bind,source=components/${COMPONENT}/uv.lock,target=/home/${COMPONENT}/uv.lock \
    --mount=type=bind,source=components/${COMPONENT}/pyproject.toml,target=/home/${COMPONENT}/pyproject.toml \
    uv sync --active --frozen --no-dev --no-install-project && \
    apk add --no-cache tzdata=2026c-r0 && \
    adduser -S "${COMPONENT}" && \
    rm -rf /usr/local/bin/pip* /usr/local/bin/idle* /usr/local/bin/pydoc* /usr/local/bin/2to3* \
        /usr/local/lib/python*/site-packages/pip \
        /usr/local/lib/python*/site-packages/pip-* \
        /usr/local/lib/python*/ensurepip /usr/local/lib/python*/idlelib && \
    apk --purge --quiet del apk-tools alpine-keys musl-utils scanelf ssl_client && \
    rm -rf /etc/apk /lib/apk /var/cache/apk /bin/sh /bin/busybox

USER ${COMPONENT}

HEALTHCHECK CMD ["python", "healthcheck.py"]

COPY components/${COMPONENT}/src /home/${COMPONENT}

ENV PATH="/home/${COMPONENT}/venv/bin:$PATH"
CMD ["python", "main.py"]
