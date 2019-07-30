FROM python:3.7-alpine

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time receiver"

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
WORKDIR /receiver
COPY src /receiver

CMD ["python", "/receiver/quality_time_receiver.py"]
