#!/bin/sh

set -e

export PYTHONDEVMODE=1

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

run mypy src
run pylint --rcfile=../../.pylintrc src tests
run python -m flake8 --select=DUO src  # Dlint
unset PYTHONDEVMODE  # Suppress ResourceWarnings given by pip-audit in dev mode
run pip-audit --strict --progress-spinner=off -r requirements/requirements-dev.txt
export PYTHONDEVMODE=1
run safety check --bare -r requirements/requirements-dev.txt
run bandit --quiet --recursive src/
run vulture --min-confidence 0 src/ tests/ .vulture_ignore_list.py
