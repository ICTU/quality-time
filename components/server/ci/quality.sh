#!/bin/sh

set -e

mypy src
pylint src tests
safety check --bare -r requirements.txt -r requirements-dev.txt
bandit --quiet --recursive src/
vulture --min-confidence 0 src/ tests/ .vulture_white_list.py
