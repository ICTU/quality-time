FROM python:3.8-alpine

RUN echo "http://dl-4.alpinelinux.org/alpine/v3.8/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.8/community" >> /etc/apk/repositories

RUN apk update
RUN apk add chromium chromium-chromedriver

RUN pip install --upgrade pip
RUN pip install selenium
