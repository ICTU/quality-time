#!/bin/bash

# Start the API-server under coverage and run the feature tests.

# We collect both the coverage of the API-server and of the tests themselves
# so we can discover dead code in the tests.

set -e

mkdir -p build
export COLUMNS=${COLUMNS:-120}  # Prevent Docker Compose warning about unset COLUMNS variable
export COVERAGE_RCFILE="$(pwd)"/tests/feature_tests/.coveragerc
export PROXY_PORT=8080
export DOCKER_CLI_HINTS=false  # Suppress Docker Desktop "What's next" promotional output

cleanup() {
  docker compose logs > build/containers.log 2>&1 || true
  docker compose down || true
}
trap cleanup EXIT
docker compose --progress quiet build database api_server renderer frontend www
docker compose up --detach database ldap
just_spec=$(uv export --project tools/third_party --only-group just --quiet --no-hashes --no-header)
cd components/api_server || exit
uvx --from=rust-just --with-requirements <(echo $just_spec) just install-py-dependencies
.venv/bin/coverage erase
RENDERER_HOST=localhost .venv/bin/python tests/quality_time_api_server_under_coverage.py &> ../../build/quality_time_api_server.log &
api_server_pid=$!
for _ in $(seq 60); do
  curl --fail --silent --output /dev/null "http://localhost:${API_SERVER_PORT:-5001}/api/internal/health" && break
  sleep 0.5
done
cd ../..
# We need to start a second API-server for the renderer. We start it after the API-server under coverage so
# we can measure the coverage of the startup code, including the containers that depend on the API-server.
docker compose up --detach api_server renderer frontend www
cd tests/feature_tests
uvx --from=rust-just --with-requirements <(echo $just_spec) just install-py-dependencies
cd ../..
for _ in $(seq 60); do
  curl --fail --silent --output /dev/null "http://localhost:${PROXY_PORT:-8080}/" && break
  sleep 0.5
done
tests/feature_tests/.venv/bin/coverage erase
result=0
tests/feature_tests/.venv/bin/coverage run -m behave --format pretty "${1:-tests/feature_tests/src/features}" || result=$?
# Bottle's reloader (reloader=True in quality_time_server.serve) runs the server
# in a child process; the parent (captured in $api_server_pid) is just a monitor.
# Signal the child so its signal handler saves the API-server's coverage data,
# then wait for the parent to exit, which happens once the child is gone.
# pgrep short flags (-n newest, -f match full command line) are used because
# macOS pgrep doesn't support the GNU long-form equivalents.
kill -s TERM "$(pgrep -n -f tests/quality_time_api_server_under_coverage.py)" || true
wait "$api_server_pid" 2>/dev/null || true
if [[ "$result" -eq "0" ]]
then
  tests/feature_tests/.venv/bin/coverage combine . components/api_server
  tests/feature_tests/.venv/bin/coverage xml
  tests/feature_tests/.venv/bin/coverage html
  tests/feature_tests/.venv/bin/coverage report
fi
exit $result
