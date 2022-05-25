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
