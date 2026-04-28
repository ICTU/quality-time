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
has_zizmor := if pyproject_toml_contents =~ '"zizmor[<=]=[A-Za-z0-9_.\-]+"' { "true" } else { "false" }
src_folder := if src_folder_exists == "true" { "src" } else { "" }
tests_folder := if tests_folder_exists == "true" { "tests" } else { "" }
code := if trim(src_folder + " " + tests_folder) == "" { ".?*.py" } else { src_folder + " " + tests_folder }
random_string := uuid()
uv_run := "uv run --quiet"
update_dep := uv_run + " --project tools/update_dependencies tools/update_dependencies/src/update_"
coverage := uv_run + " coverage"
fixit := uv_run + " fixit --quiet"
pyproject_fmt := uv_run + " pyproject-fmt --no-generate-python-version-classifiers"
ruff := uv_run + " ruff --quiet"
troml := uv_run + " troml"
vulture := uv_run + " vulture --exclude .venv --min-confidence 0"
vulture_whitelist := ".vulture-whitelist.py"
sphinx_build := uv_run + " sphinx-build"
npm_run := "npm run --silent"
zizmor := uv_run + " zizmor --no-progress --quiet " + justfile_directory() + "/.github/workflows"

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
    {{ npm_run }} --ignore-scripts build

# Build the documentation from the code.
[no-cd]
[private]
build-docs: install-py-dependencies
    ?[ {{ has_sphinx }} = true ]
    {{ sphinx_build }} src build

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
    {{ npm_run }} start

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

# Run the Python unit tests. Pass '--coverage=no' to skip reporting test coverage.
[arg("cov", long="coverage", short="c", pattern="default|yes|no", help="Measure unit test coverage?")]
[env("PYTHONDEVMODE", "1")]
[env("PYTHONPATH", "src")]
[no-cd]
[private]
py-unit-test cov="yes" *tests: install-py-dependencies
    ?[ {{ has_py_unit_tests }} = true ]
    {{ if cov == "no" { uv_run + " python" } else { coverage + " run" } }} -m unittest --quiet {{ tests }}
    ?[ "{{ cov }}" != "no" ]
    {{ coverage }} report --fail-under=0
    {{ coverage }} html --quiet --fail-under=0
    {{ coverage }} xml --quiet  # Fail if coverage is too low, but only after the text and HTML reports have been generated

# Run the JavaScript unit tests. Pass '--coverage=yes' to measure test coverage.
[arg("cov", long="coverage", short="c", pattern="default|yes|no", help="Measure unit test coverage?")]
[no-cd]
[private]
js-unit-test cov="no" *tests: install-js-dependencies
    ?[ {{ has_js_test_script }} = true ]
    {{ npm_run }} test -- {{ if cov == "yes" { "--coverage" } else { tests } }}

# Run the unit tests, in the current working directory. Measures coverage of Python unit tests by default. Pass 'cov' to also measure the coverage of JavaScript unit tests. Pass 'nocov' to skip measuring coverage of Python unit tests.
[arg("cov", long="coverage", short="c", pattern="default|yes|no", help="Measure unit test coverage? Default means yes for Python and no for Javascript")]
[no-cd]
test cov="default" *tests: (py-unit-test cov tests) (js-unit-test cov tests)
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
    {{ fixit }} lint {{ code }}

# Run ruff.
[no-cd]
[private]
ruff: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ ruff }} format --check {{ code }}
    {{ ruff }} check {{ code }}

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
    {{ troml }} check

# Run pip-audit.
[no-cd]
[private]
pip-audit: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    trap 'rm -f /tmp/requirements-{{ random_string }}.txt' EXIT; \
    uv export --quiet --directory . --format requirements-txt --no-emit-package shared-code > /tmp/requirements-{{ random_string }}.txt && \
    {{ uv_run }} pip-audit --requirement /tmp/requirements-{{ random_string }}.txt --ignore-vuln GHSA-58qw-9mgm-455v --disable-pip --progress-spinner off

# Run uv audit.
[no-cd]
[private]
uv-audit: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    uv audit --locked --quiet --ignore-until-fixed GHSA-58qw-9mgm-455v

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
    {{ vulture }} {{ code }} {{ vulture_whitelist }}

# Run vale.
[no-cd]
[private]
vale: install-py-dependencies
    ?[ {{ has_vale }} = true ]
    {{ uv_run }} vale sync
    {{ uv_run }} vale --no-wrap --glob '*.md' src

# Run yamllint.
[no-cd]
[private]
yamllint: install-py-dependencies
    ?[ {{ has_yamllint }} = true ]
    {{ uv_run }} yamllint -c .yamllint {{ justfile_directory() }}

# Run sphinx.
[no-cd]
[private]
sphinx: install-py-dependencies
    ?[ {{ has_sphinx }} = true ]
    echo Running sphinx linkcheck may take a while, be patient...
    {{ sphinx_build }} -M linkcheck src build --quiet --jobs auto

# Run zizmor.
[no-cd]
[private]
zizmor: install-py-dependencies
    ?[ {{ has_zizmor }} = true ]
    {{ zizmor }}

# Run Python checks.
[no-cd]
[parallel]
[private]
check-py: mypy fixit ruff pyproject-fmt troml pip-audit uv-audit bandit vulture vale yamllint sphinx zizmor

# Run npm lint.
[no-cd]
[private]
npm-lint: install-js-dependencies
    ?[ {{ package_json_exists }} = true ]
    {{ npm_run }} lint --if-present

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
    {{ ruff }} format {{ code }}
    {{ ruff }} check --fix {{ code }}
    {{ fixit }} fix {{ code }}
    # Pyproject-fmt returns exit code 1 when pyproject.toml needs formatting, ignore it when formatting:
    {{ pyproject_fmt }} --no-print-diff pyproject.toml || true
    {{ troml }} suggest --fix
    # Vulture returns exit code 3 when there is dead code, ignore it when writing the whitelist:
    {{ vulture }} --make-whitelist {{ code }} > {{ vulture_whitelist }} || true
    ?[ {{ has_zizmor }} = true ]
    {{ zizmor }} --fix=all

# Fix JavaScript quality issues that can be fixed automatically.
[no-cd]
[private]
fix-js: install-js-dependencies
    ?[ {{ has_js_fix_script }} = true ]
    {{ npm_run }} fix

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
[parallel]
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
