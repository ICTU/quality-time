#!/bin/bash

source ../../ci/base.sh

# Ruff
run pipx run `spec ruff` .

# Mypy
run pipx run `spec mypy` --python-executable=$(which python) src

# pip-audit
unset PYTHONDEVMODE  # Suppress ResourceWarnings given by pip-audit in dev mode
run pipx run `spec pip-audit` --strict --progress-spinner=off -r requirements/requirements.txt -r requirements/requirements-dev.txt
export PYTHONDEVMODE=1

# Safety
run pipx run `spec safety` check --bare -r requirements/requirements.txt -r requirements/requirements-dev.txt

# Bandit
run pipx run `spec bandit` --quiet --recursive src/

# Vulture
run pipx run `spec vulture` --min-confidence 0 src/ tests/ .vulture_ignore_list.py

# Black
run pipx run `spec black` --check src tests
