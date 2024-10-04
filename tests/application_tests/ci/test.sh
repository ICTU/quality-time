#!/bin/bash

cd tests/application_tests
uv venv
ci/pip-install.sh
.venv/bin/python -m unittest discover --start-directory .
