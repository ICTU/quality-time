#!/bin/bash

cd tests/application_tests
uv sync --no-progress --quiet --locked --all-groups
.venv/bin/python -m unittest discover --start-directory .
