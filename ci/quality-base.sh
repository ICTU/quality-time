#!/bin/bash

source pipx-base.sh

PYTHON_FILES_AND_FOLDERS=$(python $(script_dir)/python_files_and_folders.py)

run_ruff() {
    run_pipx ruff check $PYTHON_FILES_AND_FOLDERS
    run_pipx ruff format --check $PYTHON_FILES_AND_FOLDERS
}

run_fixit() {
    run_pipx fixit lint $PYTHON_FILES_AND_FOLDERS
}

run_mypy() {
    # Run mypy with or without pydantic plugin depending on whether pydantic is listed as dependency in the tools
    # section of the optional dependencies in the pyproject.toml file.
    pydantic_spec=$(spec pydantic)
    if [[ "$pydantic_spec" == "" ]]; then
        run_pipx mypy --python-executable=$(which python) $PYTHON_FILES_AND_FOLDERS
    else
        # To use the pydantic plugin, we need to first install mypy and then inject pydantic
        run pipx install --force $(spec mypy) # --force works around this bug: https://github.com/pypa/pipx/issues/795
        run pipx inject mypy $pydantic_spec
        run $PIPX_BIN_DIR/mypy --python-executable=$(which python) $PYTHON_FILES_AND_FOLDERS
    fi
}

run_pyproject_fmt() {
    run_pipx pyproject-fmt --check pyproject.toml
}

run_bandit() {
    run_pipx bandit --configfile pyproject.toml --quiet --recursive $PYTHON_FILES_AND_FOLDERS
}

run_pip_audit() {
    run_pipx pip-audit --strict --progress-spinner=off $(python $(script_dir)/requirements_files.py "-r %s")
}

run_vulture() {
    run_pipx vulture --min-confidence 0 $PYTHON_FILES_AND_FOLDERS .vulture_ignore_list.py $@
}

run_vale() {
    run_pipx vale sync
    run_pipx vale --no-wrap --glob "*.md" src
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
