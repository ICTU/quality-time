FROM python:3.7-alpine

LABEL maintainer="Frank Niessink <frank@niessink.com>"
LABEL description="Metric API"

WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
EXPOSE 8080

CMD ["python", "app.py"]
