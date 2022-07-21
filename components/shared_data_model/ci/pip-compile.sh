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
run pip-compile --allow-unsafe --generate-hashes --quiet requirements-base.in
run pip-compile --upgrade --allow-unsafe --generate-hashes --quiet requirements-dev.in  # Add --upgrade to prevent 'Mismatched hash for lxml (4.9.1)' when running pip-audit
