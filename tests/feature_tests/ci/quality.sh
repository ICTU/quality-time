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
run pipx run `spec safety` check --bare -r requirements/requirements-dev.txt

# Bandit
run pipx run `spec bandit` --quiet --recursive src/

# Vulture
run pipx run `spec vulture` --min-confidence 0 src/ .vulture_ignore_list.py
