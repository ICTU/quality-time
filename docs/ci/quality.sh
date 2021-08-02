#!/bin/sh

set -e

./node_modules/markdownlint-cli/markdownlint.js *.md
mypy src
pylint --rcfile=../.pylintrc src tests
python -m flake8 --select=DUO src
isort **/*.py --check-only
safety check --bare --ignore 41002 -r requirements-dev.txt  # See https://github.com/nedbat/coveragepy/issues/1200
NAMES_TO_IGNORE=''
vulture --min-confidence 0 --ignore-names $NAMES_TO_IGNORE src/ tests/ .vulture_ignore_list.py
