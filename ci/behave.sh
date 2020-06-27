#!/bin/sh

coverage run --branch -m behave tests/features  #--format null tests/features
coverage xml -o build/features-coverage.xml
coverage html --directory build/features-coverage
coverage report --fail-under=100 --skip-covered

