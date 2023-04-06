#!/bin/sh

set -e

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

# Update the compiled requirements files
run pip-compile --allow-unsafe --generate-hashes --quiet --resolver=backtracking --upgrade --output-file requirements/requirements.txt pyproject.toml
run pip-compile --allow-unsafe --generate-hashes --quiet --resolver=backtracking --upgrade --extra dev --output-file requirements/requirements-dev.txt pyproject.toml
