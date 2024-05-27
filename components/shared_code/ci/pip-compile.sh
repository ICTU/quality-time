#!/bin/bash

source ../../ci/base.sh

# Update the compiled requirements files
run pip-compile --extra dev --output-file requirements/requirements-dev.txt pyproject.toml
