#!/bin/bash

set -e

# Update the compiled requirements and package-lock files
# Remove node_modules in the frontend component as a work-around for this npm bug: https://github.com/npm/cli/issues/4828
(cd components/shared_code; ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/api_server; ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/collector; ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/notifier;  ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/frontend; rm -f package-lock.json; rm -rf node_modules; npm install --ignore-scripts) &
(cd components/renderer; rm -f package-lock.json; npm install --ignore-scripts) &
(cd docs; rm -f package-lock.json; npm install --ignore-scripts) &
(cd docs; ci/pip-compile.sh; ci/pip-install.sh) &
(cd release; ci/pip-compile.sh; ci/pip-install.sh) &
(cd tests/application_tests; ci/pip-compile.sh; ci/pip-install.sh) &
(cd tests/feature_tests; ci/pip-compile.sh; ci/pip-install.sh) &
wait
