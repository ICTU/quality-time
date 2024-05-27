#!/bin/bash

# Get the dir of this script so the vbase.sh script that is in the same dir as this script can be sourced:
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source $SCRIPT_DIR/base.sh

# Turn on development mode, see https://docs.python.org/3/library/devmode.html
export PYTHONDEVMODE=1
