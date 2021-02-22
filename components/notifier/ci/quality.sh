#!/bin/sh

set -e

mypy src
pylint src tests
isort **/*.py --check-only
python -m flake8 --select=DUO src
safety check --bare -r requirements.txt -r requirements-dev.txt
bandit --quiet --recursive src/
vulture --min-confidence 0 src/ tests/ .vulture_ignore_list.py
