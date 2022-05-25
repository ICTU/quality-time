#!/bin/sh

set -e

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

# Install the requirements
run pip install --quiet -r requirements/requirements-base.txt
run pip install --quiet -r requirements/requirements-dev.txt
run pip install --quiet -r requirements/requirements-internal.txt
