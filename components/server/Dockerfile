FROM python:3.10.1-buster AS compile-image

RUN useradd --create-home server
WORKDIR /home/server
USER server

RUN python -m venv venv
ENV PATH="/home/server/venv/bin:$PATH"
RUN python -m pip install --upgrade pip
RUN python -m pip install wheel
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --require-hashes -r /requirements.txt

FROM python:3.10.1-slim-buster

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time server"

RUN useradd --create-home server
WORKDIR /home/server
USER server

HEALTHCHECK CMD curl -f http://localhost:${SERVER_PORT:-5001}/api/health || exit 1

COPY --from=compile-image /home/server/venv /home/server/venv
COPY src /home/server

ENV PATH="/home/server/venv/bin:$PATH"
CMD ["python", "/home/server/quality_time_server.py"]
