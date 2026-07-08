FROM python:3.14.6-alpine3.24@sha256:26730869004e2b9c4b9ad09cab8625e81d256d1ce97e72df5520e806b1709f92

LABEL maintainer="Quality-time team <quality-time@ictu.nl>"
LABEL description="Quality-time testdata"

WORKDIR /work
COPY . /work

CMD ["python", "-u", "-m", "http.server"]
