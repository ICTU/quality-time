FROM python:3.10.4-bullseye AS compile-image

RUN useradd --create-home notifier
WORKDIR /home/notifier
USER notifier

RUN python -m venv venv
ENV PATH="/home/notifier/venv/bin:$PATH"
RUN python -m pip install --upgrade pip
RUN python -m pip install wheel
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt

FROM python:3.10.4-slim-bullseye

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time notifier"

RUN useradd --create-home notifier
WORKDIR /home/notifier
USER notifier

HEALTHCHECK CMD python -c "from datetime import datetime as dt, timedelta; import sys; sys.exit(dt.now() - dt.fromisoformat(open('/home/notifier/health_check.txt', encoding='utf-8').read().strip()) > timedelta(seconds=600))"

COPY --from=compile-image /home/notifier/venv /home/notifier/venv
COPY src /home/notifier

ENV PATH="/home/notifier/venv/bin:$PATH"
CMD ["python", "/home/notifier/quality_time_notifier.py"]
