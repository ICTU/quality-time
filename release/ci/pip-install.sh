#!/bin/bash

source ../ci/base.sh

# Install the requirements
run pip install --ignore-installed --quiet -r requirements/requirements-dev.txt
