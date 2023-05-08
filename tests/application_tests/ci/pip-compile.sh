#!/bin/sh

set -e

run () {
    header='\033[95m'
    endstyle='\033[0m'
    echo "${header}$*${endstyle}"
    eval "$*"
}

# Update the compiled requirements files
# Use --strip-extras to prevent:
# ERROR: In --require-hashes mode, all requirements must have their versions pinned with ==. These do not:
#    urllib3<3,>=1.21.1 from https://files.pythonhosted.org/packages/4b/1d/f8383ef593114755429c307449e7717b87044b3bcd5f7860b89b1f759e34/urllib3-2.0.2-py3-none-any.whl (from requests==2.30.0->-r requirements/requirements.txt (line 123))
run pip-compile --strip-extras --allow-unsafe --generate-hashes --quiet --resolver=backtracking --output-file requirements/requirements.txt pyproject.toml
run pip-compile --strip-extras --allow-unsafe --generate-hashes --quiet --resolver=backtracking --extra dev --output-file requirements/requirements-dev.txt pyproject.toml
