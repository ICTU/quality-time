#!/bin/bash

# Start the server under coverage and run the feature tests.
# This script assumes the database and LDAP containers are running.

# We collect both the coverage of the server and of the tests themselves
# so we can discover dead code in the tests.

trap "kill 0" EXIT  # Kill server on Ctrl-C
# Start the components that we can't/won't measure the coverage of as docker containers:
docker-compose up -d database ldap renderer www
# Start the server under coverage:
export COVERAGE_RCFILE="$(pwd)"/tests/feature_tests/.coveragerc-server
cd components/server || exit
python3 -m venv venv
. venv/bin/activate
pip --quiet install --progress-bar off -r requirements.txt -r requirements-dev.txt
coverage erase
export RENDERER_HOST=localhost
python tests/quality_time_server_under_coverage.py &> /tmp/quality_time_server.log &
deactivate
cd ../..
# Start the internal-server under coverage:
export COVERAGE_RCFILE="$(pwd)"/tests/feature_tests/.coveragerc-internal-server
cd components/internal-server || exit
python3 -m venv venv
. venv/bin/activate
pip --quiet install --progress-bar off -r requirements.txt -r requirements-dev.txt
coverage erase
python tests/quality_time_internal_server_under_coverage.py &> /tmp/quality_time_internal_server.log &
deactivate
cd ../..
# We need to start a second server for the renderer. We start it after the server under
# coverage so we can measure the coverage of the startup code.
docker-compose up -d server
# Install the test dependencies:
cd tests/feature_tests
python3 -m venv venv
. venv/bin/activate
pip --quiet install --progress-bar off -r requirements-dev.txt
cd ../..
sleep 10  # Give server time to start up
export COVERAGE_RCFILE="$(pwd)"/tests/feature_tests/.coveragerc
coverage erase  # Clean up from previous runs
coverage run -m behave "${1:-tests/feature_tests/features}"  # Run the feature tests under coverage
kill -s TERM "$(pgrep -n -f tests/quality_time_server_under_coverage.py)"
kill -s TERM "$(pgrep -n -f tests/quality_time_internal_server_under_coverage.py)"
sleep 2  # Give the servers time to write the coverage data
coverage combine . components/server components/internal-server
coverage xml
coverage html
coverage report
docker-compose down
