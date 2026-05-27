set guards
set positional-arguments
set quiet
set unstable # for user-defined functions

_default:
    @just --list

alias help := _default

export COVERAGE_RCFILE := justfile_directory() + "/.coveragerc"
components := `ls components`
exists(path) := path_exists(invocation_directory() + "/" + path)
docker_folder_exists := exists("docker")
package_json_exists := exists("package.json")
pyproject_toml_exists := exists("pyproject.toml")
pyproject_toml_contents := if pyproject_toml_exists == "true" { read(invocation_directory() + "/pyproject.toml") } else { "" }
js_scripts := if package_json_exists == "true" { shell(f"npm --prefix={{invocation_directory()}} pkg get scripts") } else { "{}" }
has_js_script(name) := if js_scripts =~ f'"{{name}}"' { "true" } else { "false" }
has_py_pkg(name) := if pyproject_toml_contents =~ f'"{{name}}[<=]=[A-Za-z0-9_.\-]+"' { "true" } else { "false" }
has_py_unit_tests := if pyproject_toml_exists == "true" { exists("tests") } else { "false" }
at_root := if invocation_directory() == justfile_directory() { "true" } else { "false" }
src_folder := if exists("src") == "true" { "src" } else { "" }
tests_folder := if exists("tests") == "true" { "tests" } else { "" }
code := if trim(src_folder + " " + tests_folder) == "" { ".?*.py" } else { src_folder + " " + tests_folder }
# Terminal width is read at parse time from stderr (still a TTY when stdout is captured by $() ); falls back to 200 if there's no TTY (CI, piped output).
term_width := shell("uv run --quiet --project tools/third_party python -c 'import os; print(os.get_terminal_size(2).columns if os.isatty(2) else 200)'")
uv_run := "uv run --quiet"
update_dep := uv_run + " --project tools/update_dependencies tools/update_dependencies/src/update_"
coverage := uv_run + " coverage"
fixit := uv_run + " fixit --quiet"
just_fmt := "just --unstable --fmt"
pyproject_fmt := uv_run + " pyproject-fmt --no-generate-python-version-classifiers"
ruff := uv_run + " ruff --quiet"
troml := uv_run + " troml"
ty := uv_run + ' ty check --no-progress --error-on-warning --color=${_color:-auto}'
vulture := uv_run + " vulture --exclude .venv --min-confidence 0"
vulture_whitelist := ".vulture-whitelist.py"
sphinx_build := uv_run + " sphinx-build"
npm_run := "npm run --silent"
project_wide_tools := uv_run + " --project " + justfile_directory() + "/tools/third_party"
# Prefix and suffix that wrap a check command: `{{ start_check(folder) }} <cmd> {{ end_check }}` captures stdout+stderr, prints `<recipe-name> [<folder>/ ]OK` or `NOK` + captured output on failure.
folder_prefix(folder) := if folder == "" { "" } else if folder == "." { "" } else { " " + trim_end_match(folder, "/") + "/" }
# Pick a tool-flag value based on `$_color` set by `start_check`. Useful for tools whose color flag values aren't `auto`/`always`/`never` (e.g. bandit's `screen`/`txt`, yamllint's `colored`/`auto`).
when_color(yes, no) := f'$([ "$_color" = always ] && echo {{yes}} || echo {{no}})'
start_check(folder) := f'_color=auto; [ -t 1 ] && { _color=always; export FORCE_COLOR=1; }; f="{{folder_prefix(folder)}}"; output=$({'
end_check := f'; } 2>&1) || { printf "%s%s {{RED}}NOK{{NORMAL}}\n%s\n" "$0" "$f" "$output"; exit 1; }; printf "%s%s {{GREEN}}OK{{NORMAL}}\n" "$0" "$f"'

# === Update dependencies ===

# Update Docker images in the CircleCI config.
[private]
update-circle-ci-config:
    {{ update_dep }}circle_ci_config.py

# Update Docker images in the Compose files.
[private]
update-docker-compose:
    {{ update_dep }}docker_compose.py

# Update Docker base images in Dockerfiles. Set the DOCKER_HUB_USERNAME and DOCKER_HUB_TOKEN environment variables to prevent hitting Docker rate limits.
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
update-dependencies: update-docker-base-images update-py-dependencies update-github-actions update-circle-ci-config update-docker-compose update-jsdelivr
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
    ?[ ! -e node_modules/.package-lock.json ] || [ package-lock.json -nt node_modules/.package-lock.json ]
    npm ci --silent

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
    ?[ {{ has_js_script("build") }} = true ]
    {{ npm_run }} build

# Build the documentation from the code.
[no-cd]
[private]
build-docs: install-py-dependencies
    ?[ {{ has_py_pkg("sphinx") }} = true ]
    {{ sphinx_build }} -W --keep-going src build

# Build artifacts or components from the code. Run `just build-help` for more information.
[no-cd]
build *components: build-docs build-js (build-docker components)
    ?[ {{ has_py_pkg("sphinx") }} = false ] && [ {{ has_js_script("build") }} = false ] && [ {{ docker_folder_exists }} = false ]
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
    COLUMNS=$({{ uv_run }} python -c 'import subprocess; s = subprocess.run(["docker", "compose", "config", "--services"], capture_output=True, text=True).stdout; print({{ term_width }} - max(len(line.strip()) for line in s.splitlines()) - 6)') docker compose up {{ components }}

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
    ?[ {{ has_js_script("start") }} = true ]
    {{ npm_run }} start

# Start one or more component(s). Run `just start-help` for more information.
[no-cd]
start *components: start-py-component start-js-component (start-docker-component components)
    ?[ {{ pyproject_toml_exists }} = false ] && [ {{ has_js_script("start") }} = false ] && [ {{ docker_folder_exists }} = false ]
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

# Run the JavaScript unit tests. Pass '--coverage=yes' to measure test coverage. Without explicit tests or coverage, only the tests for uncommitted changes are run if there are any.
[arg("cov", long="coverage", short="c", pattern="default|yes|no", help="Measure unit test coverage?")]
[no-cd]
[private]
js-unit-test cov="no" *tests: install-js-dependencies
    ?[ {{ has_js_script("test") }} = true ]
    if [ "{{ cov }}" = "yes" ]; then args="--coverage"; \
    elif [ -n "{{ tests }}" ]; then args="{{ tests }}"; \
    elif ! git diff --quiet HEAD -- {{ invocation_directory() }}/src; then args="--changed"; \
    else args=""; fi; \
    {{ npm_run }} test -- $args

[no-cd]
[private]
_test cov="default" *tests: (py-unit-test cov tests) (js-unit-test cov tests)
    ?[ {{ has_py_unit_tests }} = false ] && [ {{ has_js_script("test") }} = false ]
    echo "Nothing to test in this folder"

# Run the unit tests. Without args, runs in the current working directory; with --all/-a, runs in all relevant folders. Pass --coverage=yes/no to override the default (Python coverage on, JavaScript coverage off).
[arg("cov", long="coverage", short="c", pattern="default|yes|no", help="Measure unit test coverage? Default means yes for Python and no for Javascript")]
[arg("scope", long="all", short="a", value="all", help="Run tests in all relevant folders")]
[no-cd]
test cov="default" scope="" *tests:
    {{ if scope == "all" { "just test-all" } else { "just _test " + cov + " " + tests } }}

# Generate a JUnit XML test report at build/unittests.xml. Re-runs Python tests via xmlrunner; used by CI to feed test results to SonarCloud.
[env("PYTHONDEVMODE", "1")]
[env("PYTHONPATH", "src")]
[no-cd]
[private]
junit-xml: install-py-dependencies
    ?[ {{ has_py_unit_tests }} = true ]
    mkdir -p build
    {{ uv_run }} --with=unittest-xml-reporting -m xmlrunner --output-file build/unittests.xml

# Run the unit tests, in all relevant folders.
[parallel]
[private]
test-all: (run "test" "components/api_server") (run "test" "components/collector") (run "test" "components/frontend") (run "test" "components/notifier") (run "test" "components/renderer") (run "test" "components/shared_code") (run "test" "docs") (run "test" "tools/release") (run "test" "tools/update_dependencies")

# === Run checks ===

# Run ty to type check Python code.
[no-cd]
[private]
ty folder="": install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ start_check(folder) }} {{ ty }} {{ code }} {{ end_check }}

# Run mypy to type check Python code.
[no-cd]
[private]
mypy folder="": install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ start_check(folder) }} {{ uv_run }} mypy {{ code }} {{ end_check }}

# Run fixit to lint Python code.
[no-cd]
[private]
fixit folder="": install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ start_check(folder) }} {{ fixit }} lint {{ code }} {{ end_check }}

# Run ruff to lint and check the formatting of Python code.
[no-cd]
[private]
ruff folder="": install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ start_check(folder) }} {{ ruff }} format --check {{ code }} && {{ ruff }} check {{ code }} {{ end_check }}

# Run pyproject-fmt to check the formatting of pyproject.toml files.
[no-cd]
[private]
pyproject-fmt folder="": install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ start_check(folder) }} {{ pyproject_fmt }} --check pyproject.toml {{ end_check }}

# Run troml to the check the classifiers in pyproject.toml files.
[no-cd]
[private]
troml folder="": install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ start_check(folder) }} {{ troml }} check {{ end_check }}

# Run pip-audit to check Python dependencies for known security vulnerabilities.
[no-cd]
[private]
pip-audit folder="": install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    req=$(mktemp); trap "rm -f $req" EXIT; \
    {{ start_check(folder) }} uv export --quiet --color never --directory . --format requirements-txt --no-emit-package shared-code > $req && \
    {{ uv_run }} pip-audit --requirement $req --ignore-vuln GHSA-58qw-9mgm-455v --disable-pip --progress-spinner off {{ end_check }}

# Run uv audit to check Python dependencies for known security vulnerabilities.
[no-cd]
[private]
uv-audit folder="": install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ start_check(folder) }} uv audit --locked --quiet --ignore-until-fixed GHSA-58qw-9mgm-455v {{ end_check }}

# Run bandit to check Python code for security vulnerabilities.
[no-cd]
[private]
bandit folder="": install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ start_check(folder) }} {{ uv_run }} bandit --configfile pyproject.toml --quiet --recursive --format {{ when_color("screen", "txt") }} {{ code }} {{ end_check }}

# Run vulture to check for dead Python code.
[no-cd]
[private]
vulture folder="": install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ start_check(folder) }} {{ vulture }} {{ code }} {{ vulture_whitelist }} {{ end_check }}

# Run vale to check markdown files for spelling and style.
[no-cd]
[private]
vale folder="": install-py-dependencies
    ?[ {{ has_py_pkg("vale") }} = true ]
    {{ start_check(folder) }} {{ uv_run }} vale sync && {{ uv_run }} vale --no-wrap --glob '*.md' src {{ end_check }}

# Run yamllint to lint YAML files such as workflow definitions.
[no-cd]
[private]
yamllint folder="":
    ?[ {{ at_root }} = true ]
    {{ start_check(folder) }} {{ project_wide_tools }} yamllint -c .yamllint -f {{ when_color("colored", "auto") }} . {{ end_check }}

# Run sphinx linkcheck. Excluded from `just check` because external link availability makes it flaky and slow; runs on a schedule in CI.
[no-cd]
linkcheck: install-py-dependencies
    ?[ {{ has_py_pkg("sphinx") }} = true ]
    echo Running sphinx linkcheck may take a while, be patient...
    {{ sphinx_build }} -M linkcheck src build --quiet --jobs auto

# Run zizmor to audit GitHub Action workflows.
[no-cd]
[private]
zizmor folder="":
    ?[ {{ at_root }} = true ]
    {{ start_check(folder) }} {{ project_wide_tools }} zizmor --no-progress --quiet .github/workflows {{ end_check }}

# Run compose-lint on docker-compose.yml and on the merged dev and CI configurations.
[no-cd]
[private]
compose-lint folder="":
    ?[ {{ at_root }} = true ]
    tmp=$(mktemp -d); trap "rm -rf $tmp" EXIT; \
    {{ start_check(folder) }} docker compose --file docker/docker-compose.yml --file docker/docker-compose.override.yml config --no-interpolate > $tmp/dev.yml && \
    docker compose --file docker/docker-compose.yml --file docker/docker-compose.ci.yml config --no-interpolate > $tmp/ci.yml && \
    {{ project_wide_tools }} compose-lint --config docker/.compose-lint.yml --fail-on low --skip-suppressed docker/docker-compose.yml $tmp/dev.yml $tmp/ci.yml {{ end_check }}

# Check the justfile for correct formatting.
[private]
check-justfile folder="":
    ?[ {{ at_root }} = true ]
    {{ start_check(folder) }} {{ just_fmt }} --check --color=$_color {{ end_check }}

# Run helm lint
[no-cd]
[private]
helm-lint folder="":
    ?[ {{ at_root }} = true ]
    ?[ `which helm` ]
    {{ start_check(folder) }} helm lint --quiet --strict helm/ {{ end_check }}

# Run Python checks.
[no-cd]
[parallel]
[private]
check-py folder="": (ty folder) (mypy folder) (fixit folder) (ruff folder) (pyproject-fmt folder) (troml folder) (pip-audit folder) (uv-audit folder) (bandit folder) (vulture folder) (vale folder)

# Run npm lint to check JavaScript code.
[no-cd]
[private]
npm-lint folder="": install-js-dependencies
    ?[ {{ package_json_exists }} = true ]
    {{ start_check(folder) }} {{ npm_run }} lint --if-present {{ end_check }}

# Run npm audit to check JavaScript dependencies for known security vulnerabilities..
[no-cd]
[private]
npm-audit folder="": install-js-dependencies
    ?[ {{ package_json_exists }} = true ]
    {{ start_check(folder) }} npm audit {{ end_check }}

# Run npm outdated to check for outdated JavaScript dependencies. Ignore outdated packages that can't be updated (current == wanted).
[no-cd]
[private]
npm-outdated folder="": install-js-dependencies
    ?[ {{ package_json_exists }} = true ]
    {{ start_check(folder) }} npm outdated --json | uv run python -c "import json, sys; updates = [f'{k}: {v['current']} -> {v['wanted']}' for k, v in json.loads(sys.stdin.read()).items() if v['wanted'] != v['current']]; print('\n'.join(updates), end='\n' if updates else ''); sys.exit(1 if updates else 0)" {{ end_check }}

# Run JavaScript checks.
[no-cd]
[parallel]
[private]
check-js folder="": (npm-lint folder) (npm-audit folder) (npm-outdated folder)

# Run the quality checks, in the current working directory. Project-wide checks only run when invoked from the repo root.
[no-cd]
[private]
_check folder="": (check-js folder) (check-py folder) (check-justfile folder) (yamllint folder) (zizmor folder) (compose-lint folder) (helm-lint folder)

# Run `_check` for one folder. `cd folder` is a no-op when `folder` is `.`.
[no-cd]
[private]
check-folder folder:
    cd {{ folder }} && just _check {{ folder }}

# Run the quality checks. Without args, runs in the current working directory; with folder arguments, runs in those folders (in parallel); with --all/-a, runs in all relevant folders. Project-wide checks (yamllint, zizmor, compose-lint, check-justfile) only run from the repo root.
[arg("scope", long="all", short="a", value="all", help="Run checks in all relevant folders")]
[no-cd]
check scope="" *folders:
    {{ if scope == "all" { "just check-all" } else if folders == "" { "just _check" } else { "echo " + folders + " | xargs --max-args=1 --max-procs=0 just check-folder" } }}

# Run the quality checks, in all relevant folders.
[parallel]
[private]
check-all: (check-folder "components/api_server") (check-folder "components/collector") (check-folder "components/frontend") (check-folder "components/notifier") (check-folder "components/renderer") (check-folder "components/shared_code") (check-folder "docs") (check-folder "tests/application_tests") (check-folder "tests/feature_tests") (check-folder "tools/release") (check-folder "tools/third_party") (check-folder "tools/update_dependencies") (check-folder ".")

# === Fix issues ===

# Fix Python quality issues that can be fixed automatically, in the current working directory.
[no-cd]
[private]
fix-py: install-py-dependencies
    ?[ {{ pyproject_toml_exists }} = true ]
    {{ ty }} --fix {{ code }}
    {{ ruff }} format {{ code }}
    {{ ruff }} check --fix {{ code }}
    {{ fixit }} fix {{ code }}
    # Pyproject-fmt returns exit code 1 when pyproject.toml needs formatting, ignore it when formatting:
    {{ pyproject_fmt }} --no-print-diff pyproject.toml || true
    {{ troml }} suggest --fix
    # Vulture returns exit code 3 when there is dead code, ignore it when writing the whitelist:
    {{ vulture }} --make-whitelist {{ code }} > {{ vulture_whitelist }} || true

# Fix zizmor issues that can be fixed automatically.
[no-cd]
[private]
fix-zizmor:
    ?[ {{ at_root }} = true ]
    {{ project_wide_tools }} zizmor --no-progress --quiet --fix=all .github/workflows

# Fix JavaScript quality issues that can be fixed automatically, in the current working directory.
[no-cd]
[private]
fix-js: install-js-dependencies
    ?[ {{ has_js_script("fix") }} = true ]
    {{ npm_run }} fix

# Fix quality issues that can be fixed automatically, in the current working directory and the root folder.
[no-cd]
[parallel]
fix: fix-py fix-js fix-zizmor
    {{ just_fmt }}

# === Release ===

# Release Quality-time. Run `just release-help` for more information.
[working-directory('tools/release')]
release *args:
    {{ uv_run }} --script src/release.py {{ args }}

[private]
[working-directory('tools/release')]
release-help:
    {{ uv_run }} --script src/release.py --help

# === CI/CD ===

# Run all tests and checks in CI. Meant for running tests and checks in GitHub Actions and CircleCI.
[no-cd]
[parallel]
[private]
ci $CI="true": (test "yes") check junit-xml

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

# === Utility recipes ===

# Run the recipe in the folder.
[private]
run recipe folder:
    cd {{ folder }} && just {{ recipe }}
