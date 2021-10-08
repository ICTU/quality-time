FROM python:3.10.0-buster

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time internal-server"

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

RUN useradd --create-home server
WORKDIR /home/server
USER server

COPY src /home/server

HEALTHCHECK CMD curl -f http://localhost:8000 || exit 1

CMD ["uvicorn", "quality_time_internal_server:app", "--host", "0.0.0.0"]
