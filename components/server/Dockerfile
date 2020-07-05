FROM python:3.9.0-buster

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time server"

RUN lxml_run_time_deps='libxml2-dev libxslt-dev' \
  && apt-get update \
  && apt-get -y upgrade \
  && apt-get install -y --no-install-recommends curl $lxml_run_time_deps \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

RUN useradd --create-home server
WORKDIR /home/server
USER server

COPY src /home/server

HEALTHCHECK CMD curl -f http://localhost:${SERVER_PORT:-5001}/api/health || exit 1

CMD ["python", "/home/server/quality_time_server.py"]
