#!/bin/bash

source uvx-base.sh

python_files_and_folders() {
    echo $(.venv/bin/python $(script_dir)/python_files_and_folders.py)
}

run_ruff() {
    PYTHON_FILES_AND_FOLDERS=$(python_files_and_folders)
    run_uvx ruff check $PYTHON_FILES_AND_FOLDERS
    run_uvx ruff format --check $PYTHON_FILES_AND_FOLDERS
}

run_fixit() {
    run_uvx fixit lint $(python_files_and_folders)
}

run_mypy() {
    PYTHON_FILES_AND_FOLDERS=$(python_files_and_folders)
    # Run mypy with or without pydantic plugin depending on whether pydantic is listed as dependency in the tools
    # section of the optional dependencies in the pyproject.toml file.
    pydantic_spec=$(spec pydantic ==)
    if [[ "$pydantic_spec" == "" ]]; then
        run_uvx mypy --python-executable=.venv/bin/python $PYTHON_FILES_AND_FOLDERS
    else
        run uvx --with $pydantic_spec $(spec mypy @) --python-executable=.venv/bin/python $PYTHON_FILES_AND_FOLDERS
    fi
}

run_pyproject_fmt() {
    run_uvx pyproject-fmt --check pyproject.toml
}

run_bandit() {
    run_uvx bandit --configfile pyproject.toml --quiet --recursive $(python_files_and_folders)
}

run_pip_audit() {
    for requirements_file in $(python $(script_dir)/requirements_files.py); do
        run_uvx pip-audit --disable-pip --progress-spinner=off --requirement $requirements_file
    done
}

run_vulture() {
    run_uvx vulture --min-confidence 0 $(python_files_and_folders) .vulture_ignore_list.py $@
}

run_vale() {
    run_uvx vale sync
    run_uvx vale --no-wrap --glob "*.md" src
}

run_markdownlint() {
    run ./node_modules/markdownlint-cli/markdownlint.js src/**/*.md
}

check_python_quality() {
    run_ruff
    run_fixit
    run_mypy
    run_pyproject_fmt
    run_pip_audit
    run_bandit
    run_vulture
}
