#!/bin/bash

PATH="$PATH:../../ci"
source unittest-base.sh

run yarn run test
