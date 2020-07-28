#!/bin/sh

export PYTHONDEVMODE=1
export PYTHONPATH=src:$PYTHONPATH
export COVERAGE_RCFILE=../../.coveragerc
coverage run --branch -m unittest --quiet
coverage xml -o build/unittest-coverage.xml
coverage html --directory build/unittest-coverage --show-contexts
coverage report --skip-covered --fail-under=100
