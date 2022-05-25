#!/bin/sh

cd tests/application_tests
python3 -m venv venv
. venv/bin/activate
pip --quiet install --progress-bar off -r requirements-base.txt
pip --quiet install --progress-bar off -r requirements.txt
pip --quiet install --progress-bar off -r requirements-dev.txt
python -m unittest discover --start-directory .

