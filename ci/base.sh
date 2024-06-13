#!/bin/bash

# Code to be used in **/ci/*.sh scripts

set -e

run() {
    # Show the invoked command using a subdued text color so it is clear which tool is running.
    header='\033[95m'
    endstyle='\033[0m'
    echo -e "${header}$*${endstyle}"
    eval "$*"
}

script_dir() {
    # Get the dir of this script so that scripts that are in the same dir as this script can be invoked.
    # See https://stackoverflow.com/questions/39340169/dir-cd-dirname-bash-source0-pwd-how-does-that-work.
    echo $( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
}

# For Windows compatibility; prevent path from ending with a ':'
export PYTHONPATH=$(python -c 'import sys;print(":".join(sys.argv[1:]))' src $PYTHONPATH)
