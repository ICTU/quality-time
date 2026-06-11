FROM python:3.15.0b2-alpine3.23@sha256:8d3de8aae4a0549621b4053ca36a849d89300f7f114d5f5a89a037c783743c62

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time testdata"

WORKDIR /work
COPY . /work

CMD ["python", "-u", "-m", "http.server"]
