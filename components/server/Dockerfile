FROM python:3.8-buster

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time server"

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
WORKDIR /server
COPY src /server

CMD ["python", "/server/quality_time_server.py"]
