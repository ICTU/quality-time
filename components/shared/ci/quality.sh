#!/bin/sh

mypy shared
pylint shared
safety check --bare -r requirements.txt -r requirements-dev.txt
bandit --quiet --recursive shared/

