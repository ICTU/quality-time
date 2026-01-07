#!/bin/bash

PATH="$PATH:../ci"
source quality-base.sh

check_python_quality
run_markdownlint
run_yamllint ../publiccode.yml
run_vale
