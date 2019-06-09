FROM python:3.7-alpine

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time testdata"

WORKDIR /work
ADD . /work

CMD ["python", "-m", "http.server"]
