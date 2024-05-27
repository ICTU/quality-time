#!/bin/bash

set -e

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

# Install the requirements
run pip install --ignore-installed --quiet -r requirements/requirements.txt -r requirements/requirements-dev.txt
