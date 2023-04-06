#!/bin/sh

set -e

export PYTHONDEVMODE=1

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

run ./node_modules/markdownlint-cli/markdownlint.js src/*.md
run mypy src
# The vale Docker image doesn't support the linux/arm64/v8 architecture, so a locally installed vale if possible
if ! vale -v &> /dev/null
then
    run docker run --rm -v $(pwd)/styles:/styles -v $(pwd):/docs -w /docs jdkato/vale sync
    run docker run --rm -v $(pwd)/styles:/styles -v $(pwd):/docs -w /docs jdkato/vale --no-wrap src/*.md
else
    run vale sync
    run vale --no-wrap src/*.md
fi
run pylint --rcfile=../.pylintrc src tests
run python -m flake8 --select=DUO src  # Dlint
run isort **/*.py --check-only
unset PYTHONDEVMODE  # Suppress ResourceWarnings given by pip-audit in dev mode
run pip-audit --strict --progress-spinner=off -r requirements/requirements-dev.txt
export PYTHONDEVMODE=1
run safety check --bare -r requirements/requirements.txt -r requirements/requirements-dev.txt
NAMES_TO_IGNORE=''
run vulture --min-confidence 0 --ignore-names $NAMES_TO_IGNORE src/ tests/ .vulture_ignore_list.py
