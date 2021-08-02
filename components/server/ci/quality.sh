#!/bin/sh

set -e

mypy src
pylint --rcfile=../../.pylintrc src tests
python -m flake8 --select=DUO src
safety check --bare --ignore 41002 -r requirements.txt -r requirements-dev.txt  # See https://github.com/nedbat/coveragepy/issues/1200
bandit --quiet --recursive src/
vulture --min-confidence 0 src/ tests/ .vulture_ignore_list.py
