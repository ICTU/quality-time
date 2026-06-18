FROM python:3.14.6-alpine3.23@sha256:02da11a8d221ca167aa07de20b3cd7104c1f01227f4b02b1fa13cf6517280a81

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time testdata"

WORKDIR /work
COPY . /work

CMD ["python", "-u", "-m", "http.server"]
