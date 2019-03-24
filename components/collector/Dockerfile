FROM python:3.7-alpine

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time collector"

WORKDIR /work
ADD . /work
RUN pip install -r requirements.txt; python setup.py install

CMD ["quality-time-collector"]
