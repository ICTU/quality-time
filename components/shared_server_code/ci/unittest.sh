#!/bin/bash

source ../../ci/base.sh

export COVERAGE_RCFILE=../../.coveragerc

coverage run -m unittest --quiet
coverage report --fail-under=0
coverage html --fail-under=0
coverage xml  # Fail if coverage is too low, but only after the text and HTML reports have been generated
