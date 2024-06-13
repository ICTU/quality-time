#!/bin/bash

source base.sh

spec() {
    # The versions of tools are specified in pyproject.toml. This function calls the spec.py script which in turn
    # reads the version numbers from the pyproject.toml file. The function takes one argument: the package to return
    # the spec for.
    python $(script_dir)/spec.py $1
}

run_pipx() {
    # Look up the version of the command using the spec function and run the command using pipx.
    command_spec=$(spec $1)
    shift 1
    run pipx run $command_spec $@
}

# Don't install tools in the global pipx home folder, but locally for each component:
export PIPX_HOME=.pipx
export PIPX_BIN_DIR=$PIPX_HOME/bin
