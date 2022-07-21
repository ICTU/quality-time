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
run pip-compile --upgrade-package pycares --generate-hashes --quiet requirements.in  # Force upgrade of pycares to fix security issue
run pip-compile --upgrade-package cachecontrol --allow-unsafe --generate-hashes --quiet requirements-dev.in  # Force upgrade to prevent circular redirect from PyPI
