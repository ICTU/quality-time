#!/bin/sh

export PYTHONDEVMODE=1
export PYTHONPATH=src:$PYTHONPATH
coverage run --omit=*venv/*,/home/travis/virtualenv/* --branch -m unittest --quiet
coverage xml -o build/unittest-coverage.xml
coverage html --directory build/unittest-coverage
coverage report --skip-covered --fail-under=100
