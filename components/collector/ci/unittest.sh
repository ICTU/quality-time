#!/bin/sh

# We currently get one warning when running Python in dev mode:
# aiohttp/helpers.py:107: DeprecationWarning: "@coroutine" decorator is deprecated since Python 3.8, use "async def" instead
# Turn off dev mode until aiohttp gets fixed or there's a way to suppress warnings in third party code
# export PYTHONDEVMODE=1
export PYTHONPATH=src:$PYTHONPATH
export COVERAGE_RCFILE=../../.coveragerc
coverage run --branch -m unittest --quiet
coverage xml -o build/unittest-coverage.xml
coverage html --directory build/unittest-coverage --show-contexts
coverage report --skip-covered --fail-under=100
