FROM python:3.10.5-slim-bullseye

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time testdata"

WORKDIR /work
COPY . /work

CMD ["python", "-u", "-m", "http.server"]
