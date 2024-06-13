#!/bin/bash

PATH="$PATH:../ci"
source pip-base.sh

run_pip_install -r requirements/requirements-dev.txt
