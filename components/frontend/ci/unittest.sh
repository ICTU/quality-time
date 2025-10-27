#!/bin/bash

PATH="$PATH:../../ci"
source unittest-base.sh

export NODE_OPTIONS="--no-webstorage"  # https://github.com/vitest-dev/vitest/issues/8757
run npm test
