#!/bin/bash

# Code to be used in **/ci/*.sh scripts

set -e

run () {
    # Show the invoked command using a subdued text color so it's clear which tool is running.
    header='\033[95m'
    endstyle='\033[0m'
    echo -e "${header}$*${endstyle}"
    eval "$*"
}

spec () {
    # The versions of tools are specified in pyproject.toml. This function calls the spec.py script which in turn
    # reads the version numbers from the pyproject.toml file.

    # Get the dir of this script so the spec.py script that is in the same dir as this script can be invoked:
    SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
    python $SCRIPT_DIR/spec.py $*
}

# Turn on development mode, see https://docs.python.org/3/library/devmode.html
export PYTHONDEVMODE=1
# Don't install tools in the global pipx home folder, but locally for each component:
export PIPX_HOME=.pipx
export PIPX_BIN_DIR=$PIPX_HOME/bin

# For Windows compatibility; prevent path from ending with a ':'
export PYTHONPATH=`python -c 'import sys;print(":".join(sys.argv[1:]))' src $PYTHONPATH`
