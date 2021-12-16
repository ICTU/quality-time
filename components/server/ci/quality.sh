#!/bin/sh

set -e

# We currently get one warning when running Python in dev mode:
# astroid/node_classes.py:90: DeprecationWarning: The 'astroid.node_classes' module is deprecated and will be replaced
# by 'astroid.nodes' in astroid 3.0.0
# Turn off dev mode until astroid gets fixed or there's a way to suppress warnings in third party code
#export PYTHONDEVMODE=1
HEADER='\033[95m'
ENDSTYLE='\033[0m'

echo "${HEADER}mypy${ENDSTYLE}"
mypy src
echo "${HEADER}pylint${ENDSTYLE}"
pylint --rcfile=../../.pylintrc src tests
echo "${HEADER}flake8${ENDSTYLE}"
python -m flake8 --select=DUO src
echo "${HEADER}pip-audit${ENDSTYLE}"
pip-audit --strict --progress-spinner=off
echo "${HEADER}safety${ENDSTYLE}"
safety check --bare --ignore 41002 -r requirements.txt -r requirements-dev.txt  # See https://github.com/nedbat/coveragepy/issues/1200
echo "${HEADER}bandit${ENDSTYLE}"
bandit --quiet --recursive src/
echo "${HEADER}vulture${ENDSTYLE}"
vulture --min-confidence 0 src/ tests/ .vulture_ignore_list.py
