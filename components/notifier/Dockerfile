FROM dhi.io/python:3.14.5-alpine3.23-dev@sha256:35e345d2ca9052ad826f62ea89c3e4e99de9290f356f193e588427868a0044ae AS compile-image

ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PYTHON_DOWNLOADS=0 VIRTUAL_ENV=/home/notifier/venv

WORKDIR /home/notifier

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=tools/third_party,target=/tools/third_party,rw \
    --mount=type=bind,source=components/shared_code,target=/home/shared_code,rw \
    --mount=type=bind,source=components/notifier/uv.lock,target=/home/notifier/uv.lock \
    --mount=type=bind,source=components/notifier/pyproject.toml,target=/home/notifier/pyproject.toml \
    uv sync --active --frozen --no-dev --no-install-project

ENV HEALTH_CHECK_FILE=/home/notifier/health_check.txt
# Make the health check file writable by the non-root user (65532) of the runtime image and by the
# root group, for platforms that run containers with an arbitrary user ID in the root group
RUN touch "${HEALTH_CHECK_FILE}" && chown 65532:0 "${HEALTH_CHECK_FILE}" && chmod g+w "${HEALTH_CHECK_FILE}"

FROM dhi.io/python:3.14.5-alpine3.23@sha256:658c88b53d0525c13675b3808fbaeebe912eb8fe64ee3b761dfcc12787334981

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time notifier"

WORKDIR /home/notifier

COPY --from=compile-image /home/notifier /home/notifier
COPY components/notifier/src /home/notifier

ENV HEALTH_CHECK_FILE=/home/notifier/health_check.txt
HEALTHCHECK CMD ["python", "-c", "from datetime import datetime as dt, timedelta, UTC; import os, sys; sys.exit(dt.now(tz=UTC) - dt.fromisoformat(open(os.environ['HEALTH_CHECK_FILE'], encoding='utf-8').read().strip()) > timedelta(seconds=600))"]

ENV PATH="/home/notifier/venv/bin:$PATH"
CMD ["python", "/home/notifier/quality_time_notifier.py"]
