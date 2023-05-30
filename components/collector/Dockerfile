FROM python:3.11.3-alpine3.17 AS compile-image

WORKDIR /home/collector

RUN python -m venv venv
ENV PATH="/home/collector/venv/bin:$PATH"
COPY collector/requirements/requirements.txt /requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt
COPY shared_data_model /home/shared_data_model/
COPY shared_server_code /home/shared_server_code/
COPY collector/requirements/requirements-internal.txt /requirements-internal.txt
RUN pip install --no-cache-dir -r /requirements-internal.txt

FROM python:3.11.3-alpine3.17

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time collector"

ENV HEALTH_CHECK_FILE=/home/collector/health_check.txt
RUN adduser -S collector && adduser collector root
WORKDIR /home/collector
USER collector

RUN touch ${HEALTH_CHECK_FILE} && chmod g+w ${HEALTH_CHECK_FILE} && chgrp root ${HEALTH_CHECK_FILE}
HEALTHCHECK CMD python -c "from datetime import datetime as dt, timedelta, UTC; import sys; sys.exit(dt.now(tz=UTC) - dt.fromisoformat(open('${HEALTH_CHECK_FILE}', encoding='utf-8').read().strip()) > timedelta(seconds=600))"

COPY --from=compile-image /home/collector/venv /home/collector/venv
COPY collector/src /home/collector
COPY shared_data_model /home/shared_data_model
COPY shared_server_code /home/shared_server_code

ENV PATH="/home/collector/venv/bin:$PATH"
CMD ["python", "/home/collector/quality_time_collector.py"]
