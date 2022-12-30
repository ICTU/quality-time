#!/bin/sh

set -e

export PYTHONDEVMODE=1

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

run mypy steps
run pylint --rcfile=../../.pylintrc steps
run python -m flake8 --select=DUO steps  # Dlint
unset PYTHONDEVMODE  # Suppress ResourceWarnings given by pip-audit in dev mode
run pip-audit --strict --progress-spinner=off -r requirements/requirements-base.txt -r requirements/requirements-dev.txt
export PYTHONDEVMODE=1
run safety check --bare -r requirements/requirements-base.txt -r requirements/requirements-dev.txt
run bandit --quiet --recursive steps
NAMES_TO_IGNORE=''
run vulture --min-confidence 0 --ignore-names $NAMES_TO_IGNORE steps/ .vulture_ignore_list.py

