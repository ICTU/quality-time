#!/bin/bash

source base.sh

# Turn on development mode, see https://docs.python.org/3/library/devmode.html
export PYTHONDEVMODE=1

run_coverage() {
    run .venv/bin/coverage run -m unittest --quiet
    run .venv/bin/coverage report --fail-under=0
    run .venv/bin/coverage html --fail-under=0
    run .venv/bin/coverage xml  # Fail if coverage is too low, but only after the text and HTML reports have been generated
}
