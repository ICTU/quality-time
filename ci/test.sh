#!/bin/sh

docker build -t ictu/quality-time_selenium tests
docker run -v `pwd`:`pwd` -w `pwd` -it ictu/quality-time_selenium python -m unittest discover --start-directory tests --quiet
