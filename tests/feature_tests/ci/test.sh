#!/bin/bash

# Start the server under coverage and run the feature tests.
# This script assumes the database and LDAP containers are running.

# We collect both the coverage of the server and of the tests themselves
# so we can discover dead code in the tests.

mkdir -p build
export COVERAGE_RCFILE="$(pwd)"/tests/feature_tests/.coveragerc
docker compose up --quiet-pull -d database ldap
cd components/server || exit
python3 -m venv venv
. venv/bin/activate
pip --quiet install --progress-bar off -r requirements.txt -r requirements-dev.txt
coverage erase
RENDERER_HOST=localhost python tests/quality_time_server_under_coverage.py &> ../../build/quality_time_server.log &
deactivate
cd ../..
# We need to start a second server for the renderer. We start it after the server under
# coverage so we can measure the coverage of the startup code, including the containers
# that depend on server.
docker compose up --quiet-pull -d server renderer frontend www
cd tests/feature_tests
python3 -m venv venv
. venv/bin/activate
pip --quiet install --progress-bar off -r requirements-dev.txt
cd ../..
sleep 10  # Give server time to start up
coverage erase
coverage run -m behave --format progress "${1:-tests/feature_tests/features}"
result=$?
kill -s TERM "$(pgrep -n -f tests/quality_time_server_under_coverage.py)"
sleep 2  # Give server time to write coverage data
if [[ "$result" -eq "0" ]]
then
  coverage combine . components/server
  coverage xml
  coverage html
  coverage report
  result=$?
fi
docker compose down
exit $result
