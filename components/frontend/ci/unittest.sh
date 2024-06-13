#!/bin/bash

PATH="$PATH:../../ci"
source unittest-base.sh

run npm test
