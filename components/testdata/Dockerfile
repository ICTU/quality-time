FROM dhi.io/python:3.14.5-alpine3.23@sha256:658c88b53d0525c13675b3808fbaeebe912eb8fe64ee3b761dfcc12787334981

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time testdata"

WORKDIR /work
COPY . /work

CMD ["python", "-u", "-m", "http.server"]
