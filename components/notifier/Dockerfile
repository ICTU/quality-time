FROM python:3.10.5-bullseye AS compile-image

WORKDIR /home/notifier

RUN python -m venv venv
ENV PATH="/home/notifier/venv/bin:$PATH"
COPY notifier/requirements/requirements-base.txt /requirements-base.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements-base.txt
COPY notifier/requirements/requirements.txt /requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt
COPY shared_data_model /home/shared_data_model/
COPY notifier/requirements/requirements-internal.txt /requirements-internal.txt
RUN pip install --no-cache-dir -r /requirements-internal.txt

FROM python:3.10.5-bullseye

LABEL maintainer="Quality-time team <Quality-time@ictu.nl>"
LABEL description="Quality-time notifier"

RUN useradd --create-home notifier
WORKDIR /home/notifier
USER notifier

HEALTHCHECK CMD python -c "from datetime import datetime as dt, timedelta; import sys; sys.exit(dt.now() - dt.fromisoformat(open('/home/notifier/health_check.txt', encoding='utf-8').read().strip()) > timedelta(seconds=600))"

COPY --from=compile-image /home/notifier/venv /home/notifier/venv
COPY notifier/src /home/notifier
COPY shared_data_model /home/shared_data_model

ENV PATH="/home/notifier/venv/bin:$PATH"
CMD ["python", "/home/notifier/quality_time_notifier.py"]
