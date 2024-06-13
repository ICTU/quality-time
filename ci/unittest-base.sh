#!/bin/bash

source base.sh

# Turn on development mode, see https://docs.python.org/3/library/devmode.html
export PYTHONDEVMODE=1

run_coverage() {
    run coverage run -m unittest --quiet
    run coverage report --fail-under=0
    run coverage html --fail-under=0
    run coverage xml  # Fail if coverage is too low, but only after the text and HTML reports have been generated
}
