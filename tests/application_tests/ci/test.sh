#!/bin/sh

cd tests/application_tests
python3 -m venv venv
. venv/bin/activate
ci/pip-install.sh
docker compose ps
python -m unittest discover --start-directory .
