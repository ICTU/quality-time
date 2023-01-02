#!/bin/sh

set -e

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

# Update the compiled requirements files
(run cd components/shared_data_model; PATH="$(pwd)/venv/bin:$PATH"; run ci/pip-compile.sh)
(run cd components/shared_server_code; PATH="$(pwd)/venv/bin:$PATH"; run ci/pip-compile.sh)
(run cd components/shared_server_code; PATH="$(pwd)/venv/bin:$PATH"; run ci/pip-compile.sh)
(run cd components/external_server; PATH="$(pwd)/venv/bin:$PATH"; run ci/pip-compile.sh)
(run cd components/internal_server; PATH="$(pwd)/venv/bin:$PATH"; run ci/pip-compile.sh)
(run cd components/collector; PATH="$(pwd)/venv/bin:$PATH"; run ci/pip-compile.sh)
(run cd components/notifier; PATH="$(pwd)/venv/bin:$PATH"; run ci/pip-compile.sh)
(run cd docs; PATH="$(pwd)/venv/bin:$PATH"; run ci/pip-compile.sh)
(run cd release; PATH="$(pwd)/venv/bin:$PATH"; run ci/pip-compile.sh)
(run cd tests/application_tests; PATH="$(pwd)/venv/bin:$PATH"; run ci/pip-compile.sh)
(run cd tests/feature_tests; PATH="$(pwd)/venv/bin:$PATH"; run ci/pip-compile.sh)
