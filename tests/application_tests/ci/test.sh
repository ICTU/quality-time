#!/bin/sh

cd tests/application_tests
pip --quiet install --progress-bar off --user -r requirements-dev.txt
python -m unittest discover --start-directory .
