#!/bin/sh

set -e

# We currently get one warning when running Python in dev mode:
# astroid/node_classes.py:90: DeprecationWarning: The 'astroid.node_classes' module is deprecated and will be replaced
# by 'astroid.nodes' in astroid 3.0.0
# Turn off dev mode until astroid gets fixed or there's a way to suppress warnings in third party code
#export PYTHONDEVMODE=1

./node_modules/markdownlint-cli/markdownlint.js src/*.md
mypy src
pylint --rcfile=../.pylintrc src tests
python -m flake8 --select=DUO src
isort **/*.py --check-only
safety check --bare --ignore 41002 -r requirements-dev.txt  # See https://github.com/nedbat/coveragepy/issues/1200
NAMES_TO_IGNORE=''
vulture --min-confidence 0 --ignore-names $NAMES_TO_IGNORE src/ tests/ .vulture_ignore_list.py
