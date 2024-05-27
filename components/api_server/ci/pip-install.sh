#!/bin/bash

source ../../ci/base.sh

# Install the requirements
run pip install --ignore-installed --quiet --use-pep517 -r requirements/requirements-dev.txt
run pip install --ignore-installed --quiet --use-pep517 -r requirements/requirements-internal.txt
