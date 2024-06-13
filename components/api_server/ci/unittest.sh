#!/bin/bash

PATH="$PATH:../../ci"
source unittest-base.sh

export COVERAGE_RCFILE=../../.coveragerc
run_coverage
