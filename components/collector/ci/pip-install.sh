#!/bin/bash

PATH="$PATH:../../ci"
source pip-base.sh

run_pip_install -r requirements/requirements-dev.txt
run_pip_install -r requirements/requirements-internal.txt
