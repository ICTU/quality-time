#!/bin/sh

# Start the server under coverage and run the feature tests.
# This script assumes the database and LDAP containers are running.

# We collect both the coverage of the server and of the tests themselves
# so we can discover dead code in the tests.

trap "kill 0" EXIT  # Kill server on Ctrl-C
coverage erase
cd components/server || exit
coverage erase
. venv/bin/activate
export LOAD_EXAMPLE_REPORTS=False
export COVERAGE_PROCESS_START="../../.coveragerc-behave"
python src/quality_time_server_under_coverage.py > /tmp/quality_time_server.log 2>&1 &
deactivate
cd ../..
sleep 5  # Give server time to start up
coverage run --rcfile=.coveragerc-behave -m behave tests/features  # --format null
kill -s TERM "$(pgrep -n -f src/quality_time_server_under_coverage.py)"
sleep 2  # Give the server time to write the coverage data
coverage combine --rcfile=.coveragerc-behave . components/server
coverage html --rcfile=.coveragerc-behave --directory build/features-coverage
coverage report --rcfile=.coveragerc-behave --fail-under=100 --skip-covered
