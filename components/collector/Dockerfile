FROM python:3.9.6-buster

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time collector"

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

RUN useradd --create-home collector
WORKDIR /home/collector
USER collector

COPY src /home/collector

HEALTHCHECK CMD python -c "from datetime import datetime as dt, timedelta; import sys; sys.exit(dt.now() - dt.fromisoformat(open('/home/collector/health_check.txt', encoding='utf-8').read().strip()) > timedelta(seconds=600))"

CMD ["python", "/home/collector/quality_time_collector.py"]
