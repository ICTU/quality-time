#!/bin/sh

# Start the server under coverage and run the feature tests.
# This script assumes the database and LDAP containers are running.

# We collect both the coverage of the server and of the tests themselves
# so we can discover dead code in the tests.

trap "kill 0" EXIT  # Kill server on Ctrl-C
export COVERAGE_RCFILE="$(pwd)"/.coveragerc-behave
cd components/server || exit
python3 -m venv venv
. venv/bin/activate
pip --quiet install --progress-bar off -r requirements.txt
coverage erase
export LOAD_EXAMPLE_REPORTS=False
export COVERAGE_PROCESS_START=$COVERAGE_RCFILE
python tests/quality_time_server_under_coverage.py > /tmp/quality_time_server.log 2>&1 &
deactivate
cd ../..
python3 -m venv venv
. venv/bin/activate
pip --quiet install --progress-bar off -r requirements-dev.txt
coverage erase
sleep 3  # Give server time to start up
coverage run -m behave tests/features  # --format null
kill -s TERM "$(pgrep -n -f tests/quality_time_server_under_coverage.py)"
sleep 2  # Give the server time to write the coverage data
coverage combine . components/server
coverage html --directory build/features-coverage
coverage report --fail-under=62 --skip-covered
