#!/bin/bash

source ../ci/base.sh

# Markdownlint
run ./node_modules/markdownlint-cli/markdownlint.js src/*.md

# Ruff
run pipx run `spec ruff` check .
run pipx run `spec ruff` format --check .

# Mypy
# pipx run can't be used because mypy needs the pydantic plugin to be installed in the same venv (using pipx inject)
run pipx install --force `spec mypy`  # --force works around this bug: https://github.com/pypa/pipx/issues/795
run pipx inject mypy `spec pydantic`
run $PIPX_BIN_DIR/mypy src --python-executable=$(which python)

# Vale
run pipx run `spec vale` sync
run pipx run `spec vale` --no-wrap src/*.md

# pip-audit
unset PYTHONDEVMODE  # Suppress ResourceWarnings given by pip-audit in dev mode
run pipx run `spec pip-audit` --strict --progress-spinner=off -r requirements/requirements.txt -r requirements/requirements-dev.txt
export PYTHONDEVMODE=1

# Safety
run pipx run `spec bandit` --quiet --recursive src/

# Vulture
run pipx run `spec vulture` --min-confidence 0 src/ tests/ .vulture_ignore_list.py
