#!/bin/sh

set -e

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

# Install the requirements
run pip install -r requirements/requirements-base.txt
run pip install -r requirements/requirements.txt
run pip install -r requirements/requirements-dev.txt
run pip install -r requirements/requirements-internal.txt

