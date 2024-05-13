#!/bin/bash

source ../../ci/base.sh

# Ruff
run pipx run `spec ruff` check .
run pipx run `spec ruff` format --check .

# Mypy
run pipx run `spec mypy` --python-executable=$(which python) src

# pip-audit
unset PYTHONDEVMODE  # Suppress ResourceWarnings given by pip-audit in dev mode
run pipx run `spec pip-audit` --strict --progress-spinner=off -r requirements/requirements-dev.txt
export PYTHONDEVMODE=1

# Safety
# Vulnerability ID: 67599
# ADVISORY: ** DISPUTED ** An issue was discovered in pip (all versions) because it installs the version with the
# highest version number, even if the user had intended to obtain a private package from a private index. This only
# affects use of the --extra-index-url option, and exploitation requires that the...
# CVE-2018-20225
# For more information about this vulnerability, visit https://data.safetycli.com/v/67599/97c
run pipx run `spec safety` check --bare --ignore 67599 -r requirements/requirements-dev.txt

# Bandit
run pipx run `spec bandit` --quiet --recursive src/

# Vulture
run pipx run `spec vulture` --min-confidence 0 src/ .vulture_ignore_list.py
