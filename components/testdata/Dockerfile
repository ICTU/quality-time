FROM python:3.9.0-slim-buster

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time testdata"

WORKDIR /work
ADD . /work

CMD ["python", "-u", "-m", "http.server"]
