#!/bin/bash

cd tests/application_tests
uv sync --locked --all-groups
.venv/bin/python -m unittest discover --start-directory .
