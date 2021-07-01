FROM python:3.9.6-buster

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time notifier"

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

RUN useradd --create-home notifier
WORKDIR /home/notifier
USER notifier

COPY src /home/notifier

HEALTHCHECK CMD python -c "from datetime import datetime as dt, timedelta; import sys; sys.exit(dt.now() - dt.fromisoformat(open('/home/notifier/health_check.txt').read().strip()) > timedelta(seconds=600))"

CMD ["python", "/home/notifier/quality_time_notifier.py"]
