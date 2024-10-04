#!/bin/bash

# Code to be used in **/ci/*.sh scripts

set -e

spec() {
    # The versions of tools are specified in pyproject.toml. This function calls the spec.py script which in turn
    # reads the version numbers from the pyproject.toml file. The function takes two arguments: the package to return
    # the spec for and the seperator to use between package name and version number.
    .venv/bin/python $(script_dir)/spec.py $1 $2
}

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
if command -v python &> /dev/null
then
    export PYTHONPATH=$(python -c 'import sys;print(":".join(sys.argv[1:]))' src $PYTHONPATH)
fi
