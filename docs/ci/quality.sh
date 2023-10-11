#!/bin/bash

source ../ci/base.sh

# Markdownlint
run ./node_modules/markdownlint-cli/markdownlint.js src/*.md

# Ruff
run pipx run `spec ruff` .

# Mypy
# pipx run can't be used because mypy needs the pydantic plugin to be installed in the same venv (using pipx inject)
run pipx install --force `spec mypy`  # --force works around this bug: https://github.com/pypa/pipx/issues/795
run pipx inject mypy `spec pydantic`
run $PIPX_BIN_DIR/mypy src --python-executable=$(which python)

# The vale Docker image doesn't support the linux/arm64/v8 architecture, so use a locally installed vale if possible
if ! vale -v &> /dev/null
then
    run docker run --rm -v $(pwd)/styles:/styles -v $(pwd):/docs -w /docs jdkato/vale sync
    run docker run --rm -v $(pwd)/styles:/styles -v $(pwd):/docs -w /docs jdkato/vale --no-wrap src/*.md
else
    run vale sync
    run vale --no-wrap src/*.md
fi

# pip-audit
unset PYTHONDEVMODE  # Suppress ResourceWarnings given by pip-audit in dev mode
run pipx run `spec pip-audit` --strict --progress-spinner=off -r requirements/requirements.txt -r requirements/requirements-dev.txt
export PYTHONDEVMODE=1

# Safety
run pipx run `spec bandit` --quiet --recursive src/

# Vulture
run pipx run `spec vulture` --min-confidence 0 src/ tests/ .vulture_ignore_list.py

# Black
run pipx run `spec black` --check src tests
