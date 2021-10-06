#!/bin/sh

cd tests/application_tests
python3 -m pip --quiet install --progress-bar off --user -r requirements-dev.txt
python3 -m unittest discover --start-directory .
