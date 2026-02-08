set positional-arguments := true
set quiet := true

_default:
    @just --list

export COVERAGE_RCFILE := justfile_directory() + "/.coveragerc"
uv_update_script := justfile_directory() + "/tools/uv_update.py"
docker_folder_exists := path_exists(invocation_directory() + '/docker')
src_folder_exists := path_exists(invocation_directory() + '/src')
tests_folder_exists := path_exists(invocation_directory() + '/tests')
package_json_exists := path_exists(invocation_directory() + '/package.json')
pyproject_toml := invocation_directory() + "/pyproject.toml"
pyproject_toml_exists := path_exists(pyproject_toml)
pyproject_toml_contents := if pyproject_toml_exists == "true" { read(pyproject_toml) } else { "" }
js_build_script := if package_json_exists == "true" { shell(f"npm --prefix={{invocation_directory()}} pkg get scripts.build") } else { "{}" }
js_start_script := if package_json_exists == "true" { shell(f"npm --prefix={{invocation_directory()}} pkg get scripts.start") } else { "{}" }
js_test_script := if package_json_exists == "true" { shell(f"npm --prefix={{invocation_directory()}} pkg get scripts.test") } else { "{}" }
js_lint_script := if package_json_exists == "true" { shell(f"npm --prefix={{invocation_directory()}} pkg get scripts.lint") } else { "{}" }
js_fix_script := if package_json_exists == "true" { shell(f"npm --prefix={{invocation_directory()}} pkg get scripts.fix") } else { "{}" }
has_py_unit_tests := if pyproject_toml_exists == "true" { tests_folder_exists } else { "false" }
has_sphinx := if pyproject_toml_contents =~ '"sphinx[<=]=[A-Za-z0-9_.\-]+"' { "true" } else { "false" }
has_yamllint := if pyproject_toml_contents =~ '"yamllint[<=]=[A-Za-z0-9_.\-]+"' { "true" } else { "false" }
has_vale := if pyproject_toml_contents =~ '"vale[<=]=[A-Za-z0-9_.\-]+"' { "true" } else { "false" }
src_folder := if src_folder_exists == "true" { "src" } else { "" }
tests_folder := if tests_folder_exists == "true" { "tests" } else { "" }
code := if trim(src_folder + " " + tests_folder) == "" { "*.py" } else { src_folder + " " + tests_folder }

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
update-dependencies: (update-py-dependencies "components/shared_code") (update-py-dependencies "components/api_server") (update-py-dependencies "components/collector") (update-py-dependencies "components/notifier") (update-js-dependencies "components/frontend") (update-js-dependencies "components/renderer") (update-py-dependencies "docs") (update-js-dependencies "docs") (update-py-dependencies "release") (update-py-dependencies "tests/application_tests") (update-py-dependencies "tests/feature_tests")

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

# Build the artifacts or components from the code, in the current working directory. Builds Docker components if the working directory is the project root. Pass one or more of 'api_server', 'collector', 'notifier', 'frontend', 'proxy', 'database', 'renderer', 'testdata', or 'testldap' to build specific components or none to build them all.
[no-cd]
build *components:
    {{ if has_sphinx == "true" { "just build-docs" } else if js_build_script != "{}" { "just build-js" } else if docker_folder_exists == "true" { f"docker compose build {{components}}" } else { "echo 'Nothing to build in this folder'" } }}

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

# Start component(s). Starts a component locally if the current working directory is a component folder (components/api_server, components/collector, components/notifier, or components/frontend). Starts components in Docker if the working directory is the project root. Pass one or more of 'api_server', 'collector', 'notifier', 'frontend', 'proxy', 'database', 'renderer', 'testdata', or 'testldap' to start specific components or none to start them all.
[no-cd]
start *components:
    {{ if pyproject_toml_exists == "true" { "just start-py-component" } else if js_start_script != "{}" { "just start-js-component" } else if docker_folder_exists == "true" { f"docker compose up {{components}}" } else { "echo 'Nothing to start in this folder'" } }}

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
    {{ if js_test_script != "{}" { f"just js-unit-test {{cov}}" } else { "" } }}
    {{ if has_py_unit_tests + js_test_script == "false{}" { "echo 'Nothing to test'" } else { "" } }}

# === Run checks ===

# Run Python checks.
[no-cd]
[private]
check-py: install-py-dependencies
    uv run ruff format --check {{ code }}
    uv run ruff check {{ code }}
    uv run mypy {{ code }}
    uv run fixit lint {{ code }}
    uv run pyproject-fmt --check pyproject.toml
    uv run troml check
    uv export --quiet --directory . --format requirements-txt --no-emit-package shared-code > /tmp/requirements.txt
    uv run pip-audit --requirement /tmp/requirements.txt --disable-pip
    uv run bandit --configfile pyproject.toml --quiet --recursive {{ code }}
    uv run vulture --exclude .venv --min-confidence 0 {{ code }} .vulture-whitelist.py
    {{ if has_vale == "true" { "uv run vale sync; uv run vale --no-wrap --glob '*.md' src" } else { "" } }}
    {{ if has_yamllint == "true" { "uv run yamllint ../publiccode.yml" } else { "" } }}
    {{ if has_sphinx == "true" { "uv run sphinx-build -M linkcheck src build" } else { "" } }}

# Run JavaScript checks.
[no-cd]
[private]
check-js: install-js-dependencies
    npm run lint

# Run the quality checks, in the current working directory.
[no-cd]
check:
    {{ if pyproject_toml_exists == "true" { "just check-py" } else { "" } }}
    {{ if js_lint_script != "{}" { "just check-js" } else { "" } }}
    {{ if pyproject_toml_exists + js_lint_script == "false{}" { "echo 'Nothing to check'" } else { "" } }}

# === Fix issues ===

# Fix Python quality issues that can be fixed automatically.
[no-cd]
[private]
fix-py: install-py-dependencies
    uv run ruff format {{ code }}
    uv run ruff check --fix {{ code }}
    uv run fixit fix {{ code }}
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
    {{ if js_fix_script != "{}" { "just fix-js" } else { "" } }}

# === Release ===

# Release Quality-time. Run `just release --help` for more information.
[working-directory('release')]
release *args:
    uv run --script release.py {{ args }}

# === CI/CD ===

# Run all tests and checks in CI.
[no-cd]
[private]
ci $CI="true": test check

# === Clean ===

# Clean caches, build folders, and generated files
clean:
    rm -f .coverage
    rm -f */.coverage
    rm -f */*/.coverage
    rm -rf build
    rm -rf */build
    rm -rf */*/build
    rm -rf .*_cache
    rm -rf */.*_cache
    rm -rf */*/.*_cache
    rm -rf */node_modules
    rm -rf */*/node_modules
    rm -rf */*.egg-info
    rm -rf */*/*.egg-info
    rm -rf */*/*/*.egg-info
    rm -rf */.venv
    rm -rf */*/.venv
    rm -rf */*/dist
    rm -rf */*/htmlcov
