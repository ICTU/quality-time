FROM python:3.10.2-buster AS compile-image

RUN useradd --create-home collector
WORKDIR /home/collector
USER collector

RUN python -m venv venv
ENV PATH="/home/collector/venv/bin:$PATH"
RUN python -m pip install --upgrade pip
RUN python -m pip install wheel
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt

FROM python:3.10.2-buster

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time collector"

RUN useradd --create-home collector
WORKDIR /home/collector
USER collector

HEALTHCHECK CMD python -c "from datetime import datetime as dt, timedelta; import sys; sys.exit(dt.now() - dt.fromisoformat(open('/home/collector/health_check.txt', encoding='utf-8').read().strip()) > timedelta(seconds=600))"

COPY --from=compile-image /home/collector/venv /home/collector/venv
COPY src /home/collector

ENV PATH="/home/collector/venv/bin:$PATH"
CMD ["python", "/home/collector/quality_time_collector.py"]
