#!/bin/sh

cd tests/application_tests
python3 -m venv venv
. venv/bin/activate
pip --quiet install --upgrade pip
pip --quiet install --progress-bar off -r requirements.txt
python -m unittest discover --start-directory .
