#!/bin/sh

set -e

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

# Install the requirements
run pip install --ignore-installed --quiet --use-pep517 -r requirements/requirements-dev.txt
run pip install --ignore-installed --quiet --use-pep517 -r requirements/requirements-internal.txt
