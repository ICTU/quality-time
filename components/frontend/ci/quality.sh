#!/bin/bash

PATH="$PATH:../../ci"
source quality-base.sh

# Eslint
run npx eslint *.js *.mjs src
