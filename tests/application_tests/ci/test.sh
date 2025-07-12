#!/bin/bash

cd tests/application_tests
uv sync --locked --extra dev
.venv/bin/python -m unittest discover --start-directory .
