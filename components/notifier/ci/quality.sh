#!/bin/sh

set -e

mypy src
# Turn off Pylint until it works with Python 3.9. In the mean time we run a separate GitHub Action for Pylint with
# Python 3.8, see .github/workflows/pylint.yml
# pylint src tests
isort **/*.py --check-only
safety check --bare -r requirements.txt -r requirements-dev.txt
bandit --quiet --recursive src/
vulture --min-confidence 0 src/ tests/ .vulture_ignore_list.py
