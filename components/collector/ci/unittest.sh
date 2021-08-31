#!/bin/sh

export PYTHONDEVMODE=1
# For Windows compatibility; prevent path from ending with a ':'
export PYTHONPATH=`python -c 'import sys;print(":".join(sys.argv[1:]))' src $PYTHONPATH`
export COVERAGE_RCFILE=../../.coveragerc

coverage run -m unittest --quiet
coverage xml
coverage html
coverage report
