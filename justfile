set positional-arguments := true
set quiet := true

_default:
    @just --list

alias help := _default

export COVERAGE_RCFILE := justfile_directory() + "/.coveragerc"
uv_update_script := justfile_directory() + "/tools/uv_update.py"
docker_folder_exists := path_exists(invocation_directory() + '/docker')
src_folder_exists := path_exists(invocation_directory() + '/src')
tests_folder_exists := path_exists(invocation_directory() + '/tests')
package_json_exists := path_exists(invocation_directory() + '/package.json')
pyproject_toml := invocation_directory() + "/pyproject.toml"
pyproject_toml_exists := path_exists(pyproject_toml)
pyproject_toml_contents := if pyproject_toml_exists == "true" { read(pyproject_toml) } else { "" }
js_scripts := if package_json_exists == "true" { shell(f"npm --prefix={{invocation_directory()}} pkg get scripts") } else { "{}" }
has_js_build_script := if js_scripts =~ '"build"' { "true" } else { "false" }
has_js_start_script := if js_scripts =~ '"start"' { "true" } else { "false" }
has_js_test_script := if js_scripts =~ '"test"' { "true" } else { "false" }
has_js_fix_script := if js_scripts =~ '"fix"' { "true" } else { "false" }
has_py_unit_tests := if pyproject_toml_exists == "true" { tests_folder_exists } else { "false" }
has_sphinx := if pyproject_toml_contents =~ '"sphinx[<=]=[A-Za-z0-9_.\-]+"' { "true" } else { "false" }
has_yamllint := if pyproject_toml_contents =~ '"yamllint[<=]=[A-Za-z0-9_.\-]+"' { "true" } else { "false" }
has_vale := if pyproject_toml_contents =~ '"vale[<=]=[A-Za-z0-9_.\-]+"' { "true" } else { "false" }
src_folder := if src_folder_exists == "true" { "src" } else { "" }
tests_folder := if tests_folder_exists == "true" { "tests" } else { "" }
code := if trim(src_folder + " " + tests_folder) == "" { "*.py" } else { src_folder + " " + tests_folder }
random_string := uuid()

# === Update dependencies ===

# Update direct and indirect Python dependencies.
[private]
update-py-dependencies folder:
    uv run --frozen --no-sync --directory "{{ folder }}" --script "{{ uv_update_script }}"
    uv sync --upgrade --quiet --no-progress --directory "{{ folder }}"

# Update direct and indirect JavaScript dependencies.
[private]
update-js-dependencies folder:
    # Note: major updates are not done automatically by npm
    cd {{ folder }} && npm update --fund=false --ignore-scripts

alias update-deps := update-dependencies

# Update direct and indirect dependencies.
[parallel]
update-dependencies: (update-py-dependencies "tools") (update-py-dependencies "components/shared_code") (update-py-dependencies "components/api_server") (update-py-dependencies "components/collector") (update-py-dependencies "components/notifier") (update-js-dependencies "components/frontend") (update-js-dependencies "components/renderer") (update-py-dependencies "docs") (update-js-dependencies "docs") (update-py-dependencies "release") (update-py-dependencies "tests/application_tests") (update-py-dependencies "tests/feature_tests")

# === Install  dependencies ===

# Install Python dependencies from the lock file.
[no-cd]
[private]
install-py-dependencies:
    uv sync --no-progress --locked --all-extras --all-groups

# Install JavaScript dependencies from the lock file.
[no-cd]
[private]
install-js-dependencies:
    npm install --ignore-scripts --silent

# Build the JavaScript artifact(s) from the code.
[no-cd]
[private]
build-js: install-js-dependencies
    npm run --ignore-scripts build

# === Build artifacts ===

# Build the documentation from the code.
[no-cd]
[private]
build-docs: install-py-dependencies
    uv run sphinx-build src build

# Build artifacts or components from the code. Run `just build-help` for more information.
[no-cd]
build *components:
    {{ if has_sphinx == "true" { "just build-docs" } else if has_js_build_script == "true" { "just build-js" } else if docker_folder_exists == "true" { f"docker compose build {{components}}" } else { "echo 'Nothing to build in this folder'" } }}

components := `ls components`

[private]
build-help:
    echo build *{{ CYAN }}components{{ NORMAL }} {{ BLUE }}
    echo - In docs/, builds the documentation.
    echo - In components/frontend/, builds the frontend bundle.
    echo - In the project root, builds Docker components. Pass one or more component names
    echo "  to build specific Docker components or no names to build them all."
    echo "  Possible Docker component names are:"
    echo '  {{ CYAN }}{{ replace(components, "\n", ", ") }}'

# === Start components ===

# Start the Python component.
[no-cd]
[private]
start-py-component: install-py-dependencies
    uv run python src/quality_time*.py

# Start the JavaScript component.
[no-cd]
[private]
start-js-component: install-js-dependencies
    npm run start

# Start one or more component(s). Run `just start-help` for more information.
[no-cd]
start *components:
    {{ if pyproject_toml_exists == "true" { "just start-py-component" } else if has_js_start_script == "true" { "just start-js-component" } else if docker_folder_exists == "true" { f"docker compose up {{components}}" } else { "echo 'Nothing to start in this folder'" } }}

[private]
start-help:
    echo start *{{ CYAN }}components{{ NORMAL }} {{ BLUE }}
    echo - In components/api_server/, starts the API-server locally.
    echo - In components/collector/, starts the collector locally.
    echo - In components/notifier/, starts the notifier locally.
    echo - In components/frontend/, starts the frontend locally.
    echo - In the project root, starts Docker components. Pass one or more component names
    echo '  to start specific Docker components or no names to start them all.'
    echo '  Possible Docker component names are:'
    echo '  {{ CYAN }}{{ replace(components, "\n", ", ") }}'

# === Run tests ===

# Run the Python unit tests.
[no-cd]
[no-quiet]
[private]
py-unit-test $PYTHONDEVMODE="1" $PYTHONPATH="src:$PYTHONPATH": install-py-dependencies
    uv run coverage run -m unittest --quiet
    uv run coverage report --fail-under=0
    uv run coverage html --fail-under=0
    uv run coverage xml  # Fail if coverage is too low, but only after the text and HTML reports have been generated

# Run the JavaScript unit tests. Pass 'cov' to also measure the test coverage.
[no-cd]
[no-quiet]
[private]
js-unit-test *cov: install-js-dependencies
    npm run test {{ if cov == "cov" { "-- --coverage" } else { "" } }}

# Run the unit tests, in the current working directory. Pass 'cov' to also measure the JavaScript test coverage (Python test coverage is always measured).
[no-cd]
test *cov:
    {{ if has_py_unit_tests == "true" { "just py-unit-test" } else { "" } }}
    {{ if has_js_test_script == "true" { f"just js-unit-test {{cov}}" } else { "" } }}
    {{ if has_py_unit_tests + has_js_test_script == "falsefalse" { "echo 'Nothing to test'" } else { "" } }}

# === Run checks ===

# Run mypy
[no-cd]
[private]
mypy: install-py-dependencies
    uv run mypy {{ code }}

# Run fixit
[no-cd]
[private]
fixit: install-py-dependencies
    uv run fixit lint {{ code }}

# Run ruff
[no-cd]
[private]
ruff: install-py-dependencies
    uv run ruff format --check {{ code }}
    uv run ruff check {{ code }}

# Run pyproject-fmt
[no-cd]
[private]
pyproject-fmt: install-py-dependencies
    uv run pyproject-fmt --check pyproject.toml

# Run troml
[no-cd]
[private]
troml: install-py-dependencies
    uv run troml check

# Run pip-audit
[no-cd]
[private]
pip-audit: install-py-dependencies
    uv export --quiet --directory . --format requirements-txt --no-emit-package shared-code > /tmp/requirements-{{ random_string }}.txt
    uv run pip-audit --requirement /tmp/requirements-{{ random_string }}.txt --disable-pip --progress-spinner off
    rm -f /tmp/requirements-{{ random_string }}.txt

# Run bandit
[no-cd]
[private]
bandit: install-py-dependencies
    uv run bandit --configfile pyproject.toml --quiet --recursive {{ code }}

# Run vulture
[no-cd]
[private]
vulture: install-py-dependencies
    uv run vulture --exclude .venv --min-confidence 0 {{ code }} .vulture-whitelist.py

# Run vale
[no-cd]
[private]
vale: install-py-dependencies
    {{ if has_vale == "true" { "uv run vale sync; uv run vale --no-wrap --glob '*.md' src" } else { "" } }}

# Run yamllint
[no-cd]
[private]
yamllint: install-py-dependencies
    {{ if has_yamllint == "true" { "uv run yamllint ../publiccode.yml" } else { "" } }}

# Run sphinx
[no-cd]
[private]
sphinx: install-py-dependencies
    echo Running sphinx linkcheck may take a while, be patient...
    {{ if has_sphinx == "true" { "uv run sphinx-build -M linkcheck src build --quiet --jobs auto" } else { "" } }}

# Run Python checks.
[no-cd]
[parallel]
[private]
check-py: mypy fixit ruff pyproject-fmt troml pip-audit bandit vulture vale yamllint sphinx

# Run npm lint
[no-cd]
[private]
npm-lint: install-js-dependencies
    npm run lint --if-present

# Run npm audit
[no-cd]
[private]
npm-audit: install-js-dependencies
    npm audit

# Run npm outdated
[no-cd]
[private]
npm-outdated: install-js-dependencies
    npm outdated || true  # Don't fail, we can't upgrade ESLint yet due to peer dependencies needing updates

# Run JavaScript checks.
[no-cd]
[parallel]
[private]
check-js: npm-lint npm-audit npm-outdated

# Run the quality checks, in the current working directory.
[no-cd]
check:
    {{ if pyproject_toml_exists == "true" { "just check-py" } else { "" } }}
    {{ if package_json_exists == "true" { "just check-js" } else { "" } }}
    {{ if pyproject_toml_exists + package_json_exists == "falsefalse" { "echo 'Nothing to check'" } else { "" } }}

# === Fix issues ===

# Fix Python quality issues that can be fixed automatically.
[no-cd]
[private]
fix-py: install-py-dependencies
    uv run ruff format {{ code }}
    uv run ruff check --fix {{ code }}
    uv run fixit fix {{ code }}
    # Pyproject-fmt returns exit code 1 when pyproject.toml needs formatting, ignore it when formatting:
    uv run pyproject-fmt --no-print-diff pyproject.toml || true
    uv run troml suggest --fix
    # Vulture returns exit code 3 when there is dead code, ignore it when writing the whitelist:
    uv run vulture --exclude .venv --min-confidence 0 --make-whitelist {{ code }} >| .vulture-whitelist.py || true

# Fix JavaScript quality issues that can be fixed automatically.
[no-cd]
[private]
fix-js: install-js-dependencies
    npm run fix

# Fix quality issues that can be fixed automatically, in the current working directory.
[no-cd]
fix:
    {{ if pyproject_toml_exists == "true" { "just fix-py" } else { "" } }}
    {{ if has_js_fix_script == "true" { "just fix-js" } else { "" } }}

# === Release ===

# Release Quality-time. Run `just release-help` for more information.
[working-directory('release')]
release *args:
    uv run --script release.py {{ args }}

[private]
[working-directory('release')]
release-help:
    uv run --script release.py --help

# === CI/CD ===

# Run all tests and checks in CI.
[no-cd]
[private]
ci $CI="true": test check

# === Clean ===

# Clean caches, build folders, and generated files
clean:
    rm -f .coverage */.coverage */*/.coverage
    rm -rf build */build */*/build
    rm -rf .*_cache */.*_cache */*/.*_cache
    rm -rf */node_modules */*/node_modules
    rm -rf */*.egg-info */*/*.egg-info */*/*/*.egg-info
    rm -rf */.venv */*/.venv
    rm -rf */*/dist
    rm -rf */*/htmlcov
