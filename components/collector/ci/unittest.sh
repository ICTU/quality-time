#!/bin/sh

coverage run --omit=venv/*,/home/travis/virtualenv/* --branch -m unittest --quiet
coverage xml -o build/unittest-coverage.xml
coverage html --directory build/unittest-coverage
coverage report --fail-under=100 --skip-covered
