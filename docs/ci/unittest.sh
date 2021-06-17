#!/bin/sh

# We currently get one warning when running Python in dev mode:
# aiohttp/helpers.py:107: DeprecationWarning: "@coroutine" decorator is deprecated since Python 3.8, use "async def" instead
# Turn off dev mode until aiohttp gets fixed or there's a way to suppress warnings in third party code
# export PYTHONDEVMODE=1

# For Windows compatibility; prevent path from ending with a ':'
export PYTHONPATH=`python -c 'import sys;print(":".join(sys.argv[1:]))' src $PYTHONPATH`
export COVERAGE_RCFILE=../.coveragerc
coverage run -m unittest --quiet
coverage xml
coverage html
coverage report
