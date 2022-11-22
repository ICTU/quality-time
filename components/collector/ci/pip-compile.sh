#!/bin/sh

set -e

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

# Update the compiled requirements files
cd requirements
run pip-compile --allow-unsafe --generate-hashes --quiet --resolver=backtracking requirements-base.in
run pip-compile --generate-hashes --quiet --resolver=backtracking requirements.in 
run pip-compile --allow-unsafe --generate-hashes --quiet --resolver=backtracking requirements-dev.in

