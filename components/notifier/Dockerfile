FROM python:3.14.1-alpine3.22

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time notifier"

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PYTHON_DOWNLOADS=0 VIRTUAL_ENV=/home/notifier/venv

WORKDIR /home/notifier

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=shared_code,target=/home/shared_code,rw \
    --mount=type=bind,source=notifier/uv.lock,target=/home/notifier/uv.lock \
    --mount=type=bind,source=notifier/pyproject.toml,target=/home/notifier/pyproject.toml \
    uv sync --active --locked --no-dev --no-install-project

ENV HEALTH_CHECK_FILE=/home/notifier/health_check.txt
RUN adduser -S notifier && adduser notifier root
USER notifier

RUN touch ${HEALTH_CHECK_FILE} && chmod g+w ${HEALTH_CHECK_FILE} && chgrp root ${HEALTH_CHECK_FILE}
# Use the Shell form of CMD instead of the Exec form so the environment variable is substituted
# hadolint ignore=DL3025
HEALTHCHECK CMD python -c "from datetime import datetime as dt, timedelta, UTC; import sys; sys.exit(dt.now(tz=UTC) - dt.fromisoformat(open('${HEALTH_CHECK_FILE}', encoding='utf-8').read().strip()) > timedelta(seconds=600))"

COPY notifier/src /home/notifier

ENV PATH="/home/notifier/venv/bin:$PATH"
CMD ["python", "/home/notifier/quality_time_notifier.py"]
