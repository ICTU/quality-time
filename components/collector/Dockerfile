FROM python:3.8-slim-buster

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time collector"

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

RUN useradd --create-home collector
WORKDIR /home/collector
USER collector

COPY src /home/collector

CMD ["python", "/home/collector/quality_time_collector.py"]
