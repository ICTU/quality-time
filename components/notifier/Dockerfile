FROM python:3.10.1-buster

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time notifier"

RUN python -m pip install --upgrade pip
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt

RUN useradd --create-home notifier
WORKDIR /home/notifier
USER notifier

COPY src /home/notifier

HEALTHCHECK CMD python -c "from datetime import datetime as dt, timedelta; import sys; sys.exit(dt.now() - dt.fromisoformat(open('/home/notifier/health_check.txt', encoding='utf-8').read().strip()) > timedelta(seconds=600))"

CMD ["python", "/home/notifier/quality_time_notifier.py"]
