set guards := true
set positional-arguments := true
set quiet := true

_default:
    @just --list

alias help := _default

export COVERAGE_RCFILE := justfile_directory() + "/.coveragerc"
components := `ls components`
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
code := if trim(src_folder + " " + tests_folder) == "" { ".?*.py" } else { src_folder + " " + tests_folder }
random_string := uuid()
uv_run := "uv run --quiet"
update_dep := uv_run + " --project tools/update_dependencies tools/update_dependencies/src/update_"
pyproject_fmt := uv_run + " pyproject-fmt --no-generate-python-version-classifiers"

# === Update dependencies ===

# Update Docker images in the CircleCI config.
[private]
update-circle-ci-config:
    {{ update_dep }}circle_ci_config.py

# Update Docker base images in Dockerfiles.
[private]
update-docker-base-images:
    {{ update_dep }}dockerfile_base_image.py

# Update GitHub Actions in GitHub workflow YAML files.
[private]
update-github-actions:
    {{ update_dep }}github_action.py

# Update direct and indirect Python dependencies.
[private]
update-py-dependencies:
    {{ update_dep }}pyproject_toml.py

# Update direct and indirect JavaScript dependencies.
[private]
update-js-dependencies:
    # Note: major updates are not done automatically by npm
    {{ update_dep }}package_json.py

# Update the Node engine version in package.json files.
[private]
update-node-engine:
    {{ update_dep }}node_engine.py

# Update the jsdelivr CDN package versions in the Sphinx config.
[private]
update-jsdelivr:
    {{ update_dep }}jsdelivr.py

alias update-deps := update-dependencies

# Update direct and indirect dependencies. Set the GITHUB_TOKEN environment variable to prevent hitting GitHub rate limits.
[parallel]
update-dependencies: update-docker-base-images update-py-dependencies update-github-actions update-circle-ci-config update-jsdelivr
    just update-node-engine
    just update-js-dependencies

# === Install dependencies ===

# Install Python dependencies from the lock file.
[no-cd]
[private]
install-py-dependencies:
    ?[ {{ pyproject_toml_exists }} = true ]
    uv sync --no-progress --quiet --locked --all-extras --all-groups --reinstall-package shared-code

# Install JavaScript dependencies from the lock file.
[no-cd]
[private]
install-js-dependencies:
    ?[ {{ package_json_exists }} = true ]
    npm install --ignore-scripts --silent

# === Build artifacts ===

# Build the docker containers.
[no-cd]
[private]
build-docker *components:
    ?[ {{ docker_folder_exists }} = true ]
    docker compose build {{ components }}

# Build the JavaScript artifact(s) from the code.
[no-cd]
[private]
build-js: install-js-dependencies
    ?[ {{ has_js_build_script }} = true ]
    npm run --ignore-scripts --silent build

# Build the documentation from the code.
[no-cd]
[private]
build-docs: install-py-dependencies
    ?[ {{ has_sphinx }} = true ]
    {{ uv_run }} sphinx-build src build

# Build artifacts or components from the code. Run `just build-help` for more information.
[no-cd]
build *components: build-docs build-js (build-docker components)
    ?[ {{ has_sphinx }} = false ] && [ {{ has_js_build_script }} = false ] && [ {{ docker_folder_exists }} = false ]
    echo "Nothing to build in this folder"

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

# Start the Docker containers.
[no-cd]
[private]
start-docker-component *components:
    ?[ {{ docker_folder_exists }} = true ]
    COLUMNS=$({{ uv_run }} python -c 'import shutil, subprocess; w = shutil.get_terminal_size().columns; s = subprocess.run(["docker", "compose", "config", "--services"], capture_output=True, text=True).stdout; print(w - max(len(line.strip()) for line in s.splitlines()) - 6)') docker compose up {{ components }}

# Start the Python component.
[no-cd]
[private]
start-py-component: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ uv_run }} python src/quality_time*.py

# Start the JavaScript component.
[no-cd]
[private]
start-js-component: install-js-dependencies
    ?[ {{ has_js_start_script }} = true ]
    npm run --silent start

# Start one or more component(s). Run `just start-help` for more information.
[no-cd]
start *components: start-py-component start-js-component (start-docker-component components)
    ?[ {{ pyproject_toml_exists }} = false ] && [ {{ has_js_start_script }} = false ] && [ {{ docker_folder_exists }} = false ]
    echo "Nothing to start in this folder"

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
[private]
py-unit-test $PYTHONDEVMODE="1" $PYTHONPATH="src:$PYTHONPATH": install-py-dependencies
    ?[ {{ has_py_unit_tests }} = true ]
    {{ uv_run }} coverage run -m unittest --quiet
    {{ uv_run }} coverage report --fail-under=0
    {{ uv_run }} coverage html --quiet --fail-under=0
    {{ uv_run }} coverage xml --quiet  # Fail if coverage is too low, but only after the text and HTML reports have been generated

# Run the JavaScript unit tests. Pass 'cov' to also measure the test coverage.
[no-cd]
[private]
js-unit-test *cov: install-js-dependencies
    ?[ {{ has_js_test_script }} = true ]
    npm run --silent test {{ if cov == "cov" { "-- --coverage" } else { "" } }}

# Run the unit tests, in the current working directory. Pass 'cov' to also measure the JavaScript test coverage (Python test coverage is always measured).
[no-cd]
test *cov: py-unit-test (js-unit-test cov)
    ?[ {{ has_py_unit_tests }} = false ] && [ {{ has_js_test_script }} = false ]
    echo "Nothing to test in this folder"

# === Run checks ===

# Run mypy.
[no-cd]
[private]
mypy: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ uv_run }} mypy {{ code }}

# Run fixit.
[no-cd]
[private]
fixit: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ uv_run }} fixit --quiet lint {{ code }}

# Run ruff.
[no-cd]
[private]
ruff: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ uv_run }} ruff format --quiet --check {{ code }}
    {{ uv_run }} ruff check --quiet {{ code }}

# Run pyproject-fmt.
[no-cd]
[private]
pyproject-fmt: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ pyproject_fmt }} --check pyproject.toml

# Run troml.
[no-cd]
[private]
troml: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ uv_run }} troml check

# Run pip-audit.
[no-cd]
[private]
pip-audit: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    trap 'rm -f /tmp/requirements-{{ random_string }}.txt' EXIT; \
    uv export --quiet --directory . --format requirements-txt --no-emit-package shared-code > /tmp/requirements-{{ random_string }}.txt && \
    {{ uv_run }} pip-audit --requirement /tmp/requirements-{{ random_string }}.txt --disable-pip --progress-spinner off

# Run uv audit.
[no-cd]
[private]
uv-audit: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    uv --preview-features audit audit --locked --quiet

# Run bandit.
[no-cd]
[private]
bandit: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ uv_run }} bandit --configfile pyproject.toml --quiet --recursive {{ code }}

# Run vulture.
[no-cd]
[private]
vulture: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ uv_run }} vulture --exclude .venv --min-confidence 0 {{ code }} .vulture-whitelist.py

# Run vale.
[no-cd]
[private]
vale: install-py-dependencies
    ?[ {{ has_vale }} = true ]
    {{ uv_run }} vale sync
    {{ uv_run }} vale --no-wrap --glob '*.md' src

# Run yamllint from the project root.
[private]
yamllint: install-py-dependencies
    ?[ {{ has_yamllint }} = true ]
    {{ uv_run }} yamllint -c docs/.yamllint .

# Run sphinx.
[no-cd]
[private]
sphinx: install-py-dependencies
    ?[ {{ has_sphinx }} = true ]
    echo Running sphinx linkcheck may take a while, be patient...
    {{ uv_run }} sphinx-build -M linkcheck src build --quiet --jobs auto

# Run Python checks.
[no-cd]
[parallel]
[private]
check-py: mypy fixit ruff pyproject-fmt troml pip-audit uv-audit bandit vulture vale yamllint sphinx

# Run npm lint.
[no-cd]
[private]
npm-lint: install-js-dependencies
    ?[ {{ package_json_exists }} = true ]
    npm run --silent lint --if-present

# Run npm audit.
[no-cd]
[private]
npm-audit: install-js-dependencies
    ?[ {{ package_json_exists }} = true ]
    npm audit

# Run npm outdated. Ignore outdated packages that can't be updated (current == wanted).
[no-cd]
[private]
npm-outdated: install-js-dependencies
    ?[ {{ package_json_exists }} = true ]
    npm outdated --json | uv run python -c "import json, sys; updates = [f'{k}: {v['current']} -> {v['wanted']}' for k, v in json.loads(sys.stdin.read()).items() if v['wanted'] != v['current']]; print('\n'.join(updates), end='\n' if updates else ''); sys.exit(1 if updates else 0)"

# Run JavaScript checks.
[no-cd]
[parallel]
[private]
check-js: npm-lint npm-audit npm-outdated

# Run the quality checks, in the current working directory.
[no-cd]
check: check-js check-py
    ?[ {{ pyproject_toml_exists }} = false ] && [ {{ package_json_exists }} = false ]
    echo "Nothing to check in this folder"

# === Fix issues ===

# Fix Python quality issues that can be fixed automatically.
[no-cd]
[private]
fix-py: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ uv_run }} ruff format --quiet {{ code }}
    {{ uv_run }} ruff check --quiet --fix {{ code }}
    {{ uv_run }} fixit fix {{ code }}
    # Pyproject-fmt returns exit code 1 when pyproject.toml needs formatting, ignore it when formatting:
    {{ pyproject_fmt }} --no-print-diff pyproject.toml || true
    {{ uv_run }} troml suggest --fix
    # Vulture returns exit code 3 when there is dead code, ignore it when writing the whitelist:
    {{ uv_run }} vulture --exclude .venv --min-confidence 0 --make-whitelist {{ code }} > .vulture-whitelist.py || true

# Fix JavaScript quality issues that can be fixed automatically.
[no-cd]
[private]
fix-js: install-js-dependencies
    ?[ {{ has_js_fix_script }} = true ]
    npm run --silent fix

# Fix quality issues that can be fixed automatically, in the current working directory.
[no-cd]
fix: fix-py fix-js
    ?[ {{ pyproject_toml_exists }} = false ] && [ {{ has_js_fix_script }} = false ]
    echo "Nothing to fix in this folder"

# === Release ===

# Release Quality-time. Run `just release-help` for more information.
[working-directory('tools/release')]
release *args:
    {{ uv_run }} --script release.py {{ args }}

[private]
[working-directory('tools/release')]
release-help:
    {{ uv_run }} --script release.py --help

# === CI/CD ===

# Run all tests and checks in CI.
[no-cd]
[private]
ci $CI="true": test check

# === Clean ===

# Clean caches, build folders, and generated files.
clean:
    rm -f .coverage */.coverage */*/.coverage
    rm -rf build */build */*/build
    rm -rf .*_cache */.*_cache */*/.*_cache
    rm -rf */node_modules */*/node_modules
    rm -rf */*.egg-info */*/*.egg-info */*/*/*.egg-info
    rm -rf */.venv */*/.venv
    rm -rf */*/dist
    rm -rf */*/htmlcov
