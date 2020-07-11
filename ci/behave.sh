#!/bin/sh

# Start the server under coverage and run the feature tests.
# This script assumes the database and LDAP containers are running.

# We collect both the coverage of the server and of the tests themselves
# so we can discover dead code in the tests.

trap "kill 0" EXIT  # Kill server on Ctrl-C
coverage erase
cd components/server
. venv/bin/activate
coverage run --rcfile=../../.coveragerc-behave --branch --parallel-mode --concurrency=gevent src/quality_time_server.py > /dev/null 2>&1 &
deactivate
cd ../..
sleep 5  # Give server time to start up
coverage run --rcfile=.coveragerc-behave --branch --parallel-mode -m behave tests/features  # --format null
kill -s TERM `pgrep -n -f quality_time_server.py`  # Stop the server so the coverage is written
mv components/server/.coverage.* .
coverage combine
coverage html --rcfile=.coveragerc-behave --directory build/features-coverage
coverage report --rcfile=.coveragerc-behave --fail-under=100 --skip-covered
