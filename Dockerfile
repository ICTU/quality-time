FROM python:3.7-alpine

LABEL maintainer="Frank Niessink <frank@niessink.com>"
LABEL description="Metric API"

WORKDIR /quality_time
ADD . /quality_time
RUN pip install -r requirements.txt; python setup.py install
EXPOSE 8080

CMD ["quality-time"]
