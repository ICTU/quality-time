#!/bin/sh

export PYTHONDEVMODE=1
export PYTHONPATH=src:$PYTHONPATH
export COVERAGE_RCFILE=../../.coveragerc
coverage run -m unittest --quiet
coverage xml
coverage html
coverage report
