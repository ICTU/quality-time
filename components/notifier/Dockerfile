FROM python:3.11.3-alpine3.17 AS compile-image

WORKDIR /home/notifier

RUN python -m venv venv
ENV PATH="/home/notifier/venv/bin:$PATH"
COPY notifier/requirements/requirements.txt /requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt
COPY shared_data_model /home/shared_data_model/
COPY shared_server_code /home/shared_server_code/
COPY notifier/requirements/requirements-internal.txt /requirements-internal.txt
RUN pip install --no-cache-dir -r /requirements-internal.txt

FROM python:3.11.3-alpine3.17

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time notifier"

ENV HEALTH_CHECK_FILE=/home/notifier/health_check.txt
RUN adduser -S notifier && adduser notifier root
WORKDIR /home/notifier
USER notifier

RUN touch ${HEALTH_CHECK_FILE} && chmod g+w ${HEALTH_CHECK_FILE} && chgrp root ${HEALTH_CHECK_FILE}
HEALTHCHECK CMD python -c "from datetime import datetime as dt, timedelta; import sys; sys.exit(dt.now() - dt.fromisoformat(open('${HEALTH_CHECK_FILE}', encoding='utf-8').read().strip()) > timedelta(seconds=600))"

COPY --from=compile-image /home/notifier/venv /home/notifier/venv
COPY notifier/src /home/notifier
COPY shared_data_model /home/shared_data_model
# TODO: Move database code from shared_server_code to shared_data_model.
COPY shared_server_code /home/shared_server_code

ENV PATH="/home/notifier/venv/bin:$PATH"
CMD ["python", "/home/notifier/quality_time_notifier.py"]
