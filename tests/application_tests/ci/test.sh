#!/bin/sh

sleep 60 # give time to start up docker containers

cd tests/application_tests
python3 -m venv venv
. venv/bin/activate
ci/pip-install.sh
python -m unittest discover --start-directory .

