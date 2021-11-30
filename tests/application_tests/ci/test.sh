#!/bin/sh

cd tests/application_tests
pip --quiet install --progress-bar off --user --upgrade pip
pip --quiet install --progress-bar off --user --require-hashes -r requirements.txt
python -m unittest discover --start-directory .
