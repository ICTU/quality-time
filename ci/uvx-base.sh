#!/bin/bash

source base.sh

run_uvx() {
    # Look up the version of the command using the spec function and run the command using uvx.
    command_spec=$(spec $1 @)
    shift 1
    run uvx $command_spec $@
}
