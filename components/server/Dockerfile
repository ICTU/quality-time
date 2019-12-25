FROM python:3.8-slim-buster

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time server"

# We need to compile greenlet ourselves as there's no wheel for Python 3.8 yet, see https://github.com/python-greenlet/greenlet/issues/151
RUN build_time_deps='gcc' \
  && lxml_run_time_deps='libxml2-dev libxslt-dev' \
  && apt-get update \
  && apt-get install -y --no-install-recommends $build_time_deps $lxml_run_time_deps \
  && pip install greenlet==0.4.15 \
  && apt-get purge --auto-remove -y $build_time_deps \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY src /server
WORKDIR /server

CMD ["python", "/server/quality_time_server.py"]
