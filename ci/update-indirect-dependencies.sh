#!/bin/bash

set -e

run_npm_install() {
    cd $1
    npm install --fund=false --ignore-scripts
}

run_uv_sync() {
    uv sync --upgrade --quiet --no-progress --directory $1
}

# Update the lock files
run_uv_sync components/shared_code &
run_uv_sync components/api_server &
run_uv_sync components/collector &
run_uv_sync components/notifier &
run_npm_install components/frontend &
run_npm_install components/renderer &
run_npm_install docs &
run_uv_sync docs &
run_uv_sync release &
run_uv_sync tests/application_tests &
run_uv_sync tests/feature_tests &
wait
