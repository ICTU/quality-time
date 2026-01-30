set positional-arguments := true
set quiet := true

_default:
    @just --list

# Install dependencies from the lock file.
[no-cd]
[private]
[script("bash")]
install-dependencies:
    set -euo pipefail
    if [[ -f pyproject.toml ]] then
        uv sync --locked --all-extras --quiet
    fi
    if [[ -f package.json ]] then
        npm install --ignore-scripts --silent
    fi

# Build the code.
[no-cd]
[private]
build: install-dependencies
    npm run --ignore-scripts build --if-present

export COVERAGE_RCFILE := justfile_directory() + "/.coveragerc"

# Run the Python unit tests.
[no-cd]
[no-quiet]
[private]
py-unit-test $PYTHONDEVMODE="1" $PYTHONPATH="src:$PYTHONPATH": install-dependencies
    uv run coverage run -m unittest --quiet
    uv run coverage report --fail-under=0
    uv run coverage html --fail-under=0
    uv run coverage xml  # Fail if coverage is too low, but only after the text and HTML reports have been generated

# Run the JavaScript unit tests.
[no-cd]
[no-quiet]
[private]
js-unit-test: install-dependencies
    # See https://github.com/vitest-dev/vitest/issues/8757 for why --no-webstorage is needed
    npm run test --if-present

# Run the unit tests.
[no-cd]
[script("bash")]
test:
    set -euo pipefail
    if [[ -f pyproject.toml && -d "tests" ]] then
        just py-unit-test
    fi
    if [[ -f package.json ]] then
        just js-unit-test
    fi

# Check the Python code for formatting and quality issues. Pass 'fix' to also fix issues.
[no-cd]
[private]
[script("bash")]
check-py *fix: install-dependencies
    set -euxo pipefail
    if [[ -f pyproject.toml ]] then
        code_folders=`uv run python -c "import os;print(' '.join(d for d in ('src', 'tests') if os.path.isdir(d)) or '*.py')"`
        uv run ruff format {{ if fix == "fix" { "" } else { "--check " } }} $code_folders
        uv run ruff check {{ if fix == "fix" { "--fix " } else { "" } }} $code_folders
        uv run mypy $code_folders
        uv run fixit {{ if fix == "fix" { "fix" } else { "lint" } }} $code_folders
        uv run pyproject-fmt {{ if fix == "fix" { "" } else { "--check " } }}pyproject.toml
        uv run troml {{ if fix == "fix" { "suggest --fix" } else { "check" } }}
        uv run pip-audit --requirement <(uv export --format requirements-txt --no-emit-package shared-code) --disable-pip
        uv run bandit --configfile pyproject.toml --quiet --recursive $code_folders
        uv run vulture --exclude .venv $code_folders .vulture-whitelist.py
    fi

# Check the JavaScript code for formatting and quality issues. Pass 'fix' to also fix issues.
[no-cd]
[private]
[script("bash")]
check-js: install-dependencies
    set -euxo pipefail
    if [[ -f package.json ]] then
        npm run lint --if-present
    fi

# Check the Markdown files for formatting and quality issues.
[no-cd]
[private]
[script("bash")]
check-md: install-dependencies
    set -euxo pipefail
    if [[ -f "node_modules/markdownlint-cli/markdownlint.js" ]] then
        ./node_modules/markdownlint-cli/markdownlint.js src/**/*.md
    fi
    if [[ `uv pip list | grep vale` ]] then
        uv run vale sync
        uv run vale --no-wrap --glob "*.md" src
    fi

# Check the YAML files for formatting and quality issues.
[no-cd]
[private]
[script("bash")]
check-yml: install-dependencies
    set -euxo pipefail
    if [[ `uv pip list | grep yamllint` ]] then
        uv run yamllint ../publiccode.yml
    fi

# Start the component(s)
[no-cd]
[script("bash")]
start *components: install-dependencies
    if [[ -f pyproject.toml ]] then
        uv run python src/quality_time*.py
    elif [[ -f package.json ]] then
        npm run start --if-present
    elif [[ -d docker ]] then
        docker compose up {{ components }}
    fi

# Run all code quality checks. Pass 'fix' to also fix issues.
check *fix: (check-py fix) check-js check-md check-yml

# Run all tests and checks. Pass 'fix' to also fix issues.
all *fix: test (check fix)
