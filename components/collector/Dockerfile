FROM python:3.7-alpine

LABEL maintainer="Frank Niessink <frank.niessink@ictu.nl>"
LABEL description="Quality-time collector"

WORKDIR /work
ADD . /work
RUN pip install --no-cache-dir -r requirements.txt; python setup.py install

CMD ["python", "src/quality_time_collector.py"]
