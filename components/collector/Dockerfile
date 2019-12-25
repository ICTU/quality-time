FROM python:3.8-slim-buster

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time collector"

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
WORKDIR /collector
COPY src /collector

CMD ["python", "/collector/quality_time_collector.py"]
