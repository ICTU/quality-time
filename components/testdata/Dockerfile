FROM python:3.15.0b4-alpine3.24@sha256:c40ec5a55436b283c1570e649ff40a8188e7e0221d7f285e624b20167c712ead

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time testdata"

WORKDIR /work
COPY . /work

CMD ["python", "-u", "-m", "http.server"]
