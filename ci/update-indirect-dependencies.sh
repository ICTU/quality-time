#!/bin/bash

set -e

# Update the compiled requirements and package-lock files
(cd components/shared_code; ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/api_server; ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/collector; ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/notifier; ci/pip-compile.sh; ci/pip-install.sh) &
(cd components/frontend; yarn) &
(cd components/renderer; yarn) &
(cd docs; yarn) &
(cd docs; ci/pip-compile.sh; ci/pip-install.sh) &
(cd release; ci/pip-compile.sh; ci/pip-install.sh) &
(cd tests/application_tests; ci/pip-compile.sh; ci/pip-install.sh) &
(cd tests/feature_tests; ci/pip-compile.sh; ci/pip-install.sh) &
wait
