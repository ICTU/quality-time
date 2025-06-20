FROM python:3.13.5-alpine3.22 AS compile-image

WORKDIR /home/notifier

RUN apk add --no-cache gcc=14.2.0-r6 libffi-dev=3.4.8-r0 make=4.4.1-r3 && \
    python -m venv venv
ENV PATH="/home/notifier/venv/bin:$PATH"
COPY notifier/requirements/requirements.txt /requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt
COPY shared_code /home/shared_code/
COPY notifier/requirements/requirements-internal.txt /requirements-internal.txt
RUN pip install --no-cache-dir --use-pep517 -r /requirements-internal.txt

FROM python:3.13.5-alpine3.22

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time notifier"

ENV HEALTH_CHECK_FILE=/home/notifier/health_check.txt
RUN adduser -S notifier && adduser notifier root
WORKDIR /home/notifier
USER notifier

RUN touch ${HEALTH_CHECK_FILE} && chmod g+w ${HEALTH_CHECK_FILE} && chgrp root ${HEALTH_CHECK_FILE}
# Use the Shell form of CMD instead of the Exec form so the environment variable is substituted
# hadolint ignore=DL3025
HEALTHCHECK CMD python -c "from datetime import datetime as dt, timedelta, UTC; import sys; sys.exit(dt.now(tz=UTC) - dt.fromisoformat(open('${HEALTH_CHECK_FILE}', encoding='utf-8').read().strip()) > timedelta(seconds=600))"

COPY --from=compile-image /home/notifier/venv /home/notifier/venv
COPY notifier/src /home/notifier
COPY shared_code /home/shared_code

ENV PATH="/home/notifier/venv/bin:$PATH"
CMD ["python", "/home/notifier/quality_time_notifier.py"]
