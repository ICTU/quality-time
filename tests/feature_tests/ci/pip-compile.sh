#!/bin/sh

set -e

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

# Update the compiled requirements files
run pip-compile --allow-unsafe --generate-hashes --quiet requirements/requirements-base.in
run pip-compile --allow-unsafe --generate-hashes --quiet requirements/requirements-dev.in
