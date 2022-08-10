#!/bin/sh

cd tests/application_tests
python3 -m venv /tmp/venv-quality-time-application-tests
. /tmp/venv-quality-time-application-tests/bin/activate
ci/pip-install.sh
python -m unittest discover --start-directory .
deactivate
rm -rf /tmp/venv-quality-time-application-tests
