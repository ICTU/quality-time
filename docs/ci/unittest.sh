#!/bin/sh

set -e

export PYTHONDEVMODE=1
# For Windows compatibility; prevent path from ending with a ':'
export PYTHONPATH=`python -c 'import sys;print(":".join(sys.argv[1:]))' src $PYTHONPATH`
export COVERAGE_RCFILE=../.coveragerc

coverage run -m unittest --quiet
coverage report --fail-under=0
coverage html --fail-under=0
coverage xml  # Fail if coverage is too low, but only after the text and HTML reports have been generated
