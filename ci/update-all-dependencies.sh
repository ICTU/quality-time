#!/bin/sh

set -e

# Update the compiled requirements and package-lock files
(cd components/shared_data_model; PATH="$(pwd)/venv/bin:$PATH"; ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/shared_server_code; PATH="$(pwd)/venv/bin:$PATH"; ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/shared_server_code; PATH="$(pwd)/venv/bin:$PATH"; ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/external_server; PATH="$(pwd)/venv/bin:$PATH"; ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/collector; PATH="$(pwd)/venv/bin:$PATH"; ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/notifier; PATH="$(pwd)/venv/bin:$PATH"; ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/frontend; rm package-lock.json; npm install) &
(cd components/renderer; rm package-lock.json; npm install) &
(cd docs; PATH="$(pwd)/venv/bin:$PATH"; ci/pip-compile.sh; ci/pip-install.sh) &
(cd release; PATH="$(pwd)/venv/bin:$PATH"; ci/pip-compile.sh; ci/pip-install.sh) &
(cd tests/application_tests; PATH="$(pwd)/venv/bin:$PATH"; ci/pip-compile.sh; ci/pip-install.sh) &
(cd tests/feature_tests; PATH="$(pwd)/venv/bin:$PATH"; ci/pip-compile.sh; ci/pip-install.sh) &
wait
