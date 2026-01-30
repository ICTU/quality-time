#!/bin/bash

# Start the API-server under coverage and run the feature tests.

# We collect both the coverage of the API-server and of the tests themselves
# so we can discover dead code in the tests.

mkdir -p build
export COVERAGE_RCFILE="$(pwd)"/tests/feature_tests/.coveragerc
export PROXY_PORT=8080
docker compose build --progress quiet database api_server renderer frontend www
docker compose up --detach database ldap
cd components/api_server || exit
uvx --from rust-just==1.46.0 just install-py-dependencies
.venv/bin/coverage erase
RENDERER_HOST=localhost .venv/bin/python tests/quality_time_api_server_under_coverage.py &> ../../build/quality_time_api_server.log &
sleep 5  # Give server time to start up
cd ../..
# We need to start a second API-server for the renderer. We start it after the API-server under coverage so
# we can measure the coverage of the startup code, including the containers that depend on the API-server.
docker compose up --detach api_server renderer frontend www
cd tests/feature_tests
uvx --from rust-just==1.46.0 just install-py-dependencies
cd ../..
sleep 5  # Give components time to start up
tests/feature_tests/.venv/bin/coverage erase
tests/feature_tests/.venv/bin/coverage run -m behave --format pretty "${1:-tests/feature_tests/src/features}"
result=$?
kill -s TERM "$(pgrep -n -f tests/quality_time_api_server_under_coverage.py)"
sleep 5  # Give server time to write coverage data
if [[ "$result" -eq "0" ]]
then
  tests/feature_tests/.venv/bin/coverage combine . components/api_server
  tests/feature_tests/.venv/bin/coverage xml
  tests/feature_tests/.venv/bin/coverage html
  tests/feature_tests/.venv/bin/coverage report
  result=$?
fi
docker compose logs > build/containers.log
docker compose down
exit $result
