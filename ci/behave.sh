#!/bin/bash

# Start the server under coverage and run the feature tests.
# This script assumes the database and LDAP containers are running.

# We collect both the coverage of the server and of the tests themselves
# so we can discover dead code in the tests.

trap "kill 0" EXIT  # Kill server on Ctrl-C
export COVERAGE_RCFILE="$(pwd)"/.coveragerc-behave
cd components/server || exit
python3 -m venv venv
. venv/bin/activate
pip --quiet install --progress-bar off -r requirements.txt -r requirements-dev.txt
coverage erase
export COVERAGE_PROCESS_START=$COVERAGE_RCFILE
export RENDERER_HOST=localhost
python tests/quality_time_server_under_coverage.py &> /tmp/quality_time_server.log &
sleep 3  # Give server time to start up
deactivate
cd ../..
python3 -m venv venv
. venv/bin/activate
pip --quiet install --progress-bar off -r requirements-dev.txt
coverage erase
coverage run -m behave "${1:-tests/features}"
kill -s TERM "$(pgrep -n -f tests/quality_time_server_under_coverage.py)"
sleep 2  # Give the server time to write the coverage data
coverage combine . components/server
coverage xml -o build/features-coverage.xml
coverage html --directory build/features-coverage
coverage report --fail-under=96 --skip-covered
