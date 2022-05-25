#!/bin/sh

set -e

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

# Update the compiled requirements files
run pip-compile --allow-unsafe --generate-hashes --quiet requirements-base.in 
run pip-compile --allow-unsafe --generate-hashes --quiet requirements.in 
run pip-compile --allow-unsafe --generate-hashes --quiet requirements-dev.in
# Install the requirements from the compiled requirements files
run pip install --quiet -r requirements-base.txt
run pip install --quiet -r requirements.txt
run pip install --quiet -r requirements-dev.txt

