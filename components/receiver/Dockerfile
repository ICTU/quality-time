FROM python:3.7-alpine

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time receiver"

RUN apk add --no-cache --virtual .build-deps build-base python3-dev
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
RUN apk del --no-cache .build-deps
WORKDIR /receiver
COPY src /receiver

CMD ["python", "/receiver/quality_time_receiver.py"]
