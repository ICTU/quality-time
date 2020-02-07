FROM python:3.8-slim-buster

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time server"

RUN lxml_run_time_deps='libxml2-dev libxslt-dev' \
  && apt-get update \
  && apt-get install -y --no-install-recommends $lxml_run_time_deps \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY src /server
WORKDIR /server

CMD ["python", "/server/quality_time_server.py"]
