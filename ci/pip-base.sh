#!/bin/bash

source base.sh

# Insert a custom compile command in generated requirements file so it is clear how they are generated:
export UV_CUSTOM_COMPILE_COMMAND="ci/pip-compile.sh"

run_pip_compile() {
    for requirements_file in $(.venv/bin/python $(script_dir)/requirements_files.py); do
        extra=$([[ "$requirements_file" == *"-dev"* ]] && echo "--extra dev" || echo "")
        run uv pip compile --quiet --generate-hashes $extra --output-file $requirements_file pyproject.toml
    done
}

run_pip_install() {
    run uv pip install --quiet $@
}
